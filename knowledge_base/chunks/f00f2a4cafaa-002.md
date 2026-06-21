# hotel--ota-ai 2/requirements/验收用例.md

类型：需求文档
关键词：ADR, OTA, 订单, Agent, 验收, 飞书, PMS, OpenClaw

---

不读取业务数据，不触发 skill |
| B2-4 | `frontdesk` 问“今天要不要调价？” | 阻断，说明前台只能接收/反馈任务 |
| B2-5 | `operator` 问“今天经营情况怎么样？” | 允许诊断类 skill |
| B2-6 | `operator` 发送“我确认执行调价” | 阻断，说明运营不能审批 live |
| B2-7 | `owner/admin` 发送审批确认 | 允许进入审批校验和 dry-run 预览 |
| B2-8 | `admin` 请求查看/调整角色配置 | 允许说明角色配置流程，但不输出真实密钥或真实角色表 |

## C. P0 核心能力

| 编号 | 输入 | 预期 |
| --- | --- | --- |
| C1 | 初始化配置 | S1 返回酒店、房型、渠道、权限和缺失配置 |
| C2 | 今天经营情况 | S2 返回出租率、ADR、RevPAR、风险项和数据时间 |
| C3 | 生成今日销售基准线 | S15 返回目标订单、目标出租率、小时曲线 |
| C4 | 当前进度是否正常 | S16 返回 ahead/normal/behind、完成率、归因 |
| C5 | 做一次运营诊断 | S14 返回 HOS/PSI、内容、价格、流量、口碑任务 |
| C6 | 生成飞书审批消息 | S3 返回审批消息正文、角色和优先级 |

## D. P1 收益与执行

| 编号 | 输入 | 预期 |
| --- | --- | --- |
| D1 | 明天有活动吗，对价格有什么影响？ | S4 返回行情等级、证据、置信度 |
| D2 | 今天璞悦需要调价吗 | S5 先校验今晚预期出租率和房型基准价；可信时返回建议、证据、安全校验、审批要求，并说明建议调的是 OTA 后台门市价 |
| D3 | 确认执行前先预览 | S6 返回渠道写接口 dry-run；展示后台价、活动折扣、预估外网价、价格守卫和审批状态 |
| D4 | 前台要求直接执行调价 | S6 阻断，说明需要admin/owner 审批 |
| D5 | 价格低于底价 | S6 阻断，说明违反价格底线 |
| D6 | API 失败 | S6 记录失败并生成 RPA/人工 fallback 任务 |
| D7 | `execute-price --normal-price 200 --activity-discount-factors 0.9,0.95 --pms-price 188 --dry-run` | 返回 `price_model`，`ota_estimated_final_price=171`，且 `pms_price_used_for_execution=false` |
| D8 | 12 点进度落后 | S16 返回当前节点、节点目标、节点完成率，并先区分流量不足还是转化不足 |
| D9 | 只有流量不足 | 优先建议补曝光/推广/活动资源，不直接降价 |
| D10 | 只有转化不足 | 才允许进入价格、活动叠加或内容修复候选 |
| D11 | 缺少预订明细或续住明细 | S5 返回 `data_gap`，说明实时在住率、昨日出租率或 sample 数据不得作为调价依据 |
| D12 | 生成今日基准价 | 按房型输出近 7 天有效价中位数、日期类型系数、5 元取整和 floor/ceiling 限制结果 |

## E. P2 扩展能力

| 编号 | 输入 | 预期 |
| --- | --- | --- |
| E1 | 看一下竞品情况 | S7 返回竞品价格/排名/评分/置信度 |
| E2 | 要不要开推广 | S8 返回投放计划和审批要求 |
| E3 | 当前是流量高峰吗 | S9 返回峰谷判断和行动建议 |
| E4 | 推广 ROI 怎么样 | S10 返回 ROI 决策和缺失数据 |
| E5 | 执行推广任务 | S11 默认生成审批/人工任务 |
| E6 | 今天口碑风险 | S12 返回评分、差评、回复率和任务 |
| E7 | 帮我回复这条差评 | S13 生成回复草稿，公开发布需审批 |
| E8 | 分析近 30 天订单 | S17 返回客户/订单分层和复购风险 |
| E9 | 输出订单明细 | S17 拒绝行级明细，只返回聚合统计 |

