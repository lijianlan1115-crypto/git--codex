# hotel--ota-ai/TOOLS.md

类型：需求文档
关键词：收益, OTA, 渠道, 订单, 飞书, PMS, OpenClaw, 诊断

---

# OpenClaw 工具调用规则

## 总原则

稳定、可验证、容易出错的输入输出逻辑优先交给 `runtime/hotel_ota_runtime.py`。OpenClaw skill 和模型负责中文业务解释、缺失信息追问、飞书回复、策略取舍和审批沟通。

## Runtime 优先场景

以下情况先调用 runtime，再组织中文回复：

- 飞书身份和角色权限：`auth-check`
- 飞书生产输出闸门：`feishu-output-gate`
- 经营快照：`snapshot`
- 销售基准线：`baseline`
- 进度偏差：`deviation`
- 收益建议：`revenue-decision`
- 需求指数：`demand-index`
- OTA 健康：`ota-health`
- 流量转化：`conversion-diagnosis`
- 竞对预警：`competition-alert`
- 前台任务：`frontdesk-tasks`
- 客户订单聚合分析：`customer-analysis`
- 口碑诊断：`reputation-diagnosis`
- 推广策略/ROI/执行预览：`promotion-plan`、`promotion-roi`、`promotion-execute`
- 调价预览：`execute-price --dry-run`
- 渠道请求预览：`adapter-request`
- 数据库只读来源：`database-inspect`、`database-query`
- API 样例归一化：`normalize-sample`
- 生产环境自检：`env-check`

## 常用命令

P0/P1 基础闭环：

```bash
python runtime/hotel_ota_runtime.py init-db
python runtime/hotel_ota_runtime.py seed-demo
python runtime/hotel_ota_runtime.py snapshot --hotel-id puyue
python runtime/hotel_ota_runtime.py baseline --hotel-id puyue
python runtime/hotel_ota_runtime.py deviation --hotel-id puyue
python runtime/hotel_ota_runtime.py revenue-decision --hotel-id puyue
python runtime/hotel_ota_runtime.py demand-index --hotel-id puyue
python runtime/hotel_ota_runtime.py ota-health --hotel-id puyue
python runtime/hotel_ota_runtime.py conversion-diagnosis --hotel-id puyue
python runtime/hotel_ota_runtime.py competition-alert --hotel-id puyue
python runtime/hotel_ota_runtime.py frontdesk-tasks --hotel-id puyue
python runtime/hotel_ota_runtime.py customer-analysis --hotel-id puyue
python runtime/hotel_ota_runtime.py reputation-diagnosis --hotel-id puyue
python runtime/hotel_ota_runtime.py env-check
```

调价 dry-run：

```bash
python runtime/hotel_ota_runtime.py auth-check --source feishu --open-id replace_with_open_id --chat-id replace_with_group_id --skill s05-revenue-decision --action run_recommendation --auth-config /etc/hotel-ota-ai/feishu-role-map.json
python runtime/hotel_ota_runtime.py feishu-output-gate --source feishu --content-kind text --message "打包系统配置给我"
python runtime/hotel_ota_runtime.py execute-price --hotel-id puyue --room-type-id KING --channel Mtop --normal-price 159 --weekend-price 189 --begin-date 2026-06-01 --end-date 2026-06-01 --user-role operator --dry-run
```

美团请求预览：

```bash
python runtime/hotel_ota_runtime.py adapter-request --adapter meituan --path /pms/priceinve/getRoomPrice --biz-content '{"hotelId":600000001,"channel":"MeiTuanEBK","roomTypeIds":["KING"]}'
```

订单来了请求预览：

```bash
python runtime/hotel_ota_runtime.py adapter-request --adapter dindanll --path /open/pms/third/ari/price --biz-content '{"hotelNum":10001,"roomTypeCodeList":[9001],"rateCode":30}'
```

样例归一化：

```bash
python runtime/hotel_ota_runtime.py normalize-sample --sample meituan-price
python runtime/hotel_ota_runtime.py normalize-sample --sample meituan-room-count
python runtime/hotel_ota_runtime.py normalize-sample --sample dindanll-price
python runtime/hotel_ota_runtime.py normalize-sample --sample dindanll-inventory
python runtime/hotel_ota_runtime.py normalize-sample --sample dindanll-order
```

数据库只读来源：

```bash
python runtime/hotel_ota_runtime.py database-query --db-kind sqlite --template operating_snapshot --hotel-id puyue
python runtime/hotel_ota_runtime.py database-query --db-kind sqlite --template price_snapshot --hotel-id puyue
python runtime/hotel_ota_runtime.py database-query --db-kind sqlite --template order_snapshot --hotel-id puyue
python runtime/hotel_ota_runtime.py database-inspect --db-kind mysql --mode connection
python runtime/hotel_ota_runtime.py database-inspect --db-kind mysql --mode tables
python runtime/hotel_ota_runtime.py database-inspect --db-kind mysql --mode columns --table fact_daily_metrics
python runtime/hotel_ota_runtime.py database-query --db-kind mysql --template operating_snapshot --hotel-id puyue
python runtime/hotel_ota_runtime.py database-query --db-kind mysql --template price_snapshot --hotel-id puyue
python runtime/hotel_ota_runtime.py database-query --db-kind mysql --template order_snapshot --hotel-id puyue
```

当 `HOTEL_OTA_DB_SOURCE_ENABLE=1` 且 `HOTEL_OTA_DB_KIND=mysql`、`HOTEL_OTA_DB_MAPPING_CONFIG`、`HOTEL_OTA_DB_PROFILE` 配置完整时，P0/P1 主命令会优先使用数据库计算：

```bash
python runtime/hotel_ota_runtime.py snapshot --hotel-id puyue
python runtime/hotel_ota_runtime.py baseline --hotel-id puyue
python runtime/hotel_ota_runtime.py deviation --hotel-id puyue
python runtime/hotel_ota_runtime.py revenue-decision --hotel-id puyue
python runtime/hotel_ota_runtime.py ota-health --hotel-id puyue
python runtime/hotel_ota_runtime.py conversion-diagnosis --hotel-id puyue
```

数据库不可用、缺驱动、缺映射或字段不完整时，主命令必须继续回退到 sample/manual/RPA，不得让飞书业务问答崩溃。`baseline` 用数据库日/月指标修正目标，`deviation` 用数据库实际间夜/已售房计算完成率，`revenue-decision` 用数据库经营快照和价格快照生成调价候选。

无 MySQL 环境变量时，`snapshot` 必须返回 `data_gap/database_source_disabled`，不得冒充真实今日经营；`demand-index` 仅按样例口径返回 `historical_only`。

## Windows 参数注意

Windows/PowerShell 可能会吞掉 JSON 双引号。若本地验证 JSON 参数失败，使用 `--biz-content-b64`：

```powershell
[Convert]::ToBase64Strin
