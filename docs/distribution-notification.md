# Math404 正式发版通知

该工作流只在正式 Release published 时通知 math404 中心执行对账，不修改构建、测试、草稿审核或附件，也不持有 R2 凭据。GitHub API 接受 dispatch 并不表示镜像已同步成功。

## 启用前置

- 等待 math404 [中心分发 PR](https://github.com/dai-shifu/math404/pull/3) 合并，确认 sync-releases.yml 位于 main，中心生产同步已验证。
- 为本仓库单独创建短有效期 fine-grained PAT，仅选择私有 math404 仓库，Actions: write 和必要 Metadata: read；不授予 Contents 或其他写权限。
- 在本仓库 Settings → Environments 创建 distribution-notify，保护正式 tag（如 v*，并限制谁能创建/更新正式 tag），在该环境保存 MATH404_DISPATCH_TOKEN。正式 release workflow 运行于 release tag 对应的可信提交；必须审查 tag 中的通知 workflow，不 checkout 或运行发行包。若无法保护该环境，保持未启用。
- 确认以上配置后设置仓库 Actions variable DISTRIBUTION_NOTIFY_ENABLED=true；默认未设置时跳过通知。记录 token 到期时间、持有人、轮换与撤销流程。不要把 token 写入代码或日志。
- 下一次真实正式发布后在两个仓库 Actions 中检查通知与同步结果；现有版本由中心手动同步，不需重新发布。通知失败不撤销 GitHub Release；每日全项目对账与手动触发可恢复。
- 若未来用默认 GITHUB_TOKEN 自动发布正式 Release，GitHub 的事件防递归机制可能不会启动本 workflow；发布成功后须显式 dispatch 或使用能触发事件的受限凭据。当前人工审核草稿并发布的流程无需修改。
