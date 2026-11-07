# ModelAtlas 工作区

ModelAtlas 的统一开发入口。根仓库管理公共工具、资源和说明，通过 Git 子模块关联三个独立项目；根仓库只记录子项目的地址和指定提交，不复制子仓库的提交历史。

根仓库计划以私有仓库维护。GitHub 上的可见性需在创建远端时设置，本地 Git 配置不会自动将远端设为私有；三个子仓库的可见性和访问权限独立管理。私有仓库也不要提交密码、Token 或其他凭据。

## 目录与职责

| 路径 | 用途 | 管理方式 |
| --- | --- | --- |
| `model-atlas-android/` | Android 应用 | [独立子仓库](https://github.com/chenlongapps/model-atlas-android) |
| `model-atlas-data/` | 模型资料、Benchmark 成绩及数据构建 | [独立子仓库](https://github.com/chenlongapps/model-atlas-data) |
| `model-atlas-logo/` | 应用图标、品牌标志及设计参考 | [独立子仓库](https://github.com/chenlongapps/model-atlas-logo) |
| `scripts/` | 工作区公共工具 | 根仓库，见 [工具说明](scripts/README.md) |
| `res/` | 实验室与服务商 Logo 资源 | 根仓库，见 [资源说明](res/README.md) |
| `prompts/` | 可复用提示词（如有） | 根仓库；空目录不会被 Git 跟踪 |
| `temp/` | 本地快照及临时产物 | 忽略，不提交 |

进入子项目后遵循其自身的 README 和 AGENTS.md。根目录的 `res/` 是实验室与服务商资源，`model-atlas-logo/` 是 ModelAtlas 自身品牌素材，两者职责不同。

## 克隆完整工作区

根仓库发布后，将下面的地址占位符替换为实际远端地址。访问私有根仓库需要对应 GitHub 权限和认证；访问子仓库仍需分别满足它们的权限要求。

```sh
git clone --recurse-submodules "<根仓库地址>" model-atlas
cd model-atlas
git submodule status
```

如果已经克隆根仓库但没有下载子模块，在根目录执行：

```sh
git submodule update --init --recursive
```

子模块默认检出根仓库记录的精确提交，可能处于 detached HEAD，这是正常状态；开始开发前先切换或创建分支。

## 更新整个工作区

先确认根仓库和各子模块没有未保存的修改，再在根目录执行：

```sh
git pull --ff-only
git submodule sync --recursive
git submodule update --init --recursive
```

这会检出根仓库记录的子模块版本，**不是**自动跟踪各子仓库的最新 `main`。有本地开发中的提交或改动时，先提交并推送，避免意外离开当前开发版本；不要为了更新工作区强制覆盖本地修改。

## 修改并发布子项目

以 Android 为例，先在子仓库中选择开发分支，再按该项目规范修改、验证、提交并推送：

```sh
cd model-atlas-android
git switch main
git pull --ff-only
# 修改并验证后，按实际范围暂存文件
git add <修改的文件路径>
git commit -m "描述 Android 项目的修改"
git push origin main
```

若需要功能分支，可在子仓库中使用 `git switch -c <分支名>`。子项目提交必须先推送到可访问的远端，再让根仓库引用它，避免其他人无法下载对应版本。

子仓库推送完成后，回到根目录提交新的版本指针：

```sh
cd ..
git diff --submodule=log
git add model-atlas-android
git commit -m "更新 Android 子模块版本"
git push origin main
```

数据和品牌素材项目同理。根仓库中的 `git add model-atlas-android` 只暂存子模块的提交指针，**不会**代替子仓库提交内部文件。

## 修改公共工具或资源

直接在根仓库提交对应文件，不需要修改子仓库：

```sh
git add README.md .gitignore scripts/ res/
git diff --cached --stat
git commit -m "更新工作区工具和资源"
git push origin main
```

根仓库的首次提交和远端发布需要另行完成；以上推送命令以已经配置 `origin` 为前提。优先按路径暂存文件，检查暂存区后再提交，避免同时带入无关的子模块版本变动。

## 常用检查

```sh
git status
git submodule status
git diff --submodule=log
git submodule foreach 'git status --short --branch'
```

`git submodule status` 的前缀中，空格表示与记录版本一致，`+` 表示当前检出版本与根仓库记录不同，`-` 表示尚未初始化，`U` 表示存在合并冲突。三个子模块目录不得加入根仓库的 `.gitignore`。
