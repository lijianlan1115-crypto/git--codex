# 扣子触发 GitHub Actions + Codex 修改方案

## 目标

扣子不直接修改本地文件，而是把需求变更发送给 GitHub Actions。GitHub Actions 在云端 runner 中运行 Codex，Codex 读取仓库中的代码和需求文档，完成代码、文档、测试和影响分析报告修改，然后创建 Pull Request。

## 前置条件

1. GitHub 仓库中已经包含：
   - `requirements/`
   - `docs/`
   - `contracts/`
   - `runtime/`
   - `tests/`
   - `.github/workflows/codex-change.yml`
2. 仓库 Settings -> Secrets and variables -> Actions 中配置：
   - `OPENAI_API_KEY`
3. 扣子中配置一个可以调用 GitHub API 的 HTTP 节点。
4. GitHub token 需要有触发 Actions 的权限：
   - `actions:write`
   - `contents:read`

## 扣子 HTTP 节点配置

请求方法：

```text
POST
```

请求地址：

```text
https://api.github.com/repos/TAI-YE-2/hotel--ota-ai/actions/workflows/codex-change.yml/dispatches
```

Headers：

```text
Authorization: Bearer <GITHUB_TOKEN>
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2022-11-28
Content-Type: application/json
```

Body：

```json
{
  "ref": "main",
  "inputs": {
    "requirement": "{{input}}",
    "base_branch": "main",
    "focus_paths": "requirements,runtime,tests,docs,contracts"
  }
}
```

GitHub API 成功触发时通常返回 HTTP `204 No Content`。

## 扣子工作流建议

```text
开始节点
↓
HTTP 请求：触发 GitHub Actions
↓
大模型节点：告诉用户“已触发 Codex 修改流程，稍后在 GitHub PR 中查看结果”
↓
结束
```

如果要进一步查询结果，可以增加 GitHub API 查询 workflow run 或 PR 列表。

## 演示话术

扣子作为云端工作流不能直接控制本地文件，也不能直接运行本地 Codex CLI。因此本方案采用生产化协作方式：扣子负责提交需求，GitHub Actions 负责运行 Codex，Codex 在仓库环境中修改代码和文档，最终通过 PR 交付，开发人员审核后合并。
