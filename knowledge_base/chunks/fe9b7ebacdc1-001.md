# hotel--ota-ai 2/skills/hotel-ota/s14-operation-diagnosis/references/rules.md

类型：字段契约
关键词：RevPAR, ADR, OTA, 字段, 诊断

---

# S14 酒店运营诊断 规则

## 核心输入字段
- `hos_score`
- `merchant_operation_score`
- `peer_rank`
- `exposure`
- `views`
- `payment_conversion_rate`
- `rating_total`
- `bad_review_rate`

## 判断逻辑
1. 平台官方评分优先，自建漏斗评分辅助
2. 先修转化再做流量或降价
3. 输出 A/B 任务和责任人
4. 场景必须先分流：
 - `own_hotel_daily_diagnosis`：自有酒店日常运营诊断，用于内部经营复盘和改进动作
 - `live_acquisition_external_report`：直播获客/对外诊断报告，用于客户上传资料后的第三方评估
5. 未确认输入要求前，对外诊断只追问数据和说明缺口，不生成伪完整报告

## 数据库来源
- 可读取 `database-query --template operating_snapshot`、`price_snapshot`、`order_snapshot`、`daily_metrics` 作为诊断证据。
- 数据库证据必须标注 `data_source_type=sqlite_db/mysql_db/postgres_db` 和字段质量。
- MySQL 日经营指标通过 `metric_aliases` 归一化，不直接解释 `metric_name` 原始文本。
- 数据库字段缺失时继续使用 API/RPA/manual/sample 兜底。
- sample/demo OTA 字段必须显式标记 `demo_data`，不得包装成正式数据库诊断。
- `conversion-diagnosis` 生产默认短摘要；完整 evidence 仅在 CLI `--debug` 或 `HOTEL_OTA_FEISHU_DEBUG=1` 时显示。
- 当 RevPAR 为 0 但 ADR 和出租率存在时，优先提示字段映射/导入风险，不直接判定经营异常。

## 可配置参数
- 蓝图中未最终确认的阈值标记为 `configurable`。
- 多源资料冲突时输出 `needs_business_confirm`，并采用更保守建议。
- API 未确认时字段质量为 `manual_required` 或 `inferred`。

## 异常处理
- 缺关键字段时先追问或降级为 sample/manual/RPA，不让 skill 失败退出。
- 低质量字段只能用于诊断、提示和 dry-run，不得用于真实执行。
- 原始 API 状态码必须先由 runtime 转成统一枚举后再解释。
- 输出必须包含或引用 `data_business_date`、`data_snapshot_time`、`freshness_status`。
- 对外报告不得引用内部 runtime 字段、源码、配置、数据库表名或样例评分；客户上传数据必须标明来源和日期。

## 安全规则
- 真实调价、房量、推广、评论发布必须审批。
- 所有写动作默认 `dry_run=true`。
- 必须记录请求摘要、响应码、失败原因和人工处理建议。
