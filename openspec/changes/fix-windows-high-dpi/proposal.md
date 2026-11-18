## Why

Windows 2K 屏幕设为 150% 时，现有 exe 的主窗口和文件对话框发虚。用户改用「应用程序」高 DPI 兼容性设置后两处都恢复清晰，但发布版不应要求用户手动设置。

## What Changes

- 让 Windows 单文件 exe 默认具备系统 DPI 感知，保留系统原生文件对话框。
- 修正预览数据行的行高和文字上下留白，避免 150% 缩放下相邻行挤在一起。
- 在实际 Windows 100% 和 150% 缩放下验收成品，检查主窗口、两个浏览弹窗、预览行高和悬停提示。
- 不改预览列宽分配，不做跨不同缩放显示器的动态适配，不更改非 Windows 的显示行为。

## Capabilities

### New Capabilities

- `windows-high-dpi`: Windows 发布版默认启用系统 DPI 感知，并保证数据预览的文字不裁切、上下有留白。

### Modified Capabilities

无。

## Impact

涉及 Windows 构建入口、必要的 GUI 尺寸修正及成品验收说明。不更换 GUI 框架或打包工具，不改文件选择、配置和生成流程。
