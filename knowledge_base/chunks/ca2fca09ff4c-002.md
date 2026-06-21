# hotel--ota-ai 2/runtime/decisions/calendar.py

类型：项目资料
关键词：OTA

---

:
 season_tag = "holiday_peak"
 elif next_delta is not None and 0 < next_delta <= 3:
 season_tag = "holiday_warmup"
 elif prev_delta is not None and 0 < prev_delta <= 2:
 season_tag = "holiday_cooldown"
 elif month in {7, 8}:
 season_tag = "summer_vacation"
 elif month in {1, 2}:
 season_tag = "winter_vacation"
 else:
 season_tag = "normal"
 school_vacation_tag = "summer_vacation" if month in {7, 8} else "winter_vacation" if month in {1, 2} else "none"
 return {
 "weekday": weekday + 1,
 "is_weekend": is_weekend,
 "is_workday": is_workday,
 "is_holiday": is_holiday,
 "is_adjusted_workday": is_adjusted,
 "is_off_day": is_off_day,
 "season_tag": season_tag,
 "school_vacation_tag": school_vacation_tag,
 "demand_level": demand_level,
 "price_advice": price_advice,
 }

def build_calendar_days(year: int, seed_file: str | None = None) -> list[dict[str, Any]]:
 seed = load_holiday_seed(year, seed_file)
 start = dt.date(year, 1, 1)
 end = dt.date(year, 12, 31)
 holiday_dates = sorted(dt.date.fromisoformat(day) for day, item in seed.items() if item.get("is_holiday"))
 rows: list[dict[str, Any]] = []
 for date_value in _daterange(start, end):
 next_holiday = min((holiday for holiday in holiday_dates if holiday >= date_value), default=None)
 prev_holiday = max((holiday for holiday in holiday_dates if holiday <= date_value), default=None)
 next_delta = (next_holiday - date_value).days if next_holiday else None
 prev_delta = (date_value - prev_holiday).days if prev_holiday else None
 special = seed.get(date_value.isoformat())
 tags = _tags_for(date_value, special, next_delta, prev_delta)
 rows.append(
 {
 "date": date_value.isoformat(),
 "year": date_value.year,
 "month": date_value.month,
 "day": date_value.day,
 "days_to_holiday": next_delta,
 "days_after_holiday": prev_delta,
 "holiday_name": (special or {}).get("holiday_name"),
 "holiday_group": (special or {}).get("holiday_group"),
 "source_quality": "confirmed" if special else "computed",
 "source": (special or {}).get("source") or "runtime_date_algorithm",
 "updated_at": now_local(),
 **tags,
 }
 )
 return rows

def _ensure_calendar_tables(db_path: str) -> None:
 with closing(connect(db_path)) as conn:
 with conn:
 conn.executescript(
 """
 CREATE TABLE IF NOT EXISTS calendar_days (
 date TEXT PRIMARY KEY,
 year INTEGER NOT NULL,
 month INTEGER NOT NULL,
 day INTEGER NOT NULL,
 weekday INTEGER NOT NULL,
 is_weekend INTEGER NOT NULL,
 is_workday INTEGER NOT NULL,
 is_holiday INTEGER NOT NULL,
 is_adjusted_workday INTEGER NOT NULL,
 is_off_day INTEGER NOT NULL,
 holiday_name TEXT,
 holiday_group TEXT,
 days_to_holiday INTEGER,
 days_after_holiday INTEGER,
 season_tag TEXT NOT NULL,
 school_vacation_tag TEXT NOT NULL,
 local_event_count INTEGER NOT NULL DEFAULT 0,
 event_heat_level TEXT NOT NULL DEFAULT 'none',
 demand_level TEXT NOT NULL,
 price_advice TEXT NOT NULL,
 source_quality TEXT NOT NULL,
 source TEXT NOT NULL,
 updated_at TEXT NOT NULL
 );
 CREATE TABLE IF NOT EXISTS event_candidates (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 hotel_id TEXT NOT NULL,
 date TEXT NOT NULL,
 event_name TEXT NOT NULL,
 event_type TEXT,
 location TEXT,
 distance_km REAL,
 source_url TEXT,
 confidence REAL NOT NULL DEFAULT 0,
 expected_heat TEXT NOT NULL DEFAULT 'unknown',
 status TEXT NOT NULL DEFAULT 'candidate',
 created_at TEXT NOT NULL
 );
 """
 )

def sync_calendar_year(db_path: str, year: int, seed_file: str | None = None) -> dict[str, Any]:
 _ensure_calendar_tables(db_path)
 rows = build_calendar_days(year, seed_file)
 with closing(connect(db_path)) as conn:
 with conn:
 for row in rows:
 conn.execute(
 """
 INSERT INTO calendar_days (
 date, year, month, day, weekday, is_weekend, is_workday, is_holiday,
 is_adjusted_workday, is_off_day, holiday_name, holiday_group,
 days_to_holiday, days_after_holiday, season_tag, school_vacation_tag,
 local_event_count, event_heat_level, demand_level, price_advice,
 source_quality, source, updated_at
 )
 VALUES (
 :date, :year, :month, :day, :weekday, :is_weekend, :is_workday, :is_holiday,
 :is_adjusted_workday, :is_off_day, :holiday_name, :holiday_group,
 :days_to_holiday, :days_after_holiday, :season_tag, :school_vacation_tag,
 0, 'none', :demand_level, :price_advice,
 :source_quality, :source, :updated_at
 )
 ON CONFLICT(date) DO UPDATE SET
 year=excluded.year,
 month=excluded.month,
 day=excluded.day,
 weekday=excluded.weekday,
 is_weekend=excluded.is_weekend,
 is_workday=excluded.is_workday,
 is_holiday=excluded.is_holiday,
 is_adjusted_workday=excluded.is_adjusted_workday,
 is_off_day=excluded.is_off_day,
 holiday_name=excluded.holiday_name,
 holiday_group=excluded.holiday_group,
 days_to_holiday=excluded.days_to_holiday,
 days_after_holiday=excluded.days_after_holiday,
 season_tag=excluded.season_tag,
 school_vacation_tag=excluded.school_vacation_tag,
 demand_level=excluded.demand_level,
 price_advice=excluded.price_advice,
 source_quality=excluded.source_quality,
 source=excluded.source,
 updated_at=excluded.updated_at
 """,
 {ke
