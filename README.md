# 基于 Codex 的研发协同变更分析与测试预警工作流

本仓库是考核演示发布包，包含：

- 本地 FastAPI 服务：`server.py`
- Codex CLI 调用脚本：`codex_runner.sh`
- 本地分析/修改脚本：`scripts/`
- V27 业务知识库：`v27-*.json`
- 脱敏后的 Codex 本地知识库：`knowledge_base/`
- 考核说明和演示文档：`docs/`
- GitHub Actions 模板：`target_repo_templates/`

> 安全说明：发布包已排除虚拟环境、日志、输出报告、数据库、账号密码表、真实配置和疑似密钥文件。

## 快速使用

```bash
python3 scripts/build_knowledge_base.py
python3 scripts/build_change_summary.py --repo hotel--ota-ai --requirement "分析当前修改影响" --no-codex
```

详见 `README_考核交付.md` 和 `docs/`。
