# 基于Codex的研发协同变更分析与测试预警工作流

副标题：基于本地 Git 代码库的多人协作开发影响分析与测试协同实践

## 项目定位

本项目面向多人协作开发中的需求变更、代码变更和同事提交场景，使用 Codex 理解代码变化，结合 V27 业务知识库识别业务影响，并自动生成协同风险、验证方案、通过标准、失败标准和测试清单。

扣子不是必需组件。当前实现支持两种入口：

- 本地脚本入口：适合考核现场稳定演示。
- HTTP 服务入口：适合接入扣子、飞书、其他工作流平台。

## 本地目录

```text
6.24考核工作流/
├── repos/
│   └── hotel--ota-ai/              # 本地 Git 代码库，Codex 在这里读代码和改代码
├── outputs/                        # 分析结果、Markdown 报告、patch
├── knowledge_base/                 # 从酒店数字员工资料抽取出的 Codex 本地知识库
├── scripts/                        # 本地命令行脚本
├── docs/                           # 考核说明、演示稿、接口文档、测试说明
├── server.py                       # FastAPI 服务入口
├── codex_runner.sh                 # Codex CLI 调用脚本
├── v27-node.json                   # V27 知识库
├── v27-edge.json
├── v27-field.json
├── v27-skill.json
└── v27-mapping.json
```

## 核心流程

```text
需求变更 / Git diff / 同事提交
↓
读取本地 Git 代码库
↓
读取酒店数字员工本地知识库
↓
Codex 理解代码变化或实现需求修改
↓
V27 知识库映射业务影响
↓
生成协同风险、验证方案和测试清单
↓
输出 Markdown / JSON / patch
```

## 两类能力

## 生成 Codex 本地知识库

资料来源：

```text
/Users/jelly/Desktop/work/酒店数字员工
```

生成命令：

```bash
python3 scripts/build_knowledge_base.py
```

生成结果：

```text
knowledge_base/CODEX_KNOWLEDGE.md
knowledge_base/index.json
knowledge_base/source_manifest.json
knowledge_base/chunks/
```

### 1. 只分析，不修改代码

用于我的变更协同、同事提交预警、测试回归判断。

```bash
python3 scripts/build_change_summary.py \
  --repo hotel--ota-ai \
  --requirement "分析当前本地修改是否影响价格、库存和收益策略"
```

输出：

- `outputs/change_summary-latest.json`
- `outputs/change_summary-latest.md`

### 2. 根据需求修改代码并生成预警

用于需求更改后让 Codex 修改涉及部分。

```bash
python3 scripts/apply_requirement_change.py \
  --repo hotel--ota-ai \
  --requirement "在收益策略中增加价格下限校验，并生成测试预警"
```

输出：

- `outputs/change_summary-latest.md`
- `outputs/codex_patch.diff`
- 本地 Git 代码库中的实际文件修改

## HTTP 接口

启动服务：

```bash
export COZE_TOKEN="test-token-123"
uvicorn server:app --host 127.0.0.1 --port 8000
```

只分析：

```bash
curl -X POST http://127.0.0.1:8000/analyze-change \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token-123" \
  -d '{"repo":"hotel--ota-ai","requirement":"分析当前改动的影响"}'
```

修改代码：

```bash
curl -X POST http://127.0.0.1:8000/apply-change \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token-123" \
  -d '{"repo":"hotel--ota-ai","requirement":"根据需求修改涉及代码并生成测试预警"}'
```

## 考核材料

- [一页纸说明](docs/一页纸说明.md)
- [流程图](docs/流程图.md)
- [接口文档](docs/接口文档.md)
- [测试说明](docs/测试说明.md)
- [考核演示讲稿](docs/考核演示讲稿.md)
- [材料清单](docs/材料清单.md)
- [Codex本地知识库搭建说明](docs/Codex本地知识库搭建说明.md)
