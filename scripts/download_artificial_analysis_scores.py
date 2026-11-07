#!/usr/bin/env python3
"""下载 Artificial Analysis 模型名称、发布日期、综合分数和评测成本。

依赖：python3 -m pip install -r scripts/requirements.txt
默认将 TOML 文件保存到项目根目录的 temp/，不受当前工作目录影响。
输出字段：name、releaseDate、intelligenceIndex、cost。
按发布日期倒序排列，缺失日期的模型排在最后。
TOML 不支持 null；缺失字段会省略，但保留对应的模型记录。
cost 来自 intelligenceIndexCostPerTask.cost.total，口径为 USD/weighted task，
不做四舍五入。仅导出来源数值，不代表零成本已核实，也不自动导入模型成绩。
用法（在项目根目录运行）：
  python3 scripts/download_artificial_analysis_scores.py
  python3 scripts/download_artificial_analysis_scores.py --out ./scores.toml
  python3 scripts/download_artificial_analysis_scores.py --out ./downloads
  python3 scripts/download_artificial_analysis_scores.py --force
"""

import argparse
import gzip
import hashlib
import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

try:
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    AESGCM = None

try:
    import tomli_w
except ImportError:
    tomli_w = None


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "temp"
REQUIREMENTS_FILE = Path(__file__).resolve().parent / "requirements.txt"
SITE_URL = "https://artificialanalysis.ai/"
MODELS_PAGE_URL = urljoin(SITE_URL, "/models")
REQUEST_TIMEOUT = 30
MAX_MODELS_PAGE_BYTES = 4 * 1024 * 1024
MAX_ENCRYPTED_MANIFEST_BYTES = 16 * 1024 * 1024
MAX_DECOMPRESSED_MANIFEST_BYTES = 24 * 1024 * 1024
MANIFEST_PATTERN = re.compile(
    r'"manifest"\s*:\s*\{\s*"path"\s*:\s*"([^"]+)"\s*,\s*'
    r'"key"\s*:\s*"([0-9a-f]{64})"\s*\}',
    re.IGNORECASE,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="下载模型名称、发布日期、intelligenceIndex 分数和评测成本（USD/weighted task），输出 TOML"
    )
    parser.add_argument(
        "-o", "--out",
        help="输出 TOML 文件或目录，默认为项目根目录的 temp/；显式相对路径基于当前工作目录",
    )
    parser.add_argument("--pretty", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("-f", "--force", action="store_true", help="输出文件已存在时直接覆盖")
    return parser.parse_args()


def resolve_output_file(output):
    date = datetime.now(timezone.utc).date().isoformat()
    default_name = f"artificial-analysis-models-{date}.toml"
    if not output:
        return DEFAULT_OUTPUT_DIR / default_name

    target = Path(output).expanduser().resolve()
    is_directory = target.is_dir() if target.exists() else not target.suffix
    return target / default_name if is_directory else target


def fetch_buffer(url, maximum_bytes):
    request = Request(
        url,
        headers={
            "Accept": "*/*",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "User-Agent": "Mozilla/5.0 ArtificialAnalysisDataFetcher/1.0",
        },
    )
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            content_length = response.headers.get("Content-Length")
            if content_length:
                try:
                    size = int(content_length)
                except ValueError:
                    size = 0
                if size > maximum_bytes:
                    raise ValueError(f"响应超过大小限制 {maximum_bytes} 字节")

            data = response.read(maximum_bytes + 1)
            if len(data) > maximum_bytes:
                raise ValueError(f"响应超过大小限制 {maximum_bytes} 字节")
            return data
    except HTTPError as error:
        raise RuntimeError(f"请求 {url} 失败：HTTP {error.code}") from error


def find_manifest_entries(html):
    for _ in range(4):
        html = html.replace('\\"', '"')

    entries = []
    seen = set()
    for match in MANIFEST_PATTERN.finditer(html):
        entry = (match.group(1), match.group(2).lower())
        if entry not in seen:
            seen.add(entry)
            entries.append(entry)

    if not entries:
        raise ValueError("模型页面中没有找到数据清单；网站页面结构可能已经变化")
    return entries


def decrypt_manifest(encrypted, key_hex):
    if len(encrypted) <= 16:
        raise ValueError("加密清单长度异常")

    key = bytes.fromhex(key_hex)
    iv = hashlib.sha256(key).digest()[:12]
    try:
        compressed = AESGCM(key).decrypt(iv, encrypted, None)
    except InvalidTag as error:
        raise ValueError("AES-GCM 认证失败") from error

    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
        decompressed = stream.read(MAX_DECOMPRESSED_MANIFEST_BYTES + 1)
    if len(decompressed) > MAX_DECOMPRESSED_MANIFEST_BYTES:
        raise ValueError(f"解压后数据超过大小限制 {MAX_DECOMPRESSED_MANIFEST_BYTES} 字节")
    return decompressed


def dataset_score(data):
    if not isinstance(data, dict) or not isinstance(data.get("models"), list) or not data["models"]:
        return -1

    for model in data["models"]:
        if not isinstance(model, dict):
            return -1
        if type(model.get("deprecated")) is not bool:
            return -1
        if "price1mInputTokens" not in model or "price1mOutputTokens" not in model:
            return -1
        has_headline = isinstance(model.get("headline"), dict) or (
            "headline" in model and model["headline"] is None
        )
        if not has_headline and not isinstance(model.get("timescaleData"), dict):
            return -1
    return len(data["models"])


def simplify_dataset(data):
    models = []
    for model in data["models"]:
        per_task = model.get("intelligenceIndexCostPerTask")
        cost = per_task.get("cost") if isinstance(per_task, dict) else None
        models.append({
            "name": model.get("name"),
            "releaseDate": model.get("releaseDate"),
            "intelligenceIndex": model.get("intelligenceIndex"),
            "cost": cost.get("total") if isinstance(cost, dict) else None,
        })
    models.sort(key=lambda model: model["releaseDate"] or "", reverse=True)
    return {"models": models}


def serialize_toml(data):
    # TOML 无 null 类型，省略缺失字段，而不是将它们转换为 0 或字符串。
    models = [
        {key: value for key, value in model.items() if value is not None}
        for model in data["models"]
    ]
    return tomli_w.dumps({"models": models}).encode("utf-8")


def save_output(path, output, force):
    path.parent.mkdir(parents=True, exist_ok=True)
    if force:
        path.write_bytes(output)
        return path

    # 独占创建文件，避免并发运行时覆盖已有数据。
    candidate = path
    index = 2
    while True:
        try:
            with candidate.open("xb") as file:
                file.write(output)
            return candidate
        except FileExistsError:
            candidate = path.with_name(f"{path.stem}-{index}{path.suffix}")
            index += 1


def main():
    options = parse_args()
    if AESGCM is None or tomli_w is None:
        raise RuntimeError(
            f'缺少依赖，请运行：python3 -m pip install -r "{REQUIREMENTS_FILE}"'
        )

    print("[ArtificialAnalysis] 正在读取模型页面…")
    models_page = fetch_buffer(MODELS_PAGE_URL, MAX_MODELS_PAGE_BYTES)
    entries = find_manifest_entries(models_page.decode("utf-8", errors="replace"))
    print(f"[ArtificialAnalysis] 找到 {len(entries)} 个加密清单")

    best = None
    for path, key in entries:
        manifest_url = urljoin(SITE_URL, path)
        try:
            encrypted = fetch_buffer(manifest_url, MAX_ENCRYPTED_MANIFEST_BYTES)
            raw = decrypt_manifest(encrypted, key)
            data = json.loads(raw.decode("utf-8"))
            score = dataset_score(data)
            if score < 0:
                print(f"[ArtificialAnalysis] 跳过 {path}：不是包含完整模型字段的主数据集")
                continue
            print(f"[ArtificialAnalysis] 候选 {path}：{score} 个模型")
            if best is None or score > best["score"]:
                best = {"data": data, "url": manifest_url, "score": score}
        except Exception as error:
            print(f"[ArtificialAnalysis] 跳过 {path}：{str(error) or type(error).__name__}", file=sys.stderr)

    if best is None:
        raise RuntimeError("没有找到包含完整模型字段的主数据集")

    simplified = simplify_dataset(best["data"])
    output = serialize_toml(simplified)
    output_file = save_output(resolve_output_file(options.out), output, options.force)

    models = simplified["models"]
    models_with_scores = sum(
        isinstance(model.get("intelligenceIndex"), (int, float))
        and not isinstance(model.get("intelligenceIndex"), bool)
        for model in models
    )
    digest = hashlib.sha256(output).hexdigest()
    print(f"[ArtificialAnalysis] 已保存 {len(models)} 个模型 → {output_file}")
    print(f"[ArtificialAnalysis] 其中包含 intelligenceIndex 分数：{models_with_scores} 个")
    print("[ArtificialAnalysis] cost 口径：USD/weighted task；来源零值未经核实，不自动导入成绩")
    print(f"[ArtificialAnalysis] 数据清单：{best['url']}")
    print(f"[ArtificialAnalysis] 文件大小：{len(output)} 字节")
    print(f"[ArtificialAnalysis] SHA-256：{digest}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"[ArtificialAnalysis] 下载失败：{str(error) or type(error).__name__}", file=sys.stderr)
        sys.exit(1)
