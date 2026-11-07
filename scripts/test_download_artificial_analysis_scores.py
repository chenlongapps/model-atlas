import contextlib
import gzip
import hashlib
import io
import json
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

import download_artificial_analysis_scores as downloader


class OutputTests(unittest.TestCase):
    def test_default_directory_is_project_temp_not_cwd(self):
        with patch.object(Path, "cwd", return_value=Path("/unrelated")):
            output = downloader.resolve_output_file(None)
        self.assertEqual(output.parent, Path(downloader.__file__).resolve().parent.parent / "temp")
        self.assertRegex(output.name, r"^artificial-analysis-models-\d{4}-\d{2}-\d{2}\.toml$")

    def test_explicit_file_and_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.assertEqual(downloader.resolve_output_file(str(root / "scores.toml")), root / "scores.toml")
            self.assertEqual(downloader.resolve_output_file(str(root)).parent, root)
            self.assertEqual(downloader.resolve_output_file(str(root / "new")).parent, root / "new")
            # 已有目录即使含有扩展名，也按目录处理。
            dotted = root / "snapshots.local"
            dotted.mkdir()
            self.assertEqual(downloader.resolve_output_file(str(dotted)).parent, dotted)

    def test_collision_and_force(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "nested" / "scores.toml"
            self.assertEqual(downloader.save_output(target, b"first", False), target)
            second = downloader.save_output(target, b"second", False)
            self.assertEqual(second.name, "scores-2.toml")
            third = downloader.save_output(target, b"third", False)
            self.assertEqual(third.name, "scores-3.toml")
            self.assertEqual(target.read_bytes(), b"first")
            self.assertEqual(downloader.save_output(target, b"forced", True), target)
            self.assertEqual(target.read_bytes(), b"forced")
            self.assertEqual(second.read_bytes(), b"second")


class DatasetTests(unittest.TestCase):
    def test_manifest_unescape_and_deduplicate(self):
        key = "ab" * 32
        entry = json.dumps({"manifest": {"path": "/data.bin", "key": key.upper()}})
        html = json.dumps(entry) + entry
        self.assertEqual(downloader.find_manifest_entries(html), [("/data.bin", key)])

    def test_missing_manifest(self):
        with self.assertRaisesRegex(ValueError, "没有找到数据清单"):
            downloader.find_manifest_entries("<html></html>")

    def test_dataset_score(self):
        model = {
            "deprecated": False,
            "price1mInputTokens": None,
            "price1mOutputTokens": None,
            "headline": None,
        }
        self.assertEqual(downloader.dataset_score({"models": [model]}), 1)
        self.assertEqual(downloader.dataset_score({"models": []}), -1)
        self.assertEqual(downloader.dataset_score({"models": [{"name": "Incomplete"}]}), -1)

    @unittest.skipIf(downloader.tomli_w is None, "需要 tomli-w")
    def test_sort_missing_values_and_precision(self):
        cost = 1.4120973060945472
        data = {"models": [
            {"name": "Missing"},
            {"name": "Older", "releaseDate": "2025-01-01", "intelligenceIndex": 0,
             "intelligenceIndexCostPerTask": {"cost": {"total": 0}}},
            {"name": "Newer", "releaseDate": "2026-01-01", "intelligenceIndex": 42.123456789,
             "intelligenceIndexCostPerTask": {"cost": {"total": cost}}},
        ]}
        result = tomllib.loads(downloader.serialize_toml(downloader.simplify_dataset(data)).decode())
        models = result["models"]
        self.assertEqual([m["name"] for m in models], ["Newer", "Older", "Missing"])
        self.assertEqual(models[0]["cost"], cost)
        self.assertEqual(models[0]["intelligenceIndex"], 42.123456789)
        self.assertEqual(models[1]["cost"], 0)
        self.assertEqual(models[1]["intelligenceIndex"], 0)
        self.assertEqual(models[2], {"name": "Missing"})


@unittest.skipIf(downloader.AESGCM is None, "需要 cryptography")
class DecryptTests(unittest.TestCase):
    def setUp(self):
        self.key = bytes(range(32))
        self.raw = b'{"models": []}'
        iv = hashlib.sha256(self.key).digest()[:12]
        self.encrypted = downloader.AESGCM(self.key).encrypt(iv, gzip.compress(self.raw), None)

    def test_decrypt(self):
        self.assertEqual(downloader.decrypt_manifest(self.encrypted, self.key.hex()), self.raw)

    def test_tampered_data(self):
        tampered = self.encrypted[:-1] + bytes([self.encrypted[-1] ^ 1])
        with self.assertRaisesRegex(ValueError, "认证失败"):
            downloader.decrypt_manifest(tampered, self.key.hex())

    def test_decompression_limit(self):
        with patch.object(downloader, "MAX_DECOMPRESSED_MANIFEST_BYTES", 4):
            with self.assertRaisesRegex(ValueError, "解压后数据超过"):
                downloader.decrypt_manifest(self.encrypted, self.key.hex())


@unittest.skipIf(downloader.AESGCM is None or downloader.tomli_w is None, "需要下载工具依赖")
class MainTests(unittest.TestCase):
    def test_offline_download_to_default_directory(self):
        key = bytes(range(32))
        data = {"models": [{
            "name": "Fixture", "releaseDate": "2026-01-01", "intelligenceIndex": 42.5,
            "intelligenceIndexCostPerTask": {"cost": {"total": 0.123456789}},
            "deprecated": False, "price1mInputTokens": None,
            "price1mOutputTokens": None, "headline": None,
        }]}
        page = json.dumps({"manifest": {"path": "/fixture.bin", "key": key.hex()}}).encode()
        iv = hashlib.sha256(key).digest()[:12]
        encrypted = downloader.AESGCM(key).encrypt(iv, gzip.compress(json.dumps(data).encode()), None)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "temp"
            with (
                patch.object(downloader, "DEFAULT_OUTPUT_DIR", target),
                patch.object(downloader.sys, "argv", ["download_artificial_analysis_scores.py"]),
                patch.object(downloader, "fetch_buffer", side_effect=[page, encrypted]) as fetch,
                contextlib.redirect_stdout(io.StringIO()),
            ):
                downloader.main()
            files = list(target.glob("*.toml"))
            self.assertEqual(len(files), 1)
            models = tomllib.loads(files[0].read_text(encoding="utf-8"))["models"]
            self.assertEqual(models[0]["name"], "Fixture")
            self.assertEqual(models[0]["cost"], 0.123456789)
            self.assertEqual(fetch.call_args_list[1].args[0], "https://artificialanalysis.ai/fixture.bin")


if __name__ == "__main__":
    unittest.main()
