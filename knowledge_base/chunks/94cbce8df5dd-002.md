# hotel--ota-ai 2/runtime/decisions/deviation.py

类型：项目资料
关键词：OTA

---

erating.get("status") == "ok":
 payload.update(operating.get("payload") or {})
 operation = database_evidence["operation_diagnosis"]
 if operation.get("status") == "ok":
 payload.update(operation.get("payload") or {})

 daily = database_evidence.get("daily_metrics", {})
 daily_payload = daily.get("payload") or {}
 operating_payload = (database_evidence.get("operating_snapshot", {}) or {}).get("payload") or {}
 order_result = database_evidence.get("order_snapshot", {}) or {}
 order_payload = order_result.get("payload") or {}
 baseline_payload = _latest_baseline(args.db, args.hotel_id, target_date)

 target_source = "daily_metrics.previous_day_room_nights"
 target_basis_date = daily_payload.get("data_business_date")
 target_freshness = _freshness_status(daily) or "missing_date"
 if baseline_payload and baseline_payload.get("target_orders"):
 target_orders = int(round(float(baseline_payload["target_orders"])))
 target_source = "baselines.target_orders"
 target_basis_date = baseline_payload.get("target_basis_date") or baseline_payload.get("data_business_date")
 target_freshness = baseline_payload.get("freshness_status") or target_freshness
 else:
 target_orders = int(round(_metric(daily, "room_nights") or 15))
 target_orders = max(target_orders, 1)

 order_actual = _today_order_count(order_payload, target_date) if order_result.get("status") == "ok" else None
 actual_orders_value = order_actual
 actual_source = None
 actual_basis_date = None
 actual_freshness = _freshness_status(order_result) or "missing_date"
 actual_trusted = False
 if actual_orders_value is not None:
 actual_orders = actual_orders_value
 actual_source = "order_snapshot.business_date_or_checkin_time"
 actual_basis_date = order_payload.get("data_business_date") or target_date
 actual_trusted = actual_freshness == "fresh" and actual_basis_date == target_date
 else:
 actual_orders_value = _first_number(
 operating_payload.get("orders_today"),
 operating_payload.get("sold_rooms_today"),
 payload.get("orders_today") if payload.get("data_source_type") != "sample_data" else None,
 )
 actual_freshness = _freshness_status(database_evidence.get("operating_snapshot", {})) or "missing_date"
 if actual_orders_value is not None:
 actual_orders = actual_orders_value
 actual_source = "operating_snapshot.orders_today_or_sold_rooms_today"
 actual_basis_date = operating_payload.get("data_business_date") or payload.get("data_business_date")
 actual_trusted = actual_freshness == "fresh" and actual_basis_date == target_date
 else:
 actual_orders = _first_number(operating_payload.get("sold_rooms"), operating_payload.get("occupied_rooms")) or 0
 actual_source = "operating_snapshot.current_occupied_rooms_proxy"
 actual_basis_date = operating_payload.get("data_business_date") or payload.get("data_business_date")
 actual_trusted = False

 progress_checkpoint = _active_checkpoint()
 checkpoint_target_orders = _checkpoint_target_orders(baseline_payload, target_orders, int(progress_checkpoint["hour"]))
 daily_completion = float(actual_orders) / target_orders
 checkpoint_completion = float(actual_orders) / checkpoint_target_orders
 context = _traffic_conversion_context({**payload, **operating_payload})
 retrospective_completion = None
 historical_progress_mode = False

 if checkpoint_completion >= 0.9:
 direction = "ahead"
 recommendation = "节点进度领先。若数据为今日实时口径，继续观察晚高峰；若为历史数据，仅用于复盘。"
 downstream = "S5"
 elif checkpoint_completion >= 0.65:
 direction = "normal"
 recommendation = "节点进度正常。优先维护内容、库存和价格一致性，不急于降价。"
 downstream = "S14"
 else:
 direction = "behind"
 if context["traffic_problem"] and not context["conversion_problem"]:
 recommendation = "节点进度落后且流量不足，先补曝光、推广入口和活动资源，不直接降价。"
 downstream = "S9/S14"
 elif context["conversion_problem"]:
 recommendation = "节点进度落后且转化不足，先排查价格一致性、活动叠加和内容页，必要时再进入调价候选。"
 downstream = "S14/S5"
 else:
 recommendation = "节点进度落后，但缺少流量/转化分子分母证据；先补数据，再判断是否需要调价。"
 downstream = "S14"

 if not actual_trusted:
 if actual_basis_date == target_date and actual_orders is not None and target_orders > 0:
 retrospective_completion = float(actual_orders) / target_orders
 historical_progress_mode = True
 daily_completion = None
 checkpoint_completion = None
 direction = "data_gap"
 context = {
 "traffic_problem": None,
 "conversion_problem": None,
 "problem_basis": "actual_orders_not_today_realtime",
 }
 recommendation = (
 "该日期只能做历史日终复盘，不能当作实时节点进度；"
 "流量/转化判断和 S5 调价交接均已阻断。"
 if historical_progress_mode
 else "实际订单不是同日期 fresh 实时口径；完成率、流量/转化判断和 S5 交接均已阻断。"
 )
 downstream = "S14"

 metrics_freshness = _freshness_status(daily)
 freshness_status = actual_freshness if actual_trusted else (metrics_freshness or "missing_date")
 target_same_date = target_basis_date in (None, target_date)
 target_trusted = (
 target_orders > 0
 and target_source in {"baselines.target_orders", "daily_metrics.previous_day_room_nights"}
 and target_same_date
 and target_freshness not in {"demo_data", "missing_date"}
 )
 downstream_allowed = bool(actual_trusted and target_trusted)
 business_stat