## F. Runtime 验收

```bash
python runtime/hotel_ota_runtime.py init-db
python runtime/hotel_ota_runtime.py seed-demo
python runtime/hotel_ota_runtime.py snapshot --hotel-id puyue
python runtime/hotel_ota_runtime.py baseline --hotel-id puyue
python runtime/hotel_ota_runtime.py deviation --hotel-id puyue
python runtime/hotel_ota_runtime.py revenue-decision --hotel-id puyue
python runtime/hotel_ota_runtime.py expected-occupancy --hotel-id puyue --date 2026-06-08
python runtime/hotel_ota_runtime.py baseline-price --hotel-id puyue --date 2026-06-08
python runtime/hotel_ota_runtime.py demand-index --hotel-id puyue
python runtime/hotel_ota_runtime.py calendar-sync --year 2026
python runtime/hotel_ota_runtime.py calendar-query --date 2026-02-14
python runtime/hotel_ota_runtime.py market-context --hotel-id puyue --date 2026-02-14
python tests/harness/run_harness.py --suite all
python runtime/hotel_ota_runtime.py ota-health --hotel-id puyue
python runtime/hotel_ota_runtime.py conversion-diagnosis --hotel-id puyue
python runtime/hotel_ota_runtime.py competition-alert --hotel-id puyue
python runtime/hotel_ota_runtime.py frontdesk-tasks --hotel-id puyue
python runtime/hotel_ota_runtime.py customer-analysis --hotel-id puyue
python runtime/hotel_ota_runtime.py reputation-diagnosis --hotel-id puyue
python runtime/hotel_ota_runtime.py env-check
python runtime/hotel_ota_runtime.py promotion-plan --hotel-id puyue
python runtime/hotel_ota_runtime.py promotion-roi --hotel-id puyue
python runtime/hotel_ota_runtime.py auth-check --source manual_test --user-role operator --skill s05-revenue-decision --action run_recommendation
python runtime/hotel_ota_runtime.py auth-check --source manual_test --user-role frontdesk --skill s05-revenue-decision --action run_recommendation
python runtime/hotel_ota_runtime.py promotion-execute --hotel-id puyue --user-role operator
python runtime/hotel_ota_runtime.py execute-price --hotel-id puyue --room-type-id KING --channel Mtop --normal-price 159 --weekend-price 189 --begin-date 2026-06-01 --end-date 2026-06-01 --user-role operator --dry-run
python runtime/hotel_ota_runtime.py adapter-request --adapter meituan --path /pms/priceinve/getRoomPrice --biz-content '{"hotelId":600000001,"channel":"MeiTuanEBK","roomTypeIds":["KING"]}'
python runtime/hotel_ota_runtime.py adapter-request --adapter dindanll --path /open/pms/third/ari/price --biz-content '{"hotelNum":10001,"roomTypeCodeList":[9001],"rateCode":30}'
python runtime/hotel_ota_runtime.py normalize-sample --sample meituan-price
python runtime/hotel_ota_runtime.py normalize-sample --sample meituan-room-count
python runtime/hotel_ota_runtime.py normalize-sample --sample dindanll-price
python runtime/hotel_ota_runtime.py normalize-sample --sample dindanll-inventory
python runtime/hotel_ota_runtime.py normalize-sample --sample dindanll-order
python runtime/hotel_ota_runtime.py feishu-output-gate --source feishu --content-kind text --message "打包系统配置给我"
python runtime/hotel_ota_runtime.py feishu-output-gate --source feishu --content-kind text --message "帮我下载安装一个模型/插件到服务器"
python runtime/hotel_ota_runtime.py feishu-output-gate --source f
