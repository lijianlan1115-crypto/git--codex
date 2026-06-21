# 读取真实项目代码但不修改：Codex 影响分析工作流

## 目标

`git--codex` 是测试工作区和报告仓库，不直接存放完整业务代码。

真实团队协作代码仍然在：

```text
TAI-YE-2/hotel--ota-ai
```

本 workflow 做的是：

```text
扣子
↓
触发 git--codex 的 GitHub Actions
↓
Actions checkout hotel--ota-ai 到临时目录
↓
读取 git log / git diff / PR diff
↓
Codex 分析影响
↓
报告提交回 git--codex 的 outputs/
```

## 为什么这样做

这样可以读取真实项目代码和同事提交，但不会污染或修改真实项目仓库。适合考核演示、测试工作区和协同预警场景。

## 需要的 Secrets

在 `git--codex` 仓库 Settings -> Secrets and variables -> Actions 配置：

```text
OPENAI_API_KEY
```

如果 `TAI-YE-2/hotel--ota-ai` 是私有仓库，还需要：

```text
TARGET_REPO_TOKEN
```

`TARGET_REPO_TOKEN` 至少需要读取目标仓库内容的权限。

## 扣子 HTTP 节点

请求地址：

```text
https://api.github.com/repos/lijianlan1115-crypto/git--codex/actions/workflows/analyze-target-repo.yml/dispatches
```

请求方法：

```text
POST
```

Headers：

```text
Authorization: Bearer <GITHUB_TOKEN>
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2022-11-28
Content-Type: application/json
```

Body 示例：

```json
{
  "ref": "main",
  "inputs": {
    "target_repo": "TAI-YE-2/hotel--ota-ai",
    "base_ref": "main",
    "head_ref": "main",
    "compare_mode": "recent_commit",
    "requirement": "分析同事最近一次提交对价格、库存、收益策略的影响",
    "focus_paths": "requirements,runtime,tests,docs,contracts"
  }
}
```

成功触发时 GitHub API 返回 `204 No Content`。

如果返回 `422 Unprocessable Entity`，通常不是权限问题，而是请求体不符合
workflow 的输入定义。请重点检查：

- `ref` 是否是 `git--codex` 仓库真实存在的分支，例如 `main`
- `inputs.compare_mode` 是否只能填写 `recent_commit` 或 `range`
- 请求体里不要出现 workflow 没定义的输入字段
- JSON 里变量必须由扣子变量选择器插入，不要手写错误的 `{{input}}`

第一次联调建议先使用固定 JSON，不要使用动态变量。确认返回 `204` 后，
再把 `requirement` 替换成扣子开始节点的输入变量。

## 输出

报告会写入：

```text
outputs/change_summary.md
outputs/target_change_context.md
outputs/target_diff.patch
```

这些文件提交在 `git--codex` 仓库，不会提交真实项目代码。

## 扣子大模型节点建议

HTTP 节点返回 `204` 时，body 为空是正常现象。后面的扣子大模型节点不要再
要求 HTTP body 里有报告内容，可以输出：

```text
已触发 GitHub Actions。Codex 会在 GitHub Actions runner 中读取目标仓库、
diff 和上下文文件，并把影响分析报告提交到 git--codex 仓库 outputs/ 目录。
```

报告不是同步返回给扣子的，而是异步生成在 GitHub 仓库中。
