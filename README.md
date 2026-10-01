# RustDesk Custom TEST / DEVELOPMENT

**测试用途，非生产仓库。** 只维护补丁、脚本和手动构建 workflow；不保存完整 upstream 源码，不创建 tag/Release，不定时运行。

Standard = 官方 RustDesk + Common。
SOS = 同一官方 SHA + Common + SOS。

## 固定历史基线

本阶段默认且仅支持官方 [`005a8b4a04fd906c707eefd69c4898aa2c696202`](https://github.com/rustdesk/rustdesk/commit/005a8b4a04fd906c707eefd69c4898aa2c696202)，即正式 tag `1.4.9` 后第 2 个官方提交。不是把 `1.4.9` tag 的 SHA 改名；tag 本身为 `6c578292e8ebbbec708b76986ba8c4bc7c509747`。

- 旧 Standard：`7bf94bf7296c054a34828ea5d8958e18395ab3e6`，parent 就是选定基线。
- 旧 SOS：`54ab5a78a45f3d0f1d7d5257bfe18f4095cb9121`，parent `e2149974ccda5a063a2647bdd10d70da850b629b`。
- 选定基线保留两个旧版都有的官方 Windows 剪贴板修复；相对旧 SOS 只新增一个官方韩语翻译提交。
- `libs/hbb_common` 保留官方 gitlink，固定 `7e1c392c62d39c364127307cd408421dd5f8cfb0`；只改两行服务器默认配置，不 vendor 32 个文件，不使用 `submodule update --remote`。

旧仓库 `billradar/rustdesk` 与 `billradar/rustdesk-sos` 始终只读；测试不触发它们的 Actions。

## 补丁

| Patch | 目标 / 用途 |
|---|---|
| common/0001-hbb-server-defaults.patch | 官方 hbb_common/src/config.rs：用编译参数替换 ID server、公钥常量；在 submodule 内 apply |
| common/0002-client-defaults.patch | src/common.rs：API fallback；原有 hard password、verification-method、remote configuration 和 hide-cm 默认行为；可选 relay 默认值 |
| common/0003-hide-cm-setting.patch | desktop_setting_page.dart：恢复旧 Standard 的 hide-cm 设置项 |
| sos/0001-sos-mode.patch | 原有 BUILTIN sos-mode=Y；复用 Common 初始化，不重复服务器配置 |
| sos/0002-sos-home.patch | connection_page.dart、desktop_home_page.dart：逐字保留旧 SOS 首页和提示隐藏 |
| sos/0003-sos-settings.patch | desktop_setting_page.dart、desktop_tab_page.dart：逐字保留旧 SOS settings/图标限制 |

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

- upstream_ref：默认 exact SHA；其他 SHA/tag 会明确失败。这里暂不承诺多版本支持。
- variant：standard / sos / both，默认 both。
- 只有 workflow_dispatch，`permissions: contents: read`；无 push/PR/schedule 触发，无 Release job。

Linux bridge job 按官方配方生成同一基线的桥接文件（Rust 1.75.0、Flutter 3.22.3、cargo-expand 1.0.95、flutter_rust_bridge_codegen 1.80.1）。Windows 两个独立 matrix jobs 使用 Windows 2022、Rust 1.75.0、Flutter 3.24.5、LLVM 15.0.6、vcpkg `120deac3062162151622ca4860575a33844ba10b`；取相应 upstream 官方构建步骤，调用该 SHA 的 `build.py --portable --flutter --skip-portable-pack --hwcodec --vram`。

没有永久复制官方大 workflow。第三方 Actions 使用官方配方已有完整 SHA pin。Flutter 自定义 engine 的下载地址仍为官方 `main` Release，下载哈希写在日志；此历史依赖仍可能变化，暂不能保证多年后字节一致重建。

每个客户端 artifact 名为 `rustdesk-1.4.9-upstream2-<standard|sos>-test-windows-x86_64`，内含可解压运行的完整 Flutter Release 目录、WindowInjection.dll、build-info.json、SHA256SUMS、许可证及补丁。不是已签名 MSI/自解压安装包；不包含旧 workflow 额外下载的打印机驱动或 usbmmidd 驱动，因此打印/虚拟显示驱动安装功能未宣称等价。这些打包扩展后续再按需要验收。

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

本阶段不实现 password V2、master compatibility、定时检测、自动 Release、正式仓库或多平台矩阵。真实服务器的被控会话和交互 UI 验收尚需可授权的测试环境；虚构域名只用于构建复现，不会提供可用远程连接。

源码许可沿用 upstream AGPL-3.0；通过 manifest 精确 SHA + 本仓库补丁可以恢复对应源码，官方 URL 固定为 https://github.com/rustdesk/rustdesk 。
