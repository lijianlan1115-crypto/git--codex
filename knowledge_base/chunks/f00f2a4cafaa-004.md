# hotel--ota-ai 2/requirements/验收用例.md

类型：需求文档
关键词：ADR, OTA, 订单, Agent, 验收, 飞书, PMS, OpenClaw

---

S2/S16 |
| F5-5 | 日历 + 天气 + fresh S2/S16 | 只允许输出 S5 行情增强信号，`approval_allowed=false` |

## F6. 飞书指令菜单验收

| 编号 | 输入/操作 | 预期 |
| --- | --- | --- |
| F6-1 | `command-menu-start --source feishu --hotel-id puyue --open-id ou_operator --chat-id oc_project --message "菜单"` | 返回 `status=ok`、`menu_id`、`expires_at` 和按角色过滤后的 `available_commands` |
| F6-2 | 同一 `open_id + chat_id` 回复 `1` | 执行经营快报，返回 `execution_status=executed` 和 `final_reply` 脱敏摘要 |
| F6-3 | 其他用户回复 `1` | 返回 `blocked_reason=menu_owner_mismatch`，不执行 |
| F6-4 | 菜单过期后回复编号 | 返回 `blocked_reason=menu_expired`，不执行 |
| F6-5 | 回复 `8` 但缺少房型、渠道、价格、日期 | 返回 `status=awaiting_params` 和固定参数提示 |
| F6-6 | 回复 `8 KING Mtop 200 2026-06-08 2026-06-08 0.9,0.95 188` | 返回调价 dry-run 摘要，`live_call=false`，不输出完整 API 请求体 |
| F6-7 | `frontdesk` 发起菜单 | 只显示前台任务等被授权指令，不显示调价建议和调价 dry-run |
| F6-8 | `guest` 发起菜单 | 返回 `permission-denied` |
| F6-9 | 回复未注册编号或 shell/git 文本 | 返回 `unknown_menu_command`，不得执行自由命令 |

## G. 中文化验收

| 编号 | 操作 | 预期 |
| --- | --- | --- |
| G1 | 搜索 `Use this skill` | skill 正文不再残留英文模板句 |
| G2 | 搜索 `Responsibilities`、`Procedure`、`Output`、`Return` | skill 业务章节已改为中文 |
| G3 | 检查 `name` 字段 | 仍保持英文短 ID |
| G4 | 检查 API、命令、JSON 字段 | 仍保持英文，未误翻译 |

## H. 上线准入

- P0/P1 全部用例通过。
- `hotel-ota-chief` 总控 Agent 已启用，或默认 agent 已加载同等 allowlist。
- `AGENTS.md`、`TOOLS.md`、`BOOTSTRAP.md` 已被 OpenClaw workspace 读取。
- 飞书 allowlist 群配置完成。
- 飞书角色表配置完成，未授权用户默认阻断。
- 渠道 API 策略生效，美团/Beyondh/订单来了未授权时不阻塞 P0/P1。
- Beyondh dry-run 请求签名可生成。
- 美团和订单来了 dry-run 请求摘要可生成。
- 数据库只读来源测试通过，未知模板和自由 SQL 被阻断。
- `admin/owner` 审批链路测试通过，`operator/frontdesk/guest` live 审批阻断。
- 所有 `*_ENABLE_LIVE` 仍为 `0`，直到正式上线会议确认。
