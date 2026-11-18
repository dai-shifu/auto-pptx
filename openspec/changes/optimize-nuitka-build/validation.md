# 构建验证

本记录区分源码测试、实际单文件检查和 Windows 发布验收。尚未完成 Windows 发布验收。

## Linux 分步构建

环境：Python 3.12.13、Nuitka 4.1.3、GCC 14。沿用单文件压缩、Tk 插件和锁定依赖。每一步先实际构建，再用生成的单文件执行 GUI 生成检查，之后才移除下一个整包包含。

| 阶段 | 编译 Python 模块与包数 | 最终单文件字节 | 耗时（秒） | C 编译缓存条件 |
| --- | ---: | ---: | ---: | --- |
| 原始整包包含，增加报告 | 473 | 30,296,800 | 385.4 | 未安装 ccache |
| 移除 lxml 整包包含 | 446 | 28,981,984 | 300.8 | 新 ccache，452 次 miss |
| 再移除 openpyxl 整包包含 | 432 | 28,900,064 | 145.3 | 437 次 hit、1 次 miss |
| 再移除 pptx 整包包含 | 386 | 27,429,600 | 139.0 | 391 次 hit、1 次 miss |
| 再移除 PIL 整包包含 | 364 | 27,073,248 | 252.0 | 3 次 hit、367 次 miss |
| 最终配置重复构建 | 364 | 27,073,248 | 138.6 | 370 次 hit，无 miss |

编译模块数取报告中 CompiledPythonModule 和 CompiledPythonPackage 的合计，不包含入口、扩展模块和未编译标准库。上述耗时的缓存条件不同，不能将全部时间差归因于依赖裁剪，也不能推断 Windows 的时间或体积。

取消 lxml 整包包含后，日志不再出现 doctest warning，报告不再包含 lxml.doctestcompare 或 doctest。

最终单文件比基线减少 10.6%，编译模块与包数减少 23.0%。最终报告保留 47 个图片插件，包括 PNG 和 JPEG；PIL.ImageQt 的 anti-bloat 信息提示符合此 Tk 应用的依赖范围，没有通过禁用 warning 隐藏问题。

最终配置重复构建保持相同单文件大小。主程序 370 次 C 编译和 onefile bootstrap 的 1 次编译全部命中缓存。前一轮最终配置仍有 3 次命中，不能视为严格全空缓存基准；Windows 冷、热对比仍待完成。

检查使用 tests/create_fixtures.py 的公共合成构造器，在临时目录给模板增加 PNG 和含嵌入工作簿的原生柱状图。将单文件复制到独立临时目录，在 Xvfb 中通过 Tk 控件执行模板和 Excel 选择、全选、生成。检查首次配置、三行 Excel、生成三页、文本替换、模板标识、图片字节、图表数值和嵌入工作簿。基线、lxml、openpyxl、pptx、PIL 五轮均通过。pptx 和 PIL 轮产物额外通过 XML、关系和图表结构校验。

## 本地回归与配置检查

- 最终完整测试（真实 Xvfb 显示）：166 passed，无跳过。
- OpenSpec 全部严格校验：25 passed。
- 工作流 YAML 解析、缓存作用域和执行顺序、失败后报告保留、用户 artifact 分离检查通过。
- Git 差异空白检查通过。

## Windows 宿主检查

通过 WSL 调用宿主 Git Bash，复用已有 Python 3.12.13 AMD64 环境；没有改动宿主项目源码。

- Nuitka 自身运行库检测返回 None；严格包含运行库时实际退出码为 1，符合新的失败约束。
- 当前完整测试：161 passed、3 failed、2 skipped。失败位于 test_gui_tooltip.py 的长文本滚动、真实指针跨窗口移动、短文本高度测试。
- 从原始 HEAD 导出的临时副本复核 tooltip 测试：7 passed、2 failed、1 skipped。长文本滚动和短文本高度失败同样存在；指针测试在此轮通过，未稳定复现。跳过信息包含 Tk 初始化找不到可用 tk.tcl。
- 不修改无关 GUI 逻辑，不将这些结果表述为 Windows 全部测试通过。

## 待验收

- 准备可分发运行库后，实际构建最终 Windows exe，检查运行库包含和编译报告。
- 在相同 Windows 环境比较冷构建、热构建、最终 exe 体积。
- 在干净 Windows 机器完成单 exe 首次启动、配置、Excel 读取及含图片和图表模板的生成验收。
- 托管 Windows CI 实际验证缓存恢复、保存和报告 artifact 上传；本地配置检查不等于远程 workflow 已运行。

## 2026-11-18 收尾调研

当前 Windows Python 3.12.13、Tk 8.6.12 的诊断确认首次提示框布局存在时序问题：Text 初始 1×1 时短文本被算为 95 行，布局稳定后实际为 2 行，但窗口仍保留 400px 高度。三轮结果一致。补充首次长文本诊断在布局稳定后可以滚动到底，本轮未复现旧日志的负滚动比例。当前 listbox.tcl 存在，四轮诊断的 Tk 初始化成功；历史跳过原因仍需复测。

本次未重新执行 Windows 完整 suite、构建最终 Windows exe 或完成干净机器验收。不能据诊断将历史失败改记为通过。修复计划及 spec 见 `fix-windows-tooltip-layout`，本变更的执行顺序和完成条件见 [Windows 收尾方案](windows-acceptance-plan.md)。

## 2026-11-18 实施验证

- 已修复首次 Text 实际宽度未生效时计算提示框高度的问题；回调生命周期、测试调整及 Windows 截图见 `fix-windows-tooltip-layout/validation.md`。
- 最终源码回归：Linux Xvfb 177 passed；Windows Python 3.12.13 AMD64、Tk 8.6.12、真实桌面、`--require-gui --capture=sys` 177 passed，均无跳过。
- CI 已增加 Windows 全量源码测试，并与 Linux 测试一起作为 Windows 发布构建的前置条件。
- 新增运行库预检脚本及合成成品检查工具。后者的八个源码测试覆盖正常输出及 exe、配置、映射、表格、页数、图表、嵌入工作簿关系损坏；这些测试不代表最终 Windows exe 已验收。
- workflow YAML 解析及 Windows 前置依赖检查通过；OpenSpec 全部严格校验 26 passed。
- 本机运行库预检仍失败，未生成最终 Windows exe，未取得 Windows 冷/热性能或干净机器验收数据。
- 开发者本机不要求安装 VS/Build Tools。后续 Windows 构建仅使用 CI，本机预检失败不触发工具链下载或安装。
- 新 workflow 尚未推送或远程运行；缓存保存、恢复和成品报告仍需托管运行证据。

## 2026-11-18 发布门禁复核

- `actionlint` 1.7.12 检查两个工作流均通过。在临时副本恢复 job 级 `runner.temp` 后，检查按预期失败。托管 CI 尚未执行此检查。
- Linux Xvfb 完整源码测试 177 passed、无跳过。Windows 宿主首次全量运行 176 passed、1 failed，真实指针用例在进入提示框前未定位到源 Treeview。隔离复跑该用例三次均通过，随后全量复跑 177 passed、无跳过。首轮失败原因未确认，未修改测试或放宽断言。
- Windows 宿主使用 Nuitka 4.1.3 运行预检，仍找不到可分发运行库，按发布流程停止，未编译、未生成 exe。托管 Windows 构建和同一发布包的干净 Windows 生成验收仍待完成。
