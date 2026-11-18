## Why

Windows 打包成功仍出现运行库缺失和 doctest 冗余导入警告。当前整包强制包含扩大编译范围，且缺少可比较的耗时、体积记录和跨 CI 构建缓存。

## What Changes

- Windows 构建自动包含可分发运行库；找不到时警告并继续，正式发布仍须通过干净 Windows 验收。
- 保存 Nuitka 编译报告，输出构建耗时和最终单文件大小。
- 按 lxml、openpyxl、pptx、PIL 的顺序评估并收窄整包强制包含，验证后保留必要动态依赖。
- 在 Windows CI 中恢复和保存 Nuitka 缓存，单独上传构建报告。
- 在分支和 PR 的 CI 中静态检查所有 workflow，提前发现发布配置错误。
- 记录测试结果、对比方法和 Windows 实机验收边界。
- 补齐 Windows 源码回归与成品生成验收；GUI 布局修复及测试合同由 `fix-windows-tooltip-layout` 提供，作为 Windows 验收前置条件。
- 三平台可直接开发和测试源码。正式 Windows exe 由 Windows CI 构建；本地 Windows 可用同一脚本试打包，不强制安装 VS/Build Tools。

## Capabilities

### New Capabilities

- `nuitka-build`: 运行库包含策略、依赖包含、构建证据及 CI 缓存要求。

### Modified Capabilities

无。不改变单 exe 分发、应用功能或配置路径。

## Impact

涉及 build.py、Windows release workflow、构建文档及必要测试。沿用锁定的 Nuitka 4.1.3，不更换编译器，不裁剪 Tk 资源，不关闭单文件压缩。
