## Context

锁定版本为 Nuitka 4.1.3、Python 3.12。原脚本强制包含 src、openpyxl、pptx、lxml、PIL；用户 Windows 日志有 484 个 C 文件，390 次缓存命中，payload 从 89,676,662 压缩到 21,852,392 字节。日志没有阶段耗时，不能据此承诺优化比例。

## Goals / Non-Goals

**Goals:** Windows 运行库缺失时阻止发布；减少无用包含；保留可比较证据；复用 CI 编译缓存。

**Non-Goals:** 不修改 GUI 或生成逻辑，不切换打包工具或编译器，不裁剪 Tcl/Tk 或图片格式，不改变压缩及单 exe 分发。

## Decisions

1. Windows 使用 `--include-windows-runtime-dlls=yes`。由 Nuitka 检测实际可分发运行库，缺少时失败；不通过隐藏 warning 或手工复制未知 DLL 绕过检测。
2. 输出 `dist/compilation-report.xml`，用单调时钟输出耗时，并读取最终 exe（Linux 为同名无扩展文件）大小。失败保持原退出码，不输出成功摘要。
3. 先建立未裁剪基线，再依次移除 lxml、openpyxl、pptx 的整包包含并验证；PIL 单独评估。依赖自动跟随静态导入，Nuitka 自带 package config 处理数据和动态导入。src 保留。缺少的模块定点补充；没有 Windows 验证时明确保留待验收项。
4. CI 通过 NUITKA_CACHE_DIR 指定 runner 临时目录。缓存按操作系统、架构、Python、锁文件隔离，每次 run/attempt 使用新 key，并从同依赖前缀恢复。构建报告作为单独维护者 artifact 上传，失败时尽可能保留，不进入用户下载包。
5. 验证先做构建脚本失败传播和 Windows 参数边界测试，再运行完整 GUI 测试。实际编译对比记录平台和缓存条件，不能把 Linux 数据作为 Windows 性能结论。
6. 可复用的 CI 增加独立的 `Workflow lint` job，用固定版本的 actionlint 检查所有 workflow，包括 PR 不执行的 Release。Release 等待该检查和两个平台的源码测试都通过。缓存与编译步骤在步骤级引用 `runner.temp`，避免在 job 级环境变量中使用不可用的上下文。

## Risks / Trade-offs

- [动态导入或包数据缺失] → 按包逐项验证，检查报告及生成结果，必要时保留显式包含。
- [运行库在构建机器缺失] → 文档说明准备 Visual Studio/Build Tools 的 C++ 运行库文件，不允许带警告发布。
- [CI 宿主机预装运行库掩盖分发缺陷] → 干净 Windows 机器额外验证单 exe 启动和生成。
- [缓存首次无收益或被淘汰] → 缓存不作为成功前提，性能比较区分冷、热构建。
- [宿主 Windows 缺少可分发运行库] → 已通过 Git Bash 调用宿主 Python 确认运行库目录为空，严格检查退出码为 1。准备 C++ 构建组件后再做最终 exe 和干净机器验收。
- [宿主 Windows GUI 测试失败或跳过] → 与原始提交对比，记录实际通过范围，不将 Linux 测试结果代替 Windows 验收，不在打包变更中扩展修改 GUI。

## Migration Plan

按运行库约束、报告基线、依赖收窄、CI 缓存顺序执行。发生功能回归时恢复对应包的强制包含，报告和运行库检查保留。

## Windows Acceptance Plan

Windows 收尾顺序和完成条件见 [Windows 收尾方案](windows-acceptance-plan.md)。`fix-windows-tooltip-layout` 修复已确认的首次布局缺陷并同步测试合同；本变更负责构建环境预检、Windows 源码回归入口、成品生成、干净机器及冷/热构建验收。两者分别保留证据，源码通过不替代成品验收。不在本轮加入新的单文件解包缓存或编译策略。

用户确认开发者本机不安装 VS/Build Tools。三平台直接开发、测试源码，Windows exe 由已有 CI 构建机生成。构建机的运行库依赖不转为开发者环境要求，本机预检失败不触发自动下载或安装。
