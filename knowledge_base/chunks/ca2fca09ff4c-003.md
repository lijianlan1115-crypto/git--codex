# hotel--ota-ai 2/runtime/decisions/calendar.py

类型：项目资料
关键词：OTA

---

y: int(value) if isinstance(value, bool) else value for key, value in row.items()},
 )
 return {"status": "ok", "year": year, "rows": len(rows), "seed_file": seed_file, "updated_at": now_local()}

def _row_to_calendar_context(row: Any) -> dict[str, Any]:
 result = dict(row)
 for key in ("is_weekend", "is_workday", "is_holiday", "is_adjusted_workday", "is_off_day"):
 result[key] = bool(result.get(key))
 return result

def get_calendar_day(db_path: str, date_text: str) -> dict[str, Any]:
 date_value = _date(date_text)
 _ensure_calendar_tables(db_path)
 with closing(connect(db_path)) as conn:
 row = conn.execute("SELECT * FROM calendar_days WHERE date=?", (date_value.isoformat(),)).fetchone()
 if row is None:
 sync_calendar_year(db_path, date_value.year)
 with closing(connect(db_path)) as conn:
 row = conn.execute("SELECT * FROM calendar_days WHERE date=?", (date_value.isoformat(),)).fetchone()
 if row is None:
 raise ValueError(f"calendar row not found: {date_value.isoformat()}")
 return _row_to_calendar_context(row)

def calendar_sync(args: argparse.Namespace) -> None:
 emit(sync_calendar_year(args.db, args.year, args.seed_file))

def calendar_query(args: argparse.Namespace) -> None:
 context = get_calendar_day(args.db, args.date)
 emit({"status": "ok", **context, "approval_allowed": False})

def _load_json_file(path: str | None) -> dict[str, Any] | None:
 if not path:
 return None
 with open(path, "r", encoding="utf-8-sig") as handle:
 return json.load(handle)

def _canonical_weather_provider(provider: str) -> str:
 aliases = {
 "wttr_mcp": "wttr_http",
 "sample": "weather_fixture",
 "manual": "manual_weather",
 }
 return aliases.get(provider or "weather_mcp", provider or "weather_mcp")

def _weather_source_quality(provider: str) -> str:
 if provider == "weather_mcp":
 return "confirmed"
 if provider in {"wttr_http", "amap_api", "qweather_api"}:
 return "secondary"
 if provider == "weather_fixture":
 return "fixture"
 if provider == "manual_weather":
 return "manual"
 return "secondary"

def normalize_weather(payload: dict[str, Any] | None, provider: str = "weather_mcp") -> dict[str, Any]:
 provider = _canonical_weather_provider(provider)
 if not payload:
 summary = "天气 MCP 未配置或未返回。" if provider == "weather_mcp" else f"{provider} 天气源未配置或未返回。"
 return {
 "status": "unavailable",
 "source": provider,
 "weather_summary": summary,
 "weather_risk_level": "unknown",
 "source_quality": "unavailable",
 "field_quality": "missing",
 }
 if payload.get("status") in {"timeout", "error", "unavailable"}:
 return {
 "status": "unavailable",
 "source": provider,
 "weather_summary": payload.get("message") or f"{provider} 天气源超时或不可用。",
 "weather_risk_level": "unknown",
 "source_quality": "unavailable",
 "field_quality": "missing",
 }
 current = (payload.get("current_condition") or [{}])[0] if isinstance(payload.get("current_condition"), list) else payload
 desc = payload.get("weather_summary") or payload.get("description")
 if not desc:
 weather_desc = current.get("weatherDesc") or []
 if weather_desc and isinstance(weather_desc, list):
 desc = (weather_desc[0] or {}).get("value")
 temp = current.get("temp_C") or current.get("temperature")
 precip = current.get("precipMM") or current.get("precipitation")
 summary_parts = [str(desc or "天气已返回")]
 if temp not in (None, ""):
 summary_parts.append(f"{temp}C")
 weather_text = " ".join(summary_parts)
 risk = "low"
 text = weather_text.lower()
 try:
 precip_value = float(precip or 0)
 except (TypeError, ValueError):
 precip_value = 0.0
 if any(word in text for word in ("storm", "暴雨", "大雨", "snow", "雪", "雷")) or precip_value >= 10:
 risk = "high"
 elif any(word in text for word in ("rain", "雨", "fog", "雾", "阴")) or precip_value > 0:
 risk = "medium"
 return {
 "status": "ok",
 "source": provider,
 "weather_summary": weather_text,
 "weather_risk_level": risk,
 "source_quality": _weather_source_quality(provider),
 "field_quality": "confirmed" if desc else "inferred",
 "data_snapshot_time": now_local(),
 }

def _fresh_operating_context(payload: dict[str, Any] | None) -> tuple[bool, dict[str, Any]]:
 if not payload:
 return False, {"status": "missing", "freshness_status": "missing_date"}
 context = {
 "status": payload.get("status") or "ok",
 "freshness_status": payload.get("freshness_status"),
 "business_status": payload.get("business_status"),
 "data_business_date": payload.get("data_business_date"),
 "data_snapshot_time": payload.get("data_snapshot_time"),
 }
 fresh = context["freshness_status"] == "fresh" and context["business_status"] == "current"
 return fresh, context

def _fresh_progress_context(payload: dict[str, Any] | None) -> tuple[bool, dict[str, Any]]:
 if not payload:
 return False, {"status": "missing", "freshness_status": "missing_date", "downstream_allowed": False}
 context = {
 "status": payload.get("status") or "ok",
 "freshness_status": payload.get("freshness_status"),
 "business_status": payload.get("business_status"),
 "downstream_allowed": bool(payload.get("downstre
