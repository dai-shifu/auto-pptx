## ADDED Requirements

### Requirement: 新用户可以用公开样例生成第一页
项目 SHALL 在中英文 README 提供示例入口，并通过入门指南分别解释「Excel 模板列的值 → PPT 模板页」和「Excel 数据列 → PPT 占位符」。指南 SHALL 指出模板名和占位符名不是同一类标记，说明固定页不会自动保留、不替换图表数据，以及检查不能保证版式或文字不溢出。

#### Scenario: 用户还没有自己的模板和数据
- **WHEN** 新用户按指南打开公开的日报样例
- **THEN** 指南给出工作表、标题行、模板列和映射设置，并引导用户只选 Excel 第 2 行
- **AND** 用户能用现有 GUI 生成一页「日报总览」，不需要 AI、项目源码或 Python 环境

### Requirement: 用户可以选择普通聊天或轻量 Skill 获得同样的入门指导
项目 SHALL 发布可复制的提问示例和可选的 `auto-pptx-onboarding` Skill。两者 SHALL 使用同一份公开指南和样例。Skill SHALL 可被不持有项目源码的用户获取，且不依赖运行脚本、CLI、MCP 或 AI API，不把检测建议说成已确认的映射。

#### Scenario: 用户使用普通聊天工具
- **WHEN** 用户粘贴提问示例和审阅后的检查摘要
- **THEN** 提问示例指导 AI 区分检查事实、自动建议和待确认项，并给出具体 GUI 操作
- **AND** 流程不要求安装 Skill 或上传原始文件

#### Scenario: 用户使用已安装的 Skill
- **WHEN** 用户请求用自己的两份文件生成第一份 PPT，但没有提供可用于诊断的检查结果
- **THEN** Skill 指引用户从 GUI 检查并提供审阅后的摘要，而不是假定可读取本机路径或承诺代为生成
- **AND** 得到摘要后按同一份指南解释问题，指出需要修改的是 Excel、PPT 还是 GUI 设置
