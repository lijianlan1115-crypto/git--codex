# Codex 本地知识库搭建说明

## 资料来源

你的需求资料统一放在：

```text
/Users/jelly/Desktop/work/酒店数字员工
```

这里包含需求文档、功能逻辑蓝图、Word、PDF、Excel、测试数据、本地 Git 代码库和技能包资料。

## 知识库存放位置

抽取后的 Codex 知识库放在：

```text
/Users/jelly/Public/trae-file/6.24考核/6.24考核工作流/knowledge_base
```

生成后会包含：

```text
knowledge_base/
├── CODEX_KNOWLEDGE.md        # 给 Codex 先读的总索引
├── source_manifest.json      # 原始资料清单
├── index.json                # 知识片段索引
└── chunks/                   # 从资料抽取出来的 Markdown 片段
```

## 生成知识库

在项目目录执行：

```bash
cd "/Users/jelly/Public/trae-file/6.24考核/6.24考核工作流"
python3 scripts/build_knowledge_base.py
```

它会自动处理：

- `.md`
- `.txt`
- `.json`
- `.yaml`
- `.html`
- `.docx`
- `.xlsx`
- `.pdf`

PDF 如果没有抽取出文本，建议安装：

```bash
brew install poppler
```

然后重新运行脚本。

## Codex 如何使用知识库

`server.py` 在构造 Codex prompt 时会自动读取：

```text
knowledge_base/index.json
knowledge_base/CODEX_KNOWLEDGE.md
knowledge_base/chunks/*.md
```

它会根据需求、diff、文件名里的关键词，挑选相关知识片段放进 Codex 上下文。

也就是说，当你调用：

```bash
python3 scripts/apply_requirement_change.py \
  --repo hotel--ota-ai \
  --requirement "在价格策略中增加价格下限校验"
```

Codex 会同时参考：

- 本地 Git 代码库
- 当前 Git diff
- V27 业务知识库
- `酒店数字员工` 资料夹抽取出的需求知识库

## 验证知识库是否生成

启动服务后访问：

```bash
curl http://127.0.0.1:8000/knowledge/status
```

或查看：

```bash
ls knowledge_base
```

## 建议规则

原始资料不要直接改动，统一放在 `/Users/jelly/Desktop/work/酒店数字员工`。

抽取结果可以反复生成，属于中间产物。

如果新增需求文档，重新运行：

```bash
python3 scripts/build_knowledge_base.py
```

即可更新 Codex 可用知识。
