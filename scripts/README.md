# 项目工具

## 下载 Artificial Analysis 快照

需要 Python 3.11+。在项目根目录运行：

```sh
python3 -m pip install -r scripts/requirements.txt
python3 scripts/download_artificial_analysis_scores.py
```

默认输出为项目根目录下的 `temp/artificial-analysis-models-YYYY-MM-DD.toml`（UTC 日期），从其他目录运行脚本也不改变默认输出位置。`temp/` 是本地快照目录，不提交 Git。

```sh
# 显式相对路径以当前工作目录为准；也可以指定目录
python3 scripts/download_artificial_analysis_scores.py --out ./temp/scores.toml
python3 scripts/download_artificial_analysis_scores.py --out ./temp

# 同名文件存在时默认添加 -2、-3 等后缀；仅 --force 覆盖
python3 scripts/download_artificial_analysis_scores.py --force
```

TOML 包含 `[[models]]`，保留 `name`、`releaseDate`、`intelligenceIndex`、`cost` 四个字段，按发布日期倒序排列，缺失日期排在最后。缺失字段省略，不补零，不过滤无成绩的模型，不主动四舍五入数值。

`cost` 取自 `intelligenceIndexCostPerTask.cost.total`，口径为 **USD/weighted task**，不是 token 单价或整次评测总成本。导出仅保留来源值，不能据此确认零值代表真实零费用；下载日期也不是成绩日期。脚本仅下载快照，不自动修改 `model-atlas-data/`。网站结构变化可能导致下载失败；本工具不保证数据来源真实性或赋予数据公开再分发授权。

离线测试（不访问网站）：

```sh
python3 -B -m unittest discover -s scripts -p 'test_*.py' -v
```
