# Target Repository Change Context

Generated at: 2026-06-21T10:06:03Z

Target repo: TAI-YE-2/hotel--ota-ai
Base ref: main
Head ref: main
Compare mode: recent_commit
Requirement: 分析最近一次提交对酒店 OTA 数字员工项目的影响
Focus paths: requirements,runtime,tests,docs,contracts,config,skills

## Current HEAD
commit a1c3377c96412093bac196efb88d734e382f5b8e
Author:     TAI-YE <2622027746@qq.com>
AuthorDate: Tue Jun 9 13:55:58 2026 +0800
Commit:     TAI-YE <2622027746@qq.com>
CommitDate: Tue Jun 9 13:55:58 2026 +0800

    support business dataset v1 and strengthen feishu data trust

## Recent commits
a1c3377 support business dataset v1 and strengthen feishu data trust
5cfb5f8 修复 hotel ota runtime 问题
a5347eb fix s5 expected occupancy and baseline pricing
78ae30c fix feishu safety gate and data trust checks
a4733b2 Harden Feishu safety and data trust
c51c511 Add project memory and local embedding setup guide
ed0122a Fix Feishu auth identity and stale data safeguards
aa02d96 Use MySQL data in P0P1 decisions and add config commands

## Repository status

## Repository top-level files
.git/FETCH_HEAD
.git/HEAD
.git/config
.git/config.worktree
.git/description
.git/index
.gitignore
AGENTS.md
BOOTSTRAP.md
MEMORY.md
README.md
TOOLS.md
config/database-source.example.json
config/env.example
config/feishu-role-map.example.json
config/openclaw.example.json
cron/setup-cron.sh
examples/feishu-prompts.md
requirements/OpenClaw实施教程.md
requirements/OpenClaw常用配置命令.md
requirements/OpenClaw总控Agent提示词.md
requirements/OpenClaw自动适配提示词.md
requirements/OpenClaw项目适配说明.md
requirements/P0P1交付清单.md
requirements/P0P1技能测试矩阵.md
requirements/runtime模块化说明.md
requirements/skill_specs.yaml
requirements/价格进度转化字段规则.md
requirements/功能蓝图映射.md
requirements/功能蓝图落地矩阵.md
requirements/商用准入清单.md
requirements/多源依据治理.md
requirements/数字员工长期记忆与归档规范.md
requirements/数据字段字典与来源优先级.md
requirements/渠道API适配策略.md
requirements/生产阶段注意事项.md
requirements/统一数据契约.md
requirements/脚本固化边界.md
requirements/资料索引与引用规范.md
requirements/需求文档.md
requirements/飞书输出规范.md
requirements/验收用例.md
runtime/__init__.py
runtime/cli.py
runtime/common.py
runtime/contracts.py
runtime/hotel_ota_runtime.py
runtime/storage.py
tests/test_security_and_freshness.py
