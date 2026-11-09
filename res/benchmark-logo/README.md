# Benchmark Logo 资源

覆盖 11 项 benchmark，提供 12 个 SVG。资源来自官方站点或官方仓库，其中 3 个 SVG 从官方 PNG 描摹为矢量路径；原始 PNG 保存在 `originals/` 供追溯。全部 SVG 均不嵌入位图。

部分 benchmark 的页面使用主办方标识或站点 favicon，对应类型及具体来源见下表。文件按 benchmark 名称命名，不包含版本号；图片不代表某一版本的成绩或协议。

| Benchmark | 本地文件 | 类型 | 官方页面 / 图片来源 |
|---|---|---|---|
| Artificial Analysis Intelligence Index | [artificial-analysis-intelligence-index.svg](artificial-analysis-intelligence-index.svg) | 主办方 Logo | [页面](https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index) · [资源](https://artificialanalysis.ai/img/logo-icon.svg) |
| AutomationBench | [automationbench.svg](automationbench.svg) | 主办方 Logo | [页面](https://zapier.com/benchmarks) · [资源](https://zapier.com/) |
| Chartography | [chartography.svg](chartography.svg) | 主办方 Logo | [页面](https://surgehq.ai/benchmarks/chartography) · [资源](https://cdn.prod.website-files.com/68dc970bd6e945ea3fb0f426/68e340b3dfa20e2c97749a3a_Logo.svg) |
| DeepSWE | [deepswe.svg](deepswe.svg) | 官网图标 | [页面](https://deepswe.datacurve.ai/) · [资源](https://deepswe.datacurve.ai/favicon.svg) |
| GDPval-AA | [gdpval-aa.svg](gdpval-aa.svg) | 主办方 Logo | [页面](https://artificialanalysis.ai/evaluations/gdpval-aa) · [资源](https://artificialanalysis.ai/img/logo-icon.svg) |
| Humanity's Last Exam | [humanitys-last-exam.svg](humanitys-last-exam.svg) | 独立 Logo | [页面](https://lastexam.ai/) · [资源](https://lastexam.ai/_next/static/media/hle_logo.42325f6d.svg) |
| OSWorld | [osworld.svg](osworld.svg) | 官网图标 | [页面](https://osworld-v2.xlang.ai/) · [资源](https://osworld-v2.xlang.ai/static/images/favicon.png) |
| SWE-bench Pro | [swe-bench-pro.svg](swe-bench-pro.svg) | 主办方 Logo | [页面](https://labs.scale.com/leaderboard/swe_bench_pro_public_v2) · [资源](https://labs.scale.com/images/logo-scale-labs.svg?v=2) |
| Terminal-Bench-Science | [terminal-bench-science.svg](terminal-bench-science.svg) | 官网图标 | [页面](https://terminal-bench-science.ai/) · [资源](https://terminal-bench-science.ai/favicon.svg?v=7) |
| Terminal-Bench | [terminal-bench.svg](terminal-bench.svg) | 官网图标 | [页面](https://www.tbench.ai/) · [资源](https://www.tbench.ai/fav.png) |
| Vals Index | [vals-index.svg](vals-index.svg) | 主办方 Logo | [页面](https://www.vals.ai/benchmarks/vals_index) · [资源](https://www.vals.ai/Logos/vals-full.svg) |

## 说明

- **Artificial Analysis Intelligence Index**：Artificial Analysis 官方图标；与 GDPval-AA 共用。
- **AutomationBench**：评测页未找到独立 Logo；从 Zapier 官网页头 aria-label="Zapier" 的链接内提取 SVG，保留原始图形与配色。
- **Chartography**：评测页页头使用的 Surge AI 官方字标。
- **DeepSWE**：DeepSWE 官网 favicon，图形为 Datacurve 标识。
- **GDPval-AA**：Artificial Analysis 官方图标；与 Intelligence Index 共用。
- **Humanity's Last Exam**：HLE 官网原始版本 Logo，非 HLE-Diamond。
- **OSWorld**：OSWorld 2.0 项目站点 favicon 的矢量化 SVG，200×200，透明背景。
- **SWE-bench Pro**：官方排行榜页头使用的 Scale Labs 字标。
- **Terminal-Bench-Science**：独立官网 SVG favicon；另附从官方仓库 PNG 矢量化的完整 Logo SVG。
- **Terminal-Bench**：官网图标的矢量化 SVG，512×512，保留黑底白色符号。
- **Vals Index**：Vals Index 官方页面页头的 Vals AI 字标。

Terminal-Bench-Science 完整字标：

- [terminal-bench-science-logo.svg](terminal-bench-science-logo.svg)（浅色背景用，2449×468，透明背景，路径 SVG）。
- [官方仓库图片来源](https://raw.githubusercontent.com/harbor-framework/terminal-bench-science/main/assets/tb-science-logo-light-bold.png)。

## 使用与核验

- 保留了原始画布尺寸与主色；SVG 的 `viewBox`、宽高比各不相同，显示时按比例缩放。
- `osworld.svg`、`terminal-bench.svg`、`terminal-bench-science-logo.svg` 为本地矢量化版本，使用 VTracer 描摹路径，轮廓近似原图；它们并非官方直接发布的 SVG。OSWorld 图标适合浅色背景。
- 3 张官方原始 PNG 存于 [originals/](originals/)，其哈希与矢量化参数记录在清单中。
- 来源、提取方式和每个图片的 SHA-256 记录于 [sources.json](sources.json)。
- 已检查全部 SVG 的 XML、`viewBox`，确认无 `<image>`、脚本或外部资源依赖；3 个转换文件已用 resvg 渲染，并在浅色、深色背景上与原始 PNG 比对。

收集日期：2026-11-09。
