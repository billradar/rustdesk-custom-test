# RustDesk Custom TEST / DEVELOPMENT

**测试用途，非生产仓库。** 只维护补丁、脚本与自动维护 workflow；不保存完整 upstream 源码。第三阶段允许在本测试仓库创建明确标记的 Prerelease，不创建生产 Release。

Standard = 官方 RustDesk + Common。
SOS = 同一官方 SHA + Common + SOS。

## 固定历史基线

第一阶段已成功复现官方 [`005a8b4a04fd906c707eefd69c4898aa2c696202`](https://github.com/rustdesk/rustdesk/commit/005a8b4a04fd906c707eefd69c4898aa2c696202)，即正式 tag `1.4.9` 后第 2 个官方提交。不是把 `1.4.9` tag 的 SHA 改名；tag 本身为 `6c578292e8ebbbec708b76986ba8c4bc7c509747`。

- 旧 Standard：`7bf94bf7296c054a34828ea5d8958e18395ab3e6`，parent 就是选定基线。
- 旧 SOS：`54ab5a78a45f3d0f1d7d5257bfe18f4095cb9121`，parent `e2149974ccda5a063a2647bdd10d70da850b629b`。
- 选定基线保留两个旧版都有的官方 Windows 剪贴板修复；相对旧 SOS 只新增一个官方韩语翻译提交。
- `libs/hbb_common` 保留官方 gitlink，固定 `7e1c392c62d39c364127307cd408421dd5f8cfb0`；只改两行服务器默认配置，不 vendor 32 个文件，不使用 `submodule update --remote`。

旧仓库 `billradar/rustdesk` 与 `billradar/rustdesk-sos` 始终只读；测试不触发它们的 Actions。

## 补丁

| Patch | 目标 / 用途 |
|---|---|
| v1/common/0001-hbb-server-defaults.patch | 官方 hbb_common/src/config.rs：用编译参数替换 ID server、公钥常量；在 submodule 内 apply |
| v1/common/0002-client-defaults.patch | src/common.rs：API fallback；原有 hard password、verification-method、remote configuration 和 hide-cm 默认行为；可选 relay 默认值 |
| v1/common/0003-hide-cm-setting.patch | desktop_setting_page.dart：恢复旧 Standard 的 hide-cm 设置项 |
| v1/sos/0001-sos-mode.patch | 原有 BUILTIN sos-mode=Y；复用 Common 初始化，不重复服务器配置 |
| v1/sos/0002-sos-home.patch | connection_page.dart、desktop_home_page.dart：逐字保留旧 SOS 首页和提示隐藏 |
| v1/sos/0003-sos-settings.patch | desktop_setting_page.dart、desktop_tab_page.dart：逐字保留旧 SOS settings/图标限制 |

每个补丁先 `git apply --check` 再 apply；失败立即停止，不构建，不生成客户端 artifact。失败诊断会列出补丁及 Git 的冲突文件/hunk。UI SHA256 清单来源于两个旧仓库的上述固定提交，验证复现而非仅检查关键词。

## 配置与密码

编译所需参数：

| 参数 | 用途 |
|---|---|
| RUSTDESK_ID_SERVER | hbb_common 的 rendezvous 默认常量；不改变已有本地配置优先级 |
| RUSTDESK_KEY | base64 32-byte Ed25519 公钥 |
| RUSTDESK_API_SERVER | 保留旧版 fallback 层的位置；已有显式配置/推导行为仍优先 |
| RUSTDESK_PASSWORD | 原有 HARD_SETTINGS plaintext preset；不重新设计 salt/storage |
| RUSTDESK_RELAY_SERVER | 可选 DEFAULT_SETTINGS relay-server；空/不设置保持旧版 upstream discovery |

代码使用 Rust `env!` / `option_env!`，参数确实进入编译；无生成凭据文件、无 shell/sed 插值。未提供必需参数会失败。验证只显示 configured，不输出值或密码摘要。

**第一次 CI 仅使用 scripts/test-config.sh 的虚构 `.invalid` 域名、RFC 8032 测试公钥及明显测试密码。不要把真实值写进该文件。** 当前 workflow 不读取仓库 Variables/Secrets，以防误用生产配置。后续阶段才配置真实部署参数；地址/公钥可用 Variables，密码用 Secrets。

本阶段忠实保留旧版默认 `allow-remote-config-modification=Y`、`allow-hide-cm=Y`、`verification-method=use-permanent-password`；没有默默关闭。密码随二进制分发可被提取，旧明文 preset 机制只用于本阶段复现，后续单独做密码安全重构。已有本地永久密码的优先级沿用 upstream。不要把测试包当生产安全方案。

SOS 保留原有 **UI 隐藏**，不是 Level 3 主控功能禁用；CLI、deep link 等仍可能发起连接。没有加入 incoming-only、disable-settings 或服务器强制锁定。保留 upstream 被控后台代码。

## 手动 GitHub Actions

在测试仓库 Actions → **TEST - Standard and SOS Windows x64** → Run workflow。

- upstream_ref：解析一次并锁定 exact SHA。自动 stable 流程只接受官方非 draft、非 prerelease 的正式版本。不同版本是否兼容由严格检查决定，不承诺自动适配。
- variant：standard / sos / both，默认 both。
- test-build 支持 workflow_dispatch / workflow_call，权限 contents: read。开发分支兼容性工作流每日 UTC 03:23 检查 API 查询到的默认分支；stable 检测每日 UTC 05:41 / 17:41 运行，均支持手动触发。只有 release-check 的最终 prerelease job 有 contents: write。

Linux bridge job 按官方配方生成同一基线的桥接文件（Rust 1.75.0、Flutter 3.22.3、cargo-expand 1.0.95、flutter_rust_bridge_codegen 1.80.1）。Windows 两个独立 matrix jobs 使用 Windows 2022、Rust 1.75.0、Flutter 3.24.5、LLVM 15.0.6、vcpkg `120deac3062162151622ca4860575a33844ba10b`；取相应 upstream 官方构建步骤，调用该 SHA 的 `build.py --portable --flutter --skip-portable-pack --hwcodec --vram`。

没有永久复制官方大 workflow。第三方 Actions 使用官方配方已有完整 SHA pin。Flutter 自定义 engine 的下载地址仍为官方 `main` Release，下载哈希写在日志；此历史依赖仍可能变化，暂不能保证多年后字节一致重建。

每个客户端 artifact 名为 `rustdesk-<upstream version 或 source-SHA>-<standard|sos>-test-windows-x86_64`，内含可解压运行的完整 Flutter Release 目录、WindowInjection.dll、build-info.json、SHA256SUMS、许可证及补丁。不是已签名 MSI/自解压安装包；不包含旧 workflow 额外下载的打印机驱动或 usbmmidd 驱动，因此打印/虚拟显示驱动安装功能未宣称等价。这些打包扩展后续再按需要验收。

## 本地使用

仅首个平台 Windows x64（Git Bash、Python3、MSVC、Rust/Flutter/native 依赖按上述 workflow 安装）。先用同基线官方配方生成桥接文件和 bridge-info.json，准备官方 WindowInjection.dll、自定义 Flutter engine、SDK dropdown patch 和 vcpkg 依赖，然后：

```bash
source scripts/test-config.sh
export RUSTDESK_BRIDGE_DIR='C:/path/to/generated-bridge'
export RUSTDESK_TOPMOST_DLL='C:/path/to/WindowInjection.dll'
bash scripts/build-standard.sh
bash scripts/build-sos.sh
```

每次创建新的 `.work/<variant>.*` 临时源码树，prepare 验证官方 SHA/submodule/clean tree，apply 后验证配置和旧 UI，再构建。Standard/SOS 不复用带补丁的工作树。prepare 对已有非空目录拒绝操作，不 reset/delete；重新运行构建会使用新目录。客户端 artifact 已存在时拒绝覆盖，请先自行移动旧输出以保留证据。

仅验证补丁可在 Linux/macOS 做（不等于完整 Windows 构建）：

```bash
source scripts/test-config.sh
bash scripts/prepare.sh 005a8b4a04fd906c707eefd69c4898aa2c696202 .work/manual-standard
bash scripts/apply-patches.sh .work/manual-standard standard
python3 scripts/verify-source.py .work/manual-standard standard
```

verify-source 用实际 patched helper/常量编译独立 Rust 测试，验证编译参数进入设置、重复初始化行为及变体；它用内存 mock settings maps，不代替完整 upstream Config/密码认证/真实被控会话。`--static-only` 明确标记 native compilation NOT_RUN。

## 证据与限制

build-info 记录 upstream SHA/ref、hbb SHA、custom repo SHA、patch hashes、变体、平台、构建时间及 workflow run，不记录配置值/密码。必须以新仓库两个 build jobs 成功和实际 artifact 为完整构建成功证据；旧仓库成功、YAML 解析或 apply 成功都不算。

第三阶段实现开发分支兼容性检查、stable 检测和测试 Prerelease。继续暂缓 password V2、正式仓库、生产配置、正式 Release 和多平台矩阵。真实服务器的被控会话和交互 UI 验收尚需可授权的测试环境；虚构域名只用于构建复现，不会提供可用远程连接。

源码许可沿用 upstream AGPL-3.0；通过 manifest 精确 SHA + 本仓库补丁可以恢复对应源码，官方 URL 固定为 https://github.com/rustdesk/rustdesk 。

## 第三阶段自动维护

项目状态必须准确记录：**Build Reproduction: PASS；Runtime/UI Validation: SKIPPED BY USER；Real Remote Session Validation: NOT TESTED。** 第一阶段证据与第三阶段待执行项见 [stage3-status](docs/stage3-status.md)。编译成功不等于 UI/真实远控验收成功。

- `upstream-compatibility.yml` 查询 upstream default_branch，锁定 SHA，只执行 test-build 的 validation_only 路径；没有 Release job、写权限或 Windows 客户端构建。
- `release-check.yml` 依据官方 Release 的 draft/prerelease 标志及数字版本选 stable。解析 exact tag → SHA；同一个 SHA 传给两个独立构建树。
- `test-build.yml` 在 Windows/vcpkg 开始前执行 strict patch、配置注入、结构接口、native helper mock 和真实 hbb_common Cargo 临时 binary-target check（避免 example 引入无关 dev dependencies）；生成 exact SHA bridge 后，Flutter 3.24.5 analyze 四个补丁相关页面，error 为致命失败，upstream warnings/infos 留日志。
- Rust 快检编译真实 hbb_common 与实际 helper，检查 Config 函数类型，不覆盖完整 root Rust app/平台 codec；后续两个 Windows full builds 覆盖实际 root Rust 和 Flutter 编译。结构测试验证历史 SOS UI guards，不能证明所有导航入口安全；SOS 仍不是 Level 3 禁止主控。
- build-baseline.json 对历史构建关键文件保存 SHA256；变动给 WARNING。缺少 Windows adapter 文件/参数或最低 Rust 版本迁移则 FAIL，需人工审查固定工具链。不会自动修改 Patch。
- 诊断 artifact 与 step summary 保留失败 patch/hunk/API/compiler 信息。不使用 --reject、fuzz 忽略或关键 continue-on-error。

Patch revision 存在 `patch-revision.txt`。同一 upstream 修订 Patch 后人工递增 revision。测试 tags 为 `vX.Y.Z-custom-test.N` / `vX.Y.Z-sos-test.N`；不改 Cargo/Flutter/Windows 内部官方版本，不覆盖现有 tag/assets。GitHub 的 prerelease 标记决定测试身份。

只有两边 build、源 SHA/maintenance SHA/Common hash/run 一致、checksum 全覆盖、PE AMD64 验证通过，才创建两个 draft、上传完全部资产并提升为 Prerelease。使用本仓库 GITHUB_TOKEN，不使用 PAT。GitHub 不能原子发布两个 Release；若最后 API 阶段出现部分发布，workflow FAIL，之后去重拒绝自动覆盖，等待人工恢复。

去重要求一对完整 prerelease 与源/patch metadata、资产均匹配。已处理版本直接退出；force_rebuild 对已发布 revision 仅重建 artifacts，不覆盖 Release。manual simulate_failure 在临时工作树内模拟缺失文件，不修改 tracked Patch，并阻断后续昂贵 jobs 与发布。

测试 Prerelease 固定声明 Runtime/UI NOT TESTED (SKIPPED BY USER)、Real remote session NOT TESTED、Code signing NOT ENABLED、Configuration TEST ONLY。定时与手动路径都继续使用公开虚构 fixtures，绝不读取生产 Variables/Secrets。

配置/密码逻辑与成功 Patch 不变。官方 Flutter engine main 下载仍浮动，无法保证字节级可复现；文件下载 SHA 写日志。Windows runner 和 apt 依赖也会变化。自动 Issue、密码 V2、生产仓库和新增平台不在本阶段。

## 多代 Patch Set

成功的 1.4.9 补丁已逐字节迁至 patchsets/v1，metadata 保留原构建证据和 hashes；不修改已发布资产。patchsets/v2 基于新客户端 config-key API 和现存 Flutter UI 实现。行为契约及变化见 [API Migration](docs/api-migration-v1-to-v2.md)。

patchsets/index.json 对已验证精确 SHA 固定映射到 v1；未知 SHA 用独立干净 clones 探测候选 v2/v1，严格 patch + 配置/接口检查选取预检兼容候选。选定后仍必须通过真实 Rust 快检、Bridge 和 Flutter analyze 才报告完整兼容 PASS，Windows 全构建另计。没有候选通过则 fail closed，绝不默认套用最新版。

v1/v2 metadata 中的 hashes 是审查后固定值，不会在 CI 自动重算并接受修改。已有 v1 冻结；新的实质迁移创建新一代。每次 artifact/build-info/未来 Release Notes 记录 patchset；Standard/SOS 使用同一 resolver 输出。历史 Release 未包含 patchset 字段时，仅精确已验证 1.4.9/v1/hash 组合允许旧格式去重，绝不修改旧 notes/manifest。

手动重新运行 release-check 1.4.9 可验证去重；simulate_failure=true 可验证昂贵 jobs/发布阻断。upstream-compatibility 用 candidate 并保留每代选择诊断。v2 已由 Actions run 36828069170 验证 Common/SOS、Rust 快检、Bridge 与 Flutter analyze，metadata 为 compatibility_validated；未执行开发分支完整 Windows 构建或 Runtime 验证。去重与失败阻断也已 Actions 实测；schedule 仍仅配置，尚未观察到运行。
