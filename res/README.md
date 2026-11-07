# Logo 资源说明

Model Atlas 使用的全部 SVG logo 资产，来源为 [models.dev](https://models.dev) 的 Logos 服务，按用途分为三个目录，另附一个占位兜底图。

| 目录 / 文件 | 数量 | 远端地址 | 说明 |
|---|---|---|---|
| `provider-logo/{provider}.svg` | 221 | `https://models.dev/logos/{provider}.svg` | 按 provider ID 命名的服务商 logo |
| `lab-logo/{lab}.svg` | 23 | `https://models.dev/logos/labs/{lab}.svg` | 按实验室/厂商母品牌命名的 logo |
| `lab-logo-color/{lab}.svg` | 23 | —（本地资产） | `lab-logo` 同图文件的彩色变体 |
| `fallback-default.svg` | 1 | —（无独立 URL） | models.dev 兜底图，见下文 |

## 来源与取用规则

models.dev 以静态文件形式托管 logo，`{provider}` / `{lab}` 即 models.dev 上的 ID（文件名去掉 `.svg`）：

```bash
# provider logo
curl https://models.dev/logos/anthropic.svg

# lab logo
curl https://models.dev/logos/labs/anthropic.svg
```

响应为 `content-type: image/svg+xml`。

## ⚠️ Catch-all 陷阱（重要）

`/logos/*.svg` 是 **catch-all 路由**：请求任何不存在的名字也返回 **HTTP 200**，内容是一个固定的兜底 SVG（1421 字节）。因此：

- **不能靠 HTTP 状态码判断 logo 是否存在**，一切校验必须比对文件内容；
- 本地 `fallback-default.svg` 与该兜底返回值**字节完全一致**（md5 `f14bc05b…`），可作为「远端无此 logo」的判定参照——客户端拿到远端 SVG 后与其比 md5（或比 path 图形数据）即可识别兜底图。

## 三个目录的区别

### `provider-logo/` — 服务商 logo

按 models.dev provider ID 命名。其中 **212/221 为单色（`currentColor`）**，适合用 CSS 控制颜色、适配明暗主题；其余 9 个（`302ai`、`atomic-chat`、`hpc-ai`、`novita-ai`、`orcarouter`、`regolo-ai`、`wafer.ai`、`zeldoc`、`zenmux`）为固定填充色，取用后不要再改色。

命名包含 models.dev 的渠道/区域变体后缀，例如 `-cn`（国内站）、`-coding-plan` / `-token-plan` / `-step-plan`（套餐），与远端 ID 一一对应。

### `lab-logo/` — 实验室 logo

23 个模型实验室/厂商母品牌 logo，**全部为单色 `currentColor`**。与 `provider-logo` 中的同名文件（如 `anthropic.svg`）图形相同，区别在于：`lab-logo` 表示「这是哪家实验室」，`provider-logo` 表示「通过哪个服务商访问」。

### `lab-logo-color/` — 彩色变体（本地资产）

models.dev **只提供单色版 lab logo**，没有彩色版。本目录是本地对 `lab-logo` 同图文件的着色变体，图形（path 数据）一致、仅配色不同，共 23 个：

- 16 个纯色 `fill`（`vivgrid` 为 fill + stroke 同色）；
- 6 个渐变（`google`、`meta`、`minimax`、`mistral`、`stepfun`、`vispark`）；
- 1 个纯描边（`perplexity`）。

注意：彩色版**不使用 `currentColor`**，即不随主题变色，适合需要展示品牌原色的场景。

## 已知特殊条目

| 文件 | 情况 |
|---|---|
| `lab-logo/{ai21, inception, stepfun, thinkingmachines, vivgrid}.svg` | `/logos/labs/{name}.svg` 在 models.dev 上不存在（返回兜底图），实际托管在 `/logos/{name}.svg`（与 provider 同地址） |
| `provider-logo/arcee-ai.svg` | 图形来源于 `/logos/arcee.svg`；`/logos/arcee-ai.svg` 本身不存在 |
| `provider-logo/tencent.svg` | models.dev 无 `/logos/tencent.svg`；本地文件与 `tencent-tokenhub` / `tencent-token-plan` 同图 |
| `fallback-default.svg` | 无独立 URL，与 `/logos/{任意不存在名称}.svg` 的 catch-all 返回值字节一致 |

## 使用方式

```html
<!-- 直接引用 -->
<img src="res/provider-logo/openai.svg" alt="OpenAI" />

<!-- 单色 logo 推荐：用 currentColor 适配文字色 -->
<style>
  .logo {
    background-color: currentColor;
    -webkit-mask: url("res/lab-logo/anthropic.svg") center / contain no-repeat;
            mask: url("res/lab-logo/anthropic.svg") center / contain no-repeat;
  }
</style>
```

## 注意事项

- **viewBox 不统一**：`provider-logo` 中常见 `0 0 24 24`（64 个）、`0 0 40 40`（61 个），还有 `32×32`、`512×512`、`1024×1024` 及各种非方形画布。不要假设尺寸，用 `<img>` 或 `mask` + `contain` 缩放，不要写死 width/height。
- 各文件均通过 XML 合法性校验，可直接被浏览器/XML 解析器处理。
- 目录中的 `.DS_Store` 是 macOS 元数据，非 logo 文件，建议删除。

## 验证

`verify-logos.py`（位于仓库根目录）会逐个请求 models.dev 比对本地文件（先比 MD5，不一致再比 path 图形数据），并生成 `res/LOGO-MAPPING.md` 完整对照表。可重复执行：

```bash
python3 verify-logos.py
```
