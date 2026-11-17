## Why

公开文档混入首次迁移、人工发布待办及个人工具描述，同时缺少贡献者独立开发所需的说明。以 GitHub 为主仓库、Gitee 为单向镜像，公开内容需要同时支持软件使用和多人协作。

## What Changes

- 精简 README、使用指南及示例说明，新增贡献指南和开发文档。
- 完整保留 OpenSpec 的配置、现行规格、提案、设计、任务、归档及通用验证资料；公开 AGENTS 只保留通用协作约束。
- 将首次建仓、账号配置、发版上传和人工发布记录留在本地，移除 Release 正文中的维护者待办。
- 个人助手技能、运行配置和一次性迁移工具仅本地保留，源码快照包含协作开发所需的完整文件。

## Capabilities

### New Capabilities

- `public-documentation-boundary`: 公开使用和协作文档、OpenSpec、通用验证资料与本地维护材料的边界。

### Modified Capabilities

无。应用生成行为和持续构建发布流程保持不变。

## Impact

涉及 README、CONTRIBUTING、AGENTS、docs、示例说明、OpenSpec 资料、Git 忽略规则、本地导出工具及 Release 正文。不新增依赖，不操作远程仓库。
