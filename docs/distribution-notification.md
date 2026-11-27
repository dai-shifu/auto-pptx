# Math404 正式发版通知

通知默认关闭。启用后，仅当正式稳定版 `vX.Y.Z` 发布时，请求 Math404 中心对账。通知不修改构建、测试、草稿或附件，也不持有 R2 凭据。

## 启用条件

- 确认 Math404 的 `main` 分支上有 `sync-releases.yml`，并验证中心能同步产物。
- 保护 `distribution-notify` 环境和正式标签，限制谁能创建或更新标签，并审查标签中的通知工作流。无法保护时不要启用。
- 将短期 fine-grained PAT 存为该环境的 `MATH404_DISPATCH_TOKEN`。令牌只访问 Math404 仓库，授予 `Actions: write` 和必要的 `Metadata: read`，不授予 `Contents` 或其他写权限。记录到期、轮换与撤销方式，不在代码或日志中保存令牌。
- 满足以上条件后，设置仓库 Actions 变量 `DISTRIBUTION_NOTIFY_ENABLED=true`。

## 核对结果

在本仓库 Actions 查看通知，在 Math404 Actions 查看同步。GitHub 接受请求不等于镜像已更新。通知失败不会撤销 Release；可等待中心定期对账或手动同步，无需重新发布。

如果改用默认 `GITHUB_TOKEN` 自动发布，发布事件可能不触发通知；应另行验证触发方式。
