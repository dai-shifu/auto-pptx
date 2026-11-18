## Why

Windows 源码测试暴露提示框首次布局测量过早的问题。短文本显示为 400px 高窗口，长文本滚动也曾失败，阻碍 `optimize-nuitka-build` 的 Windows 验收。

## What Changes

- 在实际 Text 宽度和换行布局可用后确定提示框高度，并使首次显示与窗口复用行为一致。
- 明确短文本紧凑显示、长文本完整滚动及鼠标跨入提示框的验收要求。
- 调整依赖固定像素、固定屏幕坐标或一次 idle 更新的测试假设，保留功能断言。Tk 初始化失败仍须单独调查。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `preview-overflow-tooltip`: 明确布局稳定后的紧凑高度、首次显示与复用一致性，以及跨平台行为验收。

## Impact

限于 `src/gui_tooltip.py`、对应 GUI 测试和规格。不修改生成行为、配置、依赖或打包工具。修复后作为 `optimize-nuitka-build` Windows 源码回归的前置条件。
