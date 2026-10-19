import json
import html
import math
import re
import uuid
from datetime import date, datetime, time, timedelta, timezone as datetime_timezone
from pathlib import Path

import streamlit as st

DATA_FILE = Path("assignments.json")
CALENDAR_FILE = Path("calendar.ics")
DEFAULT_WAKE_START = time(7, 0)
DEFAULT_WAKE_END = time(23, 0)


COURSES = ["Course 1", "Course 2", "Course 3", "Other"]
COURSE_COLORS = {
    "Course 1": "#C8D6F2",
    "Course 2": "#BFE3E1",
    "Course 3": "#F3D0B5",
    "Other": "#E5DDD0",
}
APP_THEME_DEFAULTS = {
    "background": "#E8DBC7",
    "sidebar": "#DDCBB1",
    "text": "#40392F",
    "button": "#76553F",
    "button_text": "#FFF8ED",
    "card": "#D7C2A6",
    "card_text": "#493D31",
    "input": "#FFFDF8",
    "border": "#B89C7B",
    "surface": "#F4EADB",
}
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DEFAULT_COURSE_MEETING_DAYS = {}


def infer_course(name):
    text = str(name).casefold()
    for course_name in COURSES:
        if course_name != "Other" and course_name.casefold() in text:
            return course_name
    return "Other" if "Other" in COURSE_COLORS else next(iter(COURSE_COLORS))

st.set_page_config(page_title="Assignment Planner", page_icon="📚", layout="wide")


st.markdown("""
<style>
    .stApp { background: #e8dbc7; color: #40392f; }
    [data-testid="stAppViewContainer"] { background: #e8dbc7; }
    [data-testid="stHeader"] { background: rgba(232,219,199,0.96); }
    [data-testid="stSidebar"] { background: #ddcbb1; border-right: 1px solid #c7af91; }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1180px; }
    h1, h2, h3, h4, p, label, span, div { letter-spacing: -0.015em; }
    h1, h2, h3 { color: #433c32; letter-spacing: -0.035em; }
    [data-testid="stMarkdownContainer"] { color: #4b4035; }
    [data-testid="stCaptionContainer"] { color: #776553; }
    [data-testid="stWidgetLabel"] p, .stApp label, .stApp p { color: #4b443a; }
    [data-testid="stAlert"] { background: #f2e6d5; border-color: #d5c0a2; color: #4b4035; }
    div[data-testid="stProgress"] > div > div { background: #b9d8bd; }
    .stApp button[kind="primary"] { background: #76553f; border-color: #684a36; color: #fff8ed; }
    .stApp button[kind="secondary"] { background: #e2d1b8; border-color: #cbb391; color: #4b4035; }
    div[data-testid="stMetric"] {
        background: #624837; border: 1px solid #7b5c43;
        padding: 16px 18px; border-radius: 14px;
    }
    div[data-testid="stMetricLabel"] { color: #eadbc6; }
    div[data-testid="stMetricValue"] { color: #fff8ed; font-weight: 750; }
    div[data-testid="stTabs"] button { font-weight: 650; }
    div[data-testid="stTabs"] button p { color: #655c50; }
    div[data-testid="stForm"] {
        background: #f4eadb; border: 1px solid #d6c2a7;
        border-radius: 14px; padding: 14px 16px;
    }
    [data-testid="stFileUploaderDropzone"] {
        background: #f1e5d3 !important; border: 1px dashed #b99e7d !important;
    }
    [data-testid="stFileUploaderDropzone"] * { color: #564839 !important; }
    [data-testid="stFileUploaderDropzone"] button {
        background: #e2d1b8 !important; color: #574535 !important;
        border-color: #c5aa88 !important;
    }
    [data-testid="stFileUploader"] section { background: transparent !important; }
    /* Style the outer BaseWeb shell once. Styling its nested base-input too
       creates the clipped inner white rectangle and dark double borders. */
    .stApp [data-testid="stTextInput"] [data-baseweb="input"],
    .stApp [data-testid="stNumberInput"] [data-baseweb="input"],
    .stApp [data-testid="stDateInput"] [data-baseweb="input"],
    .stApp [data-testid="stTimeInput"] [data-baseweb="input"],
    .stApp [data-testid="stTextArea"] [data-baseweb="textarea"],
    .stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    .stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        background: #fffdf8 !important;
        color: #453e34 !important;
        border: 1px solid #c8b393 !important;
        border-radius: 11px !important;
        box-shadow: none !important;
        outline: 0 !important;
        overflow: hidden;
        color-scheme: light;
    }
    .stApp [data-testid="stTextInput"] [data-baseweb="base-input"],
    .stApp [data-testid="stNumberInput"] [data-baseweb="base-input"],
    .stApp [data-testid="stDateInput"] [data-baseweb="base-input"],
    .stApp [data-testid="stTimeInput"] [data-baseweb="base-input"] {
        background: transparent !important;
        border: 0 !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        outline: 0 !important;
    }
    .stApp [data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
    .stApp [data-testid="stNumberInput"] [data-baseweb="input"]:focus-within,
    .stApp [data-testid="stDateInput"] [data-baseweb="input"]:focus-within,
    .stApp [data-testid="stTimeInput"] [data-baseweb="input"]:focus-within,
    .stApp [data-testid="stTextArea"] [data-baseweb="textarea"]:focus-within,
    .stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
    .stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within {
        border-color: #a88b69 !important;
        box-shadow: 0 0 0 2px rgba(168, 139, 105, .16) !important;
    }
    .stApp [data-testid="stTextInput"] input,
    .stApp [data-testid="stNumberInput"] input,
    .stApp [data-testid="stDateInput"] input,
    .stApp [data-testid="stTimeInput"] input,
    .stApp [data-testid="stTextArea"] textarea,
    .stApp [data-testid="stMultiSelect"] input {
        background: #fffdf8 !important;
        color: #453e34 !important;
        border: 0 !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        outline: 0 !important;
        -webkit-appearance: none !important;
        appearance: none !important;
        color-scheme: light;
    }
    /* Streamlit/BaseWeb renders the visible value in nested elements for
       select and date controls, so give those inner surfaces the same cream
       fill as the input itself. Only the fill changes; borders and shape stay
       defined by the control rules above. */
    .stApp [data-testid="stSelectbox"] [data-baseweb="select"] div,
    .stApp [data-testid="stMultiSelect"] [data-baseweb="select"] div,
    .stApp [data-testid="stDateInput"] [data-baseweb="input"] div,
    .stApp [data-testid="stDateInput"] [data-baseweb="input"] input {
        background-color: #fffdf8 !important;
    }
    .stApp [data-testid="stNumberInput"] input { text-align: center; }
    .stApp [data-testid="stNumberInput"] button,
    .stApp [data-testid="stTimeInput"] button {
        background: #f1e6d5 !important;
        color: #574535 !important;
        border: 0 !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        outline: 0 !important;
    }
    .stApp [data-testid="stNumberInput"] button:hover,
    .stApp [data-testid="stTimeInput"] button:hover { background: #e9dbc5 !important; }
    .stApp [data-testid="stMultiSelect"] [data-baseweb="tag"] {
        background: #e9dfcf !important; color: #514333 !important;
        border-radius: 8px !important;
    }
    .stApp [data-testid="stDateInput"] button {
        color: #69563f !important; border: 0 !important;
        background: transparent !important; box-shadow: none !important;
    }
    .stApp [data-testid="stForm"] button,
    .stApp [data-testid="stSidebar"] button {
        background: #e2d1b8 !important;
        color: #514333 !important;
        border-color: #c5aa88 !important;
        box-shadow: none !important;
    }
    .stApp [data-baseweb="popover"] [role="listbox"],
    .stApp [data-baseweb="popover"] [role="option"] {
        background: #fffdf8 !important;
        color: #453e34 !important;
    }
    .stApp [data-baseweb="popover"] [data-testid="stDatePicker"] *,
    .stApp [data-baseweb="popover"] [data-testid="stTimePicker"] * {
        color: #453e34 !important;
    }
    .stApp [data-baseweb="popover"] [role="option"]:hover,
    .stApp [data-baseweb="popover"] [aria-selected="true"] {
        background: #efe3d1 !important;
        color: #453e34 !important;
    }
    .stApp input[type="checkbox"], .stApp input[type="radio"] { accent-color: #8c7154; color-scheme: light; }
    .stApp [data-testid="stSlider"] [role="slider"] { background: #8c7154 !important; }
    .stApp [data-testid="stExpander"] details,
    .stApp [data-testid="stExpander"] summary,
    .stApp [data-testid="stExpander"] summary:hover {
        background: #d7c2a6 !important;
        color: #514333 !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #d7c2a6 !important; border: 1px solid #b89c7b !important;
        border-radius: 15px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div { background: transparent !important; border-color: transparent !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"],
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"],
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stWidgetLabel"] p { color: #514333 !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"],
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"] { color: #514333 !important; }
    div[data-testid="stExpander"] { background: #d7c2a6; border: 1px solid #b89c7b; border-radius: 13px; }
    div[data-testid="stExpander"] summary, div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] [data-testid="stMarkdownContainer"] { color: #514333 !important; }
    .assignment-card {
        border: 1px solid #b89c7b; border-radius: 16px;
        background: linear-gradient(145deg, #d7c2a6, #cdb391);
        padding: 17px 18px; margin: 0 0 8px 0; min-height: 220px;
    }
    .assignment-card.due-today {
        border: 3px solid #c96f59;
        box-shadow: 0 0 0 1px rgba(201,111,89,.18), 0 7px 20px rgba(113,66,49,.16);
    }
    .due-today-tag {
        display: inline-block; color: #6a3f36; border: 1px solid #e5b7ad;
        background: #f8e5df; border-radius: 999px;
        padding: 3px 9px; font-size: .72rem; font-weight: 800;
        letter-spacing: .06em; text-transform: uppercase; margin-left: 8px;
        vertical-align: middle;
    }
    .target-line { display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }

    .assignment-title {
        display: inline-block; color: #493d31; font-size: 1.22rem;
        line-height: 1.35; font-weight: 750; padding: 9px 15px;
        border-radius: 10px; margin-bottom: 12px;
        overflow-wrap: anywhere;
    }
    .target-label {
        color: #6b5845; text-transform: uppercase; letter-spacing: .11em;
        font-size: .78rem; font-weight: 750; margin-top: 2px;
    }
    .target-number {
        color: #493d31; font-size: 2.65rem; line-height: 1.12;
        font-weight: 850; letter-spacing: -.05em; margin: 4px 0 5px 0;
    }
    .target-unit { color: #6b5845; font-size: 1.35rem; font-weight: 700; letter-spacing: -.02em; }
    .assignment-meta { color: #6b5845; font-size: .9rem; margin-top: 7px; }
    .historical-progress {
        display: inline-flex; margin-top: 10px; padding: 5px 10px;
        border: 1px solid #b89c7b; border-radius: 999px;
        background: #e6d5bc; color: #554434; font-size: .8rem;
    }
    .today-progress-label { color: #5c4b3b; font-size: .88rem; font-weight: 650; }
    div[data-testid="stVerticalBlock"] > div:has(> .assignment-card) { gap: .35rem; }
    @media (max-width: 700px) {
        .target-number { font-size: 2.1rem; }
        .assignment-card { padding: 14px; }
    }
</style>
""", unsafe_allow_html=True)


def load_data():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            st.error("Could not read assignments.json. Make a backup before replacing it.")
    return {"assignments": [], "calendar_events": [], "calendar_name": None, "daily_availability_overrides": {}}


def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _calendar_datetime(value):
    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime.combine(value, time.min)
    if value.tzinfo is not None:
        return value.astimezone().replace(tzinfo=None)
    return value


def _recurrence_datetime(value, timezone=None):
    if isinstance(value, date) and not isinstance(value, datetime):
        value = datetime.combine(value, time.min)
    if timezone is not None and value.tzinfo is None:
        if hasattr(timezone, "localize"):
            return timezone.localize(value)
        return value.replace(tzinfo=timezone)
    return value


def _recurrence_values(component, property_name):
    values = component.get(property_name)
    if values is None:
        return []
    properties = values if isinstance(values, (list, tuple)) else [values]
    dates = []
    for prop in properties:
        entries = getattr(prop, "dts", None)
        if entries is None:
            entries = [prop]
        for entry in entries:
            value = getattr(entry, "dt", entry)
            if isinstance(value, tuple):
                value = value[0]
            dates.append(value)
    return dates


def _recurrence_rule_text(recurrence_rule, recurrence_start):
    rule_text = recurrence_rule.to_ical().decode("utf-8")
    timezone = recurrence_start.tzinfo
    if timezone is None:
        return rule_text

    normalized_parts = []
    for part in rule_text.split(";"):
        name, separator, value = part.partition("=")
        if separator and name.upper() == "UNTIL" and not value.endswith("Z"):
            if len(value) == 8:
                local_until = datetime.strptime(value, "%Y%m%d").replace(
                    hour=23, minute=59, second=59
                )
            else:
                local_until = datetime.strptime(value, "%Y%m%dT%H%M%S")
            if hasattr(timezone, "localize"):
                local_until = timezone.localize(local_until)
            else:
                local_until = local_until.replace(tzinfo=timezone)
            utc_until = local_until.astimezone(datetime_timezone.utc)
            value = utc_until.strftime("%Y%m%dT%H%M%SZ")
            part = f"{name}={value}"
        normalized_parts.append(part)
    return ";".join(normalized_parts)


def parse_ics(uploaded_file):
    """Return busy event intervals as local-naive datetimes."""
    try:
        from icalendar import Calendar
        from dateutil.rrule import rruleset, rrulestr
    except ImportError as exc:
        raise RuntimeError("A calendar package is missing. Run: pip install -r requirements.txt") from exc

    calendar = Calendar.from_ical(uploaded_file.getvalue())
    components = [item for item in calendar.walk() if item.name == "VEVENT"]
    recurrence_exceptions = {}
    for component in components:
        recurrence_id = component.get("RECURRENCE-ID")
        uid = component.get("UID")
        if recurrence_id is not None and uid is not None:
            recurrence_exceptions.setdefault(str(uid), []).append(recurrence_id.dt)

    events = []
    expansion_today = date.today()
    expansion_end = expansion_today + timedelta(days=365)
    for component in components:
        # Ignore events explicitly marked FREE.
        transp = str(component.get("TRANSP", "OPAQUE")).upper()
        status = str(component.get("STATUS", "")).upper()
        if transp == "TRANSPARENT" or status == "CANCELLED":
            continue

        start_prop = component.get("DTSTART")
        end_prop = component.get("DTEND")
        if not start_prop:
            continue

        start_value = start_prop.dt
        recurrence_start = _recurrence_datetime(start_value)
        if end_prop:
            end_value = end_prop.dt
        elif isinstance(start_value, date) and not isinstance(start_value, datetime):
            end_value = start_value + timedelta(days=1)
        else:
            end_value = start_value + timedelta(hours=1)

        start_dt = _calendar_datetime(start_value)
        end_dt = _calendar_datetime(end_value)
        duration = end_dt - start_dt
        if duration <= timedelta(0):
            continue

        summary = str(component.get("SUMMARY", "Busy"))

        def add_event(instance_start):
            instance_end = instance_start + duration
            local_start = _calendar_datetime(instance_start)
            local_end = _calendar_datetime(instance_end)
            if local_end > local_start:
                events.append({
                    "start": local_start.isoformat(),
                    "end": local_end.isoformat(),
                    "summary": summary,
                })

        recurrence_rule = component.get("RRULE")
        recurrence_dates = _recurrence_values(component, "RDATE")
        if recurrence_rule is None and not recurrence_dates:
            add_event(start_value)
            continue

        recurrence_set = rruleset()
        if recurrence_rule is not None:
            try:
                rule_text = _recurrence_rule_text(recurrence_rule, recurrence_start)
                recurrence_set.rrule(rrulestr(rule_text, dtstart=recurrence_start))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Could not read recurring calendar event '{summary}': {exc}") from exc
        else:
            recurrence_set.rdate(recurrence_start)

        timezone = recurrence_start.tzinfo
        for recurrence_value in recurrence_dates:
            recurrence_set.rdate(_recurrence_datetime(recurrence_value, timezone))
        for excluded_value in _recurrence_values(component, "EXDATE"):
            recurrence_set.exdate(_recurrence_datetime(excluded_value, timezone))
        uid = component.get("UID")
        if uid is not None:
            for excluded_value in recurrence_exceptions.get(str(uid), []):
                recurrence_set.exdate(_recurrence_datetime(excluded_value, timezone))

        if timezone is not None:
            now_in_event_timezone = datetime.now(timezone).date()
            range_start_date = now_in_event_timezone - timedelta(days=1)
            range_end_date = now_in_event_timezone + timedelta(days=365)

            def recurrence_bound(day):
                bound = datetime.combine(day, time.min)
                if hasattr(timezone, "localize"):
                    return timezone.localize(bound)
                return bound.replace(tzinfo=timezone)
        else:
            range_start_date = expansion_today - timedelta(days=1)
            range_end_date = expansion_end

            def recurrence_bound(day):
                return datetime.combine(day, time.min)

        recurrence_instances = recurrence_set.between(
            recurrence_bound(range_start_date),
            recurrence_bound(range_end_date),
            inc=True,
        )
        for instance_start in recurrence_instances:
            add_event(instance_start)
    return events


def normalize_imported_assignments(payload, today):
    """Accept either a list of assignments or an object containing an assignments list."""
    rows = payload.get("assignments", []) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("JSON must be a list of assignments or an object with an 'assignments' list.")

    normalized = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"Assignment #{index} must be an object.")
        name = str(row.get("name", "")).strip()
        if not name:
            raise ValueError(f"Assignment #{index} is missing a name.")

        total = int(row.get("total_units", row.get("questions", 0)))
        completed = int(row.get("completed_units", row.get("done", 0)))
        due_raw = row.get("due_date", row.get("due"))
        if not due_raw:
            raise ValueError(f"Assignment '{name}' is missing due_date (YYYY-MM-DD).")
        if isinstance(due_raw, date):
            due_iso = due_raw.isoformat()
        else:
            due_iso = date.fromisoformat(str(due_raw)).isoformat()

        unit = str(row.get("unit", "Questions")).strip() or "Questions"
        if total < 1 or completed < 0 or completed > total:
            raise ValueError(f"Assignment '{name}' has invalid total/completed values.")

        course = str(row.get("course", infer_course(name))).strip()
        if course not in COURSES:
            course = "Other" if "Other" in COURSES else COURSES[0]

        normalized.append({
            "id": str(uuid.uuid4()),
            "name": name,
            "course": course,
            "mode": "units",
            "start_date": today.isoformat(),
            "total_units": total,
            "unit": unit,
            "due_date": due_iso,
            "completed_units": completed,
            "today_completed": 0,
            "today_date": today.isoformat(),
        })
    return normalized


def merge_intervals(intervals, max_gap_minutes=30):
    """Merge overlapping/nearby busy events. Short gaps are not counted as free."""
    if not intervals:
        return []
    intervals = sorted(intervals, key=lambda item: item[0])
    merged = [list(intervals[0])]
    for start, end in intervals[1:]:
        previous_end = merged[-1][1]
        gap = (start - previous_end).total_seconds() / 60
        if gap <= max_gap_minutes:
            merged[-1][1] = max(previous_end, end)
        else:
            merged.append([start, end])
    return [(start, end) for start, end in merged]


def daily_calendar_free_hours(day, events, wake_start, wake_end, ignore_gap_minutes):
    day_start = datetime.combine(day, wake_start)
    day_end = datetime.combine(day, wake_end)
    intervals = []
    for event in events:
        start = datetime.fromisoformat(event["start"])
        end = datetime.fromisoformat(event["end"])
        if end > day_start and start < day_end:
            intervals.append((max(start, day_start), min(end, day_end)))

    merged = merge_intervals(intervals, ignore_gap_minutes)
    free_minutes = 0
    cursor = day_start
    for start, end in merged:
        if start > cursor:
            free_minutes += (start - cursor).total_seconds() / 60
        cursor = max(cursor, end)
    if cursor < day_end:
        free_minutes += (day_end - cursor).total_seconds() / 60
    return max(0.0, free_minutes / 60)


def get_calendar_estimate_hours(day, settings, events, has_calendar):
    """Estimate free hours from the imported calendar, or use a default without one."""
    if has_calendar:
        return daily_calendar_free_hours(
            day, events, settings["wake_start"], settings["wake_end"],
            settings["ignore_gap_minutes"]
        )
    return settings["weekday_fallback"] if day.weekday() < 5 else settings["weekend_fallback"]


def get_daily_availability_hours(day, settings, events, has_calendar):
    """Use a date-specific manual value when one exists; otherwise use the estimate."""
    overrides = settings.get("daily_availability", {})
    key = day.isoformat()
    if key in overrides:
        return max(0.0, float(overrides[key]))
    return get_calendar_estimate_hours(day, settings, events, has_calendar)


def build_schedule(assignments, settings, events, has_calendar, today=None):
    """Spread remaining units or percentage points across available days."""
    today = today or date.today()
    active_assignments = [
        a for a in assignments
        if (float(a.get("remaining_percent", 0)) > 0 if a.get("mode") == "percentage"
            else int(a.get("remaining_units", 0)) > 0)
    ]
    end_date = max(
        [date.fromisoformat(a["due_date"]) for a in active_assignments] or [today]
    )

    days = []
    current = today
    while current <= end_date:
        hours = get_daily_availability_hours(current, settings, events, has_calendar)
        # Distribute work directly in proportion to available hours.
        weight = max(0.0, hours)
        days.append({"date": current, "availability_weight": weight, "free_hours": hours})
        current += timedelta(days=1)

    plan = {d["date"].isoformat(): [] for d in days}

    # Assign earlier deadlines first. Rounding each day's share UP deliberately
    # creates a small buffer and tends to finish work before its due date.
    for assignment in sorted(assignments, key=lambda a: (a["due_date"], a["name"].lower())):
        is_percentage = assignment.get("mode") == "percentage"
        remaining = max(0.0, float(assignment.get("remaining_percent", 0))) if is_percentage else max(0, int(assignment.get("remaining_units", 0)))
        due = date.fromisoformat(assignment["due_date"])
        start = date.fromisoformat(assignment.get("start_date", today.isoformat()))

        # If some progress was recorded today, schedule the rest from tomorrow.
        today_done = float(assignment.get("today_completed", 0))
        first_day = today + timedelta(days=1) if today_done > 0 else max(today, start)
        eligible = [
            d for d in days
            if first_day <= d["date"] <= due and d["availability_weight"] > 0
        ]
        total_weight = sum(d["availability_weight"] for d in eligible)

        if remaining > 0 and eligible and total_weight > 0:
            if is_percentage:
                # Allocate whole percentage points, with rounding balanced across days.
                shares = [remaining * d["availability_weight"] / total_weight for d in eligible]
                targets = [int(math.floor(value)) for value in shares]
                points_left = int(round(remaining)) - sum(targets)
                order = sorted(range(len(shares)), key=lambda i: shares[i] - targets[i], reverse=True)
                for index in order[:max(0, points_left)]:
                    targets[index] += 1
                for day_info, target in zip(eligible, targets):
                    if target > 0:
                        plan[day_info["date"].isoformat()].append({
                            "assignment_id": assignment["id"], "name": assignment["name"],
                            "percent": target, "mode": "percentage",
                        })
                remaining = max(0.0, remaining - sum(targets))
            else:
                for day_info in eligible:
                    if remaining <= 0:
                        break
                    ideal_share = int(assignment["remaining_units"]) * day_info["availability_weight"] / total_weight
                    target = min(remaining, max(1, math.ceil(ideal_share)))
                    plan[day_info["date"].isoformat()].append({
                        "assignment_id": assignment["id"], "name": assignment["name"],
                        "units": target, "unit": assignment["unit"], "mode": "units",
                    })
                    remaining -= target

        assignment["unscheduled_percent" if is_percentage else "unscheduled_units"] = remaining

    return plan, days


data = load_data()
data.setdefault("assignments", [])
data.setdefault("calendar_events", [])
data.setdefault("calendar_name", None)
saved_categories = data.get("course_categories")
if not isinstance(saved_categories, dict) or not saved_categories:
    saved_categories = dict(COURSE_COLORS)
data["course_categories"] = {
    str(name).strip(): str(color)
    for name, color in saved_categories.items()
    if str(name).strip()
}
if not data["course_categories"]:
    data["course_categories"] = dict(COURSE_COLORS)
COURSE_COLORS.clear()
COURSE_COLORS.update(data["course_categories"])
COURSES[:] = list(COURSE_COLORS)
saved_class_topics = data.get("class_topics", {})
if not isinstance(saved_class_topics, dict):
    saved_class_topics = {}
data["class_topics"] = saved_class_topics
for saved_course, saved_topics in list(data["class_topics"].items()):
    normalized_topics = []
    if isinstance(saved_topics, list):
        for saved_topic in saved_topics:
            if isinstance(saved_topic, str) and saved_topic.strip():
                normalized_topics.append({"id": str(uuid.uuid4()), "name": saved_topic.strip()})
            elif isinstance(saved_topic, dict) and str(saved_topic.get("name", "")).strip():
                normalized_topic = {
                    "id": str(saved_topic.get("id") or uuid.uuid4()),
                    "name": str(saved_topic["name"]).strip(),
                }
                saved_class_date = saved_topic.get("class_date")
                try:
                    normalized_topic["class_date"] = date.fromisoformat(str(saved_class_date)).isoformat()
                except (TypeError, ValueError):
                    pass
                normalized_topics.append(normalized_topic)
    data["class_topics"][saved_course] = normalized_topics
for course_name in COURSES:
    data["class_topics"].setdefault(course_name, [])
saved_meeting_days = data.get("course_meeting_days", {})
if not isinstance(saved_meeting_days, dict):
    saved_meeting_days = {}
data["course_meeting_days"] = {
    course_name: [
        weekday for weekday in saved_meeting_days.get(
            course_name, DEFAULT_COURSE_MEETING_DAYS.get(course_name, [])
        )
        if weekday in WEEKDAY_NAMES
    ]
    for course_name in COURSE_COLORS
}
if not isinstance(data.get("lecture_tasks"), list):
    data["lecture_tasks"] = []
saved_theme = data.get("app_theme")
if not isinstance(saved_theme, dict):
    saved_theme = {}
app_theme = dict(APP_THEME_DEFAULTS)
for theme_key, theme_value in saved_theme.items():
    if theme_key in app_theme and isinstance(theme_value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", theme_value):
        app_theme[theme_key] = theme_value.upper()
data["app_theme"] = dict(app_theme)
if st.session_state.pop("reset_app_theme_pending", False):
    for theme_widget_key in (
        "theme_background", "theme_sidebar", "theme_text", "theme_border",
        "theme_button", "theme_button_text", "theme_card", "theme_card_text",
        "theme_input", "theme_surface",
    ):
        st.session_state.pop(theme_widget_key, None)
data.setdefault("planner_settings", {})

st.markdown(f"""
<style>
    .stApp, [data-testid="stAppViewContainer"] {{
        background: {app_theme['background']} !important;
        color: {app_theme['text']} !important;
    }}
    [data-testid="stHeader"] {{ background: {app_theme['background']} !important; }}
    [data-testid="stSidebar"] {{
        background: {app_theme['sidebar']} !important;
        border-right-color: {app_theme['border']} !important;
    }}
    h1, h2, h3, h4, .stApp p, .stApp label,
    [data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"],
    [data-testid="stWidgetLabel"] p,
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"],
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"],
    .stApp [data-testid="stExpander"] summary,
    .stApp [data-testid="stExpander"] summary p {{ color: {app_theme['text']} !important; }}
    [data-testid="stForm"], [data-testid="stAlert"],
    [data-testid="stFileUploaderDropzone"],
    div[data-testid="stExpander"],
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {app_theme['surface']} !important;
        border-color: {app_theme['border']} !important;
    }}
    .stApp button, .stApp [data-testid="stFormSubmitButton"] button {{
        background: {app_theme['button']} !important;
        color: {app_theme['button_text']} !important;
        border-color: {app_theme['border']} !important;
    }}
    .stApp input[type="checkbox"], .stApp input[type="radio"],
    .stApp [data-testid="stSlider"] [role="slider"] {{ accent-color: {app_theme['button']} !important; }}
    .stApp [data-testid="stNumberInput"] button,
    .stApp [data-testid="stTimeInput"] button,
    .stApp [data-testid="stDateInput"] button {{
        background: {app_theme['surface']} !important;
        color: {app_theme['text']} !important;
    }}
    .stApp [data-testid="stTextInput"] [data-baseweb="input"],
    .stApp [data-testid="stNumberInput"] [data-baseweb="input"],
    .stApp [data-testid="stDateInput"] [data-baseweb="input"],
    .stApp [data-testid="stTimeInput"] [data-baseweb="input"],
    .stApp [data-testid="stTextArea"] [data-baseweb="textarea"],
    .stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    .stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
    .stApp [data-testid="stTextInput"] input,
    .stApp [data-testid="stNumberInput"] input,
    .stApp [data-testid="stDateInput"] input,
    .stApp [data-testid="stTimeInput"] input,
    .stApp [data-testid="stTextArea"] textarea,
    .stApp [data-testid="stSelectbox"] [data-baseweb="select"] div,
    .stApp [data-testid="stMultiSelect"] [data-baseweb="select"] div,
    .stApp [data-testid="stDateInput"] [data-baseweb="input"] div {{
        background-color: {app_theme['input']} !important;
        color: {app_theme['text']} !important;
        border-color: {app_theme['border']} !important;
    }}
    .stApp [data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
    .stApp [data-testid="stNumberInput"] [data-baseweb="input"]:focus-within,
    .stApp [data-testid="stDateInput"] [data-baseweb="input"]:focus-within,
    .stApp [data-testid="stTimeInput"] [data-baseweb="input"]:focus-within,
    .stApp [data-testid="stTextArea"] [data-baseweb="textarea"]:focus-within,
    .stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
    .stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within {{
        border-color: {app_theme['button']} !important;
    }}
    .stApp [data-baseweb="popover"] [role="listbox"],
    .stApp [data-baseweb="popover"] [role="option"] {{
        background: {app_theme['input']} !important;
        color: {app_theme['text']} !important;
    }}
    .stApp [data-baseweb="popover"] [role="option"]:hover,
    .stApp [data-baseweb="popover"] [aria-selected="true"] {{
        background: {app_theme['surface']} !important;
        color: {app_theme['text']} !important;
    }}
    .assignment-card {{
        background: {app_theme['card']} !important;
        border-color: {app_theme['border']} !important;
        color: {app_theme['card_text']} !important;
    }}
    .assignment-card.due-today {{ border-color: #C96F59 !important; }}
    .assignment-card .target-number, .assignment-card .target-unit,
    .assignment-card .target-label, .assignment-card .assignment-meta,
    .assignment-card .historical-progress {{ color: {app_theme['card_text']} !important; }}
    .assignment-card .historical-progress {{
        background: {app_theme['surface']} !important;
        border-color: {app_theme['border']} !important;
    }}
</style>
""", unsafe_allow_html=True)

try:
    saved_wake_start = time.fromisoformat(data["planner_settings"].get("wake_start", DEFAULT_WAKE_START.isoformat()))
except (TypeError, ValueError):
    saved_wake_start = DEFAULT_WAKE_START
try:
    saved_wake_end = time.fromisoformat(data["planner_settings"].get("wake_end", DEFAULT_WAKE_END.isoformat()))
except (TypeError, ValueError):
    saved_wake_end = DEFAULT_WAKE_END

st.title("Assignment Planner")
st.caption("A local study planner that uses your exported calendar and dynamically redistributes work.")

with st.sidebar:
    st.header("Calendar")
    calendar_upload = st.file_uploader("Upload Google Calendar export (.ics)", type=["ics"])
    if calendar_upload is not None:
        try:
            parsed = parse_ics(calendar_upload)
            data["calendar_events"] = parsed
            data["calendar_name"] = calendar_upload.name
            data["calendar_recurrence_version"] = 2
            save_data(data)
            st.success(
                f"Imported {len(parsed)} calendar event occurrence(s), including recurring events."
            )
        except Exception as exc:
            st.error(str(exc))

    if data["calendar_name"]:
        st.caption(f"Current calendar: {data['calendar_name']}")
        if data.get("calendar_recurrence_version") != 2:
            st.warning(
                "Re-upload this calendar file once to include recurring classes in availability estimates."
            )
        if st.button("Remove imported calendar"):
            data["calendar_events"] = []
            data["calendar_name"] = None
            data.pop("calendar_recurrence_version", None)
            save_data(data)
            st.rerun()
    else:
        st.info("No calendar imported. The app will use your fallback availability settings.")

    st.divider()
    with st.expander("Availability settings", expanded=False):
        weekday_fallback = st.number_input(
            "Default weekday free hours (no calendar)", 0.0, 24.0,
            float(data["planner_settings"].get("weekday_fallback", 4.0)), 0.5,
        )
        weekend_fallback = st.number_input(
            "Default weekend free hours (no calendar)", 0.0, 24.0,
            float(data["planner_settings"].get("weekend_fallback", 6.0)), 0.5,
        )
        ignore_gap = st.number_input(
            "Ignore calendar gaps up to (minutes)", 0, 120,
            int(data["planner_settings"].get("ignore_gap_minutes", 30)), 5,
        )
        st.caption(
            "Recurring calendar events are expanded for the next year. Gaps up to "
            f"{ignore_gap:g} minutes are counted as part of class time."
        )
        wake_start = st.time_input("Waking day starts", saved_wake_start)
        wake_end = st.time_input("Waking day ends", saved_wake_end)

settings = {
    "weekday_fallback": weekday_fallback,
    "weekend_fallback": weekend_fallback,
    "ignore_gap_minutes": ignore_gap,
    "wake_start": wake_start,
    "wake_end": wake_end,
}
data["planner_settings"] = {
    "weekday_fallback": weekday_fallback,
    "weekend_fallback": weekend_fallback,
    "ignore_gap_minutes": ignore_gap,
    "wake_start": wake_start.isoformat(timespec="minutes"),
    "wake_end": wake_end.isoformat(timespec="minutes"),
}
save_data(data)

# Date-by-date availability estimates and manual overrides.
data.setdefault("daily_availability_overrides", {})
today_for_availability = date.today()
due_dates = []
for assignment in data.get("assignments", []):
    try:
        due_dates.append(date.fromisoformat(assignment["due_date"]))
    except (KeyError, TypeError, ValueError):
        pass
last_availability_day = max(
    [d for d in due_dates if d >= today_for_availability]
    or [today_for_availability + timedelta(days=13)]
)
last_availability_day = min(last_availability_day, today_for_availability + timedelta(days=59))

daily_availability = {}
with st.sidebar:
    with st.expander("Daily availability · inspect and edit", expanded=True):
        st.caption(
            "Estimate is free time inside your waking hours after calendar events. "
            "Edit 'Your hours' for any date to override it."
        )
        if st.button("Reset all dates to estimates", key="reset_daily_availability"):
            data["daily_availability_overrides"] = {}
            for state_key in list(st.session_state):
                if state_key.startswith("daily_hours_"):
                    del st.session_state[state_key]
            save_data(data)
            st.rerun()

        header = st.columns([1.45, 0.85, 1.0, 0.42])
        header[0].markdown("**Date**")
        header[1].markdown("**Estimate**")
        header[2].markdown("**Your hours**")
        current_day = today_for_availability
        while current_day <= last_availability_day:
            day_key = current_day.isoformat()
            estimate = get_calendar_estimate_hours(
                current_day, settings, data["calendar_events"], bool(data["calendar_name"])
            )
            saved_value = data["daily_availability_overrides"].get(day_key)
            initial_value = float(saved_value) if saved_value is not None else round(estimate, 1)
            row = st.columns([1.45, 0.85, 1.0, 0.42])
            row[0].write(current_day.strftime("%a %b ") + str(current_day.day))
            row[1].write(f"{estimate:.1f} h")
            chosen_value = row[2].number_input(
                f"Available hours on {day_key}",
                min_value=0.0, max_value=24.0,
                value=min(24.0, max(0.0, initial_value)),
                step=0.5, key=f"daily_hours_{day_key}",
                label_visibility="collapsed",
            )
            if saved_value is not None and row[3].button(
                "↺", key=f"reset_daily_hours_{day_key}",
                help="Reset this date to its calendar estimate",
            ):
                data["daily_availability_overrides"].pop(day_key, None)
                st.session_state.pop(f"daily_hours_{day_key}", None)
                save_data(data)
                st.rerun()
            if abs(float(chosen_value) - float(estimate)) > 0.01:
                daily_availability[day_key] = float(chosen_value)
            current_day += timedelta(days=1)

data["daily_availability_overrides"] = daily_availability
settings["daily_availability"] = daily_availability
save_data(data)

if wake_end <= wake_start:
    st.error("The waking-day end must be later than the waking-day start.")
    st.stop()

today = date.today()

# Create class-prep tasks for the next lecture and notes-review tasks for the
# previous lecture. Unfinished tasks roll forward without recreating history.
lecture_tasks_by_key = {
    task.get("id"): task for task in data["lecture_tasks"]
    if isinstance(task, dict) and task.get("id")
}
for course_name, meeting_days in data["course_meeting_days"].items():
    # Generate a short rolling window so Schedule can show upcoming work too.
    for day_offset in range(-1, 22):
        class_date = today + timedelta(days=day_offset)
        if class_date.strftime("%A") not in meeting_days:
            continue
        for task_type, due_date in (
            ("lecture_prep", class_date - timedelta(days=1)),
            ("lecture_notes_review", class_date + timedelta(days=1)),
        ):
            if due_date < today:
                continue
            task_id = f"{course_name}|{task_type}|{class_date.isoformat()}"
            if task_id not in lecture_tasks_by_key:
                task = {
                    "id": task_id,
                    "course": course_name,
                    "type": task_type,
                    "class_date": class_date.isoformat(),
                    "due_date": due_date.isoformat(),
                    "completed": False,
                }
                data["lecture_tasks"].append(task)
                lecture_tasks_by_key[task_id] = task

for task in data["lecture_tasks"]:
    if isinstance(task, dict) and not task.get("completed"):
        try:
            if date.fromisoformat(task.get("due_date", today.isoformat())) < today:
                task["due_date"] = today.isoformat()
        except (TypeError, ValueError):
            task["due_date"] = today.isoformat()

data["lecture_tasks"] = [
    task for task in data["lecture_tasks"]
    if isinstance(task, dict) and (
        not task.get("completed")
        or task.get("completed_date", today.isoformat()) >= (today - timedelta(days=90)).isoformat()
    )
]
save_data(data)

# Bulk assignment import
with st.expander("Import assignments in bulk (JSON)", expanded=False):
    st.write("Upload a JSON file or paste a JSON list. Required fields: name, total_units, due_date. Optional: completed_units, unit.")
    json_upload = st.file_uploader("Choose assignments JSON", type=["json"], key="bulk_json_upload")
    pasted_json = st.text_area(
        "Or paste JSON here",
        height=140,
        placeholder='[{"name":"Example Assignment","total_units":12,"completed_units":4,"unit":"Questions","due_date":"2026-10-06"}]',
        key="bulk_json_text",
    )
    if st.button("Import assignments", type="primary", key="bulk_import_button"):
        try:
            if json_upload is not None:
                payload = json.loads(json_upload.getvalue().decode("utf-8-sig"))
            elif pasted_json.strip():
                payload = json.loads(pasted_json)
            else:
                raise ValueError("Choose a JSON file or paste JSON first.")

            incoming = normalize_imported_assignments(payload, today)
            existing_keys = {
                (a.get("name", "").strip().casefold(), a.get("due_date"))
                for a in data["assignments"]
            }
            added = 0
            skipped = 0
            for assignment in incoming:
                key = (assignment["name"].casefold(), assignment["due_date"])
                if key in existing_keys:
                    skipped += 1
                    continue
                data["assignments"].append(assignment)
                existing_keys.add(key)
                added += 1
            save_data(data)
            st.success(f"Imported {added} assignment(s)." + (f" Skipped {skipped} duplicate(s)." if skipped else ""))
            st.rerun()
        except Exception as exc:
            st.error(f"Import failed: {exc}")

# Assignment creation
with st.expander("＋ Add an assignment", expanded=not data["assignments"]):
    # Keep this selector outside the form so changing it immediately switches fields.
    mode = st.radio(
        "Progress type",
        ["Units (questions, problems, pages)", "Percentage (0–100%)"],
        horizontal=True,
        key="new_assignment_mode",
    )
    with st.form("new_assignment", clear_on_submit=True):
        name = st.text_input("Assignment name")
        course = st.selectbox("Course / category", COURSES, key="new_course")
        col1, col2 = st.columns(2)
        start_date = col1.date_input("Start date", value=today, min_value=today)
        due_date = col2.date_input("End date / due date", value=today + timedelta(days=7), min_value=today)
        if mode.startswith("Units"):
            col3, col4, col5 = st.columns(3)
            total_units = col3.number_input("Total units", min_value=1, value=10, step=1)
            unit = col4.selectbox("Unit type", ["Questions", "Pages", "Chapters", "Problems", "Other"])
            completed_before = col5.number_input("Already completed", min_value=0, value=0, step=1)
            completed_today = 0
        else:
            completed_percent = st.number_input("Current completion (%)", min_value=0, max_value=100, value=0, step=1)
        submitted = st.form_submit_button("Save assignment", type="primary")
        if submitted:
            if not name.strip():
                st.error("Enter an assignment name.")
            elif due_date < start_date:
                st.error("End date must be on or after the start date.")
            elif mode.startswith("Units") and completed_before > total_units:
                st.error("Completed units cannot exceed total units.")
            else:
                assignment = {
                    "id": str(uuid.uuid4()), "name": name.strip(), "course": course,
                    "mode": "units" if mode.startswith("Units") else "percentage",
                    "start_date": start_date.isoformat(), "due_date": due_date.isoformat(),
                    "today_completed": 0, "today_date": today.isoformat(),
                }
                if mode.startswith("Units"):
                    assignment.update({
                        "total_units": int(total_units), "unit": unit,
                        "completed_units": int(completed_before),
                    })
                else:
                    assignment.update({"completed_percent": int(completed_percent)})
                data["assignments"].append(assignment)
                save_data(data)
                st.success("Assignment saved.")
                st.rerun()

# Progress rollover and remaining work
for assignment in data["assignments"]:
    if assignment.get("today_date") != today.isoformat():
        assignment["today_completed"] = 0
        assignment["today_date"] = today.isoformat()
    if assignment.get("mode") == "percentage":
        assignment["completed_percent"] = min(100, max(0, float(assignment.get("completed_percent", 0))))
        assignment["remaining_percent"] = max(0, 100 - assignment["completed_percent"])
    else:
        assignment.setdefault("mode", "units")
        assignment.setdefault("start_date", today.isoformat())
        assignment["remaining_units"] = max(0, assignment["total_units"] - assignment["completed_units"])

if data["assignments"]:
    plan, day_rows = build_schedule(
        data["assignments"], settings, data["calendar_events"], bool(data["calendar_name"]), today
    )
else:
    plan, day_rows = {}, []

# Top-level summary
remaining_assignments = [
    a for a in data["assignments"]
    if (
        float(a.get("remaining_percent", 0)) > 0
        if a.get("mode") == "percentage"
        else int(a.get("remaining_units", 0)) > 0
    )
]
today_items = plan.get(today.isoformat(), [])

tab_today, tab_assignments, tab_class_test_prep, tab_schedule, tab_settings = st.tabs(
    ["Today", "Assignments", "Class & Test Prep", "Schedule", "Data"]
)

with tab_today:
    st.subheader(f"Today's plan · {today.strftime('%A, %B') + f' {today.day}'}")
    if st.session_state.pop("show_progress_celebration", False):
        st.balloons()
        st.toast("Nice work — today's progress is recorded!", icon="🎉")
    today_lecture_tasks = [
        task for task in data["lecture_tasks"]
        if not task.get("completed") and task.get("due_date", today.isoformat()) <= today.isoformat()
    ]
    today_lecture_tasks.sort(key=lambda task: (task.get("type") != "lecture_prep", task.get("due_date", ""), task.get("course", "")))
    if today_lecture_tasks:
        st.markdown("#### Class prep & review")
        for lecture_task in today_lecture_tasks:
            course_name = lecture_task.get("course", "")
            course_color = COURSE_COLORS.get(course_name, app_theme["border"])
            class_date = date.fromisoformat(lecture_task["class_date"])
            title = "Lecture prep" if lecture_task.get("type") == "lecture_prep" else "Lecture notes review"
            related_topics = [
                topic["name"] for topic in data["class_topics"].get(course_name, [])
                if topic.get("class_date") == class_date.isoformat()
            ]
            detail = ", ".join(related_topics) if related_topics else f"Class on {class_date.strftime('%a, %b %d')}"
            task_col, done_col = st.columns([5.8, 1.1], vertical_alignment="center")
            task_col.markdown(
                f'<div style="background:{app_theme["surface"]};border:1px solid {app_theme["border"]};'
                f'border-left:5px solid {course_color};border-radius:10px;padding:9px 12px;margin:0 0 8px 0;">'
                f'<span style="display:inline-block;background:{course_color};color:{app_theme["card_text"]};'
                f'border-radius:999px;padding:3px 8px;font-size:.78rem;font-weight:750;margin-right:8px;">'
                f'{html.escape(course_name)}</span><strong style="font-size:.98rem;">{title}</strong>'
                f'<div style="font-size:.82rem;opacity:.78;margin-top:3px;">{html.escape(detail)}</div></div>',
                unsafe_allow_html=True,
            )
            if lecture_task.get("type") == "lecture_notes_review":
                review_outcome = done_col.selectbox(
                    "Review result",
                    ["Choose a color", "Red · extremely hard", "Orange · struggled", "Yellow · partly understood", "Green · easy"],
                    key=f"lecture_review_color_{lecture_task['id']}",
                    label_visibility="collapsed",
                )
                if done_col.button("Mark review done", key=f"complete_lecture_{lecture_task['id']}", use_container_width=True):
                    if review_outcome == "Choose a color":
                        st.warning("Choose a color for how the review went before marking it done.")
                    else:
                        lecture_task["review_color"] = review_outcome.split(" · ", 1)[0]
                        lecture_task["completed"] = True
                        lecture_task["completed_date"] = today.isoformat()
                        save_data(data)
                        st.toast("Lecture review recorded.", icon="✅")
                        st.rerun()
            elif done_col.button("Mark done", key=f"complete_lecture_{lecture_task['id']}", use_container_width=True):
                lecture_task["completed"] = True
                lecture_task["completed_date"] = today.isoformat()
                save_data(data)
                st.toast(f"{title} complete!", icon="✅")
                st.rerun()
    if not today_items and not today_lecture_tasks:
        st.info("Nothing is scheduled for today. Add assignments or check your calendar availability.")

    # Two assignments per row.
    for row_start in range(0, len(today_items), 2):
        row_cols = st.columns(2, gap="medium")
        for col_index, item in enumerate(today_items[row_start:row_start + 2]):
            with row_cols[col_index]:
                assignment = next((a for a in data["assignments"] if a["id"] == item["assignment_id"]), None)
                if not assignment:
                    continue

                course_name = assignment.get("course", infer_course(assignment["name"]))
                if course_name not in COURSE_COLORS:
                    course_name = "Other" if "Other" in COURSE_COLORS else next(iter(COURSE_COLORS))
                course_color = COURSE_COLORS[course_name]
                due_date = date.fromisoformat(assignment["due_date"])
                is_due_today = due_date == today
                card_class = "assignment-card due-today" if is_due_today else "assignment-card"
                due_tag = '<span class="due-today-tag">Due today</span>' if is_due_today else ""
                historical_progress = ""
                if assignment.get("mode") != "percentage":
                    completed_before_today = max(
                        0,
                        int(assignment.get("completed_units", 0))
                        - int(assignment.get("today_completed", 0)),
                    )
                    historical_unit = str(assignment.get("unit", "Questions")).lower()
                    if completed_before_today == 1 and historical_unit.endswith("s"):
                        historical_unit = historical_unit[:-1]
                    elif completed_before_today != 1 and not historical_unit.endswith("s"):
                        historical_unit += "s"
                    historical_progress = (
                        '<div class="historical-progress">Before today: '
                        f'{completed_before_today} {html.escape(historical_unit)} completed</div>'
                    )
                if item.get("mode") == "percentage":
                    target_text, unit_label = f"{item['percent']}%", "completion"
                else:
                    unit_label = item["unit"].lower()
                    if int(item["units"]) == 1 and unit_label.endswith("s"):
                        unit_label = unit_label[:-1]
                    elif int(item["units"]) != 1 and not unit_label.endswith("s"):
                        unit_label += "s"
                    target_text = str(item["units"])

                st.markdown(
                    f"""
                    <div class="{card_class}">
                        <div class="assignment-title" style="background:{course_color};">{html.escape(item['name'])}</div>{due_tag}
                        <div class="target-label">Today's target</div>
                        <div class="target-line">
                            <div class="target-number">{target_text}</div>
                            <div class="target-unit">{html.escape(unit_label)}</div>
                        </div>
                        <div class="assignment-meta">{html.escape(course_name)} &nbsp;·&nbsp; Due {due_date.strftime('%b %d')}</div>
                        {historical_progress}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.form(f"progress_{assignment['id']}"):
                    progress_col, action_col = st.columns([1, 1.15], vertical_alignment="bottom")
                    progress_col.markdown('<div class="today-progress-label">Completed today</div>', unsafe_allow_html=True)
                    if assignment.get("mode") == "percentage":
                        amount = progress_col.number_input(
                            "Percentage completed today", min_value=0, max_value=100,
                            value=int(assignment.get("today_completed", 0)), step=1,
                            key=f"today_{assignment['id']}", label_visibility="collapsed"
                        )
                    else:
                        amount = progress_col.number_input(
                            "Units completed today", min_value=0,
                            max_value=max(0, int(assignment["total_units"]) - (
                                int(assignment["completed_units"]) - int(assignment.get("today_completed", 0))
                            )),
                            value=int(assignment.get("today_completed", 0)), step=1,
                            key=f"today_{assignment['id']}", label_visibility="collapsed"
                        )
                    if action_col.form_submit_button("Update", use_container_width=True):
                        previous_today = float(assignment.get("today_completed", 0))
                        delta = float(amount) - previous_today
                        if assignment.get("mode") == "percentage":
                            assignment["completed_percent"] = max(0, min(100, float(assignment.get("completed_percent", 0)) + delta))
                        else:
                            assignment["completed_units"] = max(
                                0, min(assignment["total_units"], assignment["completed_units"] + int(delta))
                            )
                        assignment["today_completed"] = int(amount)
                        assignment["today_date"] = today.isoformat()
                        if float(amount) > previous_today:
                            st.session_state["show_progress_celebration"] = True
                        save_data(data)
                        st.rerun()

with tab_assignments:
    st.subheader("Your assignments")
    if not data["assignments"]:
        st.info("No assignments yet.")

    current_assignments = []
    completed_assignments = []
    for assignment in data["assignments"]:
        is_percentage = assignment.get("mode") == "percentage"
        progress = float(assignment.get("completed_percent", 0)) / 100 if is_percentage else (
            assignment["completed_units"] / assignment["total_units"]
        )
        (completed_assignments if progress >= 1 else current_assignments).append(assignment)

    for group_label, group_assignments in (
        ("Current assignments", current_assignments),
        ("Completed assignments", completed_assignments),
    ):
        with st.expander(f"{group_label} ({len(group_assignments)})", expanded=False):
            if not group_assignments:
                st.caption("None")
            for assignment in group_assignments:
                is_percentage = assignment.get("mode") == "percentage"
                due = date.fromisoformat(assignment["due_date"])
                start = date.fromisoformat(assignment.get("start_date", today.isoformat()))
                progress = float(assignment.get("completed_percent", 0)) / 100 if is_percentage else (
                    assignment["completed_units"] / assignment["total_units"]
                )
                overdue = due < today and progress < 1
                with st.container(border=True):
                    left, right = st.columns([4, 1])
                    course_name = assignment.get("course", infer_course(assignment["name"]))
                    if course_name not in COURSE_COLORS:
                        course_name = "Other" if "Other" in COURSE_COLORS else next(iter(COURSE_COLORS))
                    left.markdown(
                        f'<div class="assignment-title" style="background:{COURSE_COLORS[course_name]};">{html.escape(assignment["name"])}</div>',
                        unsafe_allow_html=True,
                    )
                    if is_percentage:
                        left.caption(f"{round(progress * 100)}% complete · {start.strftime('%b %d')} – {due.strftime('%b %d, %Y')}")
                    else:
                        left.caption(f"{assignment['completed_units']}/{assignment['total_units']} {assignment['unit'].lower()} completed · {start.strftime('%b %d')} – {due.strftime('%b %d, %Y')}")
                    left.progress(progress)
                    if overdue:
                        right.error("Overdue")
                    elif progress >= 1:
                        right.success("Complete")
                    else:
                        right.info(f"{round((1-progress)*100)}% left" if is_percentage else f"{assignment['total_units']-assignment['completed_units']} left")
                    with st.expander("Edit or delete"):
                        with st.form(f"edit_{assignment['id']}"):
                            edit_name = st.text_input("Name", assignment["name"])
                            current_course = assignment.get("course", infer_course(assignment["name"]))
                            if current_course not in COURSES:
                                current_course = "Other" if "Other" in COURSES else COURSES[0]
                            edit_course = st.selectbox("Course / category", COURSES, index=COURSES.index(current_course), key=f"course_{assignment['id']}")
                            edit_start = st.date_input("Start date", value=start, key=f"start_{assignment['id']}")
                            edit_due = st.date_input("End date / due date", value=due, key=f"due_{assignment['id']}")
                            if is_percentage:
                                edit_completed_percent = st.number_input("Percent complete", min_value=0, max_value=100, value=int(assignment.get("completed_percent", 0)), key=f"pct_{assignment['id']}")
                            else:
                                edit_total = st.number_input("Total units", min_value=1, value=int(assignment["total_units"]), key=f"total_{assignment['id']}")
                                edit_completed = st.number_input("Total completed units", min_value=0, max_value=int(edit_total), value=min(int(assignment["completed_units"]), int(edit_total)), key=f"completed_{assignment['id']}")
                                edit_unit = st.selectbox("Unit", ["Questions", "Pages", "Chapters", "Problems", "Other"], index=["Questions", "Pages", "Chapters", "Problems", "Other"].index(assignment["unit"]) if assignment["unit"] in ["Questions", "Pages", "Chapters", "Problems", "Other"] else 0, key=f"unit_{assignment['id']}")
                            save_edit = st.form_submit_button("Save changes")
                            delete = st.form_submit_button("Delete assignment")
                            if save_edit:
                                if edit_due < edit_start:
                                    st.error("End date must be on or after the start date.")
                                else:
                                    assignment.update({
                                        "name": edit_name.strip(), "course": edit_course,
                                        "start_date": edit_start.isoformat(), "due_date": edit_due.isoformat(),
                                    })
                                    if is_percentage:
                                        assignment["completed_percent"] = int(edit_completed_percent)
                                    else:
                                        assignment.update({"total_units": int(edit_total), "completed_units": int(edit_completed), "unit": edit_unit})
                                    save_data(data)
                                    st.rerun()
                            if delete:
                                data["assignments"] = [a for a in data["assignments"] if a["id"] != assignment["id"]]
                                save_data(data)
                                st.rerun()

with tab_class_test_prep:
    st.subheader("Class & Test Prep")
    st.caption("Manage course topics here. Choose a class date from the meeting days configured in Data, then add, edit, or remove topics.")

    selected_topic_course = st.selectbox(
        "Choose a class", COURSES, key="topic_manager_course",
    )
    selected_course_color = COURSE_COLORS[selected_topic_course]
    st.markdown(
        f'<div style="display:inline-block;background:{selected_course_color};color:{app_theme["card_text"]};'
        f'border-radius:999px;padding:5px 11px;margin:3px 0 10px 0;font-weight:750;">'
        f'{html.escape(selected_topic_course)} topics</div>',
        unsafe_allow_html=True,
    )

    selected_topics = data["class_topics"].setdefault(selected_topic_course, [])
    selected_meeting_days = data["course_meeting_days"].get(selected_topic_course, [])
    default_topic_class_date = today
    for day_offset in range(8):
        candidate_date = today - timedelta(days=day_offset)
        if candidate_date.strftime("%A") in selected_meeting_days:
            default_topic_class_date = candidate_date
            break
    if st.button("＋ Add topic", key=f"show_add_topic_{COURSES.index(selected_topic_course)}"):
        st.session_state["adding_topic_for_course"] = selected_topic_course
    if st.session_state.get("adding_topic_for_course") == selected_topic_course:
        with st.form(f"add_class_topic_{COURSES.index(selected_topic_course)}", clear_on_submit=True):
            new_topic_name = st.text_input("Topic name", placeholder="e.g. 7.8 Improper Integrals")
            topic_class_date = st.date_input(
                "Class date", value=default_topic_class_date,
                key=f"add_topic_class_date_{COURSES.index(selected_topic_course)}",
            )
            if not selected_meeting_days:
                st.info("Set this course's meeting days in the Data tab before adding a dated topic.")
            add_topic = st.form_submit_button("Add topic", type="primary")
            cancel_topic = st.form_submit_button("Cancel")
            if add_topic:
                normalized_topic_name = new_topic_name.strip()
                if not normalized_topic_name:
                    st.error("Enter a topic name.")
                elif not selected_meeting_days:
                    st.error("Set this course's meeting days in the Data tab first.")
                elif topic_class_date.strftime("%A") not in selected_meeting_days:
                    st.error("Choose a class date that matches this course's meeting days in the Data tab.")
                elif any(topic["name"].casefold() == normalized_topic_name.casefold() for topic in selected_topics):
                    st.error("That topic is already listed for this class.")
                else:
                    selected_topics.append({
                        "id": str(uuid.uuid4()),
                        "name": normalized_topic_name,
                        "class_date": topic_class_date.isoformat(),
                    })
                    data["class_topics"][selected_topic_course] = selected_topics
                    st.session_state.pop("adding_topic_for_course", None)
                    save_data(data)
                    st.rerun()
            if cancel_topic:
                st.session_state.pop("adding_topic_for_course", None)
                st.rerun()

    if selected_topics:
        for topic in list(selected_topics):
            topic_meeting_days = data["course_meeting_days"].get(selected_topic_course, [])
            default_edit_class_date = today
            try:
                default_edit_class_date = date.fromisoformat(topic.get("class_date", ""))
            except (TypeError, ValueError):
                for day_offset in range(8):
                    candidate_date = today - timedelta(days=day_offset)
                    if candidate_date.strftime("%A") in topic_meeting_days:
                        default_edit_class_date = candidate_date
                        break
            with st.form(f"edit_class_topic_{topic['id']}"):
                edit_col, date_col, save_col, delete_col = st.columns([3, 1.4, 0.8, 0.8])
                edited_topic_name = edit_col.text_input(
                    "Topic", topic["name"], key=f"edit_topic_name_{topic['id']}",
                )
                edited_class_date = date_col.date_input(
                    "Class date", value=default_edit_class_date, key=f"edit_topic_class_date_{topic['id']}",
                )
                if not topic_meeting_days:
                    date_col.caption("Set meeting days in Data to choose a date.")
                save_topic = save_col.form_submit_button("Save")
                delete_topic = delete_col.form_submit_button("Delete")
                if save_topic:
                    normalized_topic_name = edited_topic_name.strip()
                    duplicate_topic = any(
                        item["id"] != topic["id"]
                        and item["name"].casefold() == normalized_topic_name.casefold()
                        for item in selected_topics
                    )
                    if not normalized_topic_name:
                        st.error("Enter a topic name.")
                    elif duplicate_topic:
                        st.error("That topic is already listed for this class.")
                    elif not topic_meeting_days:
                        st.error("Set this course's meeting days in the Data tab first.")
                    elif edited_class_date.strftime("%A") not in topic_meeting_days:
                        st.error("Choose a class date that matches this course's meeting days in the Data tab.")
                    else:
                        topic["name"] = normalized_topic_name
                        topic["class_date"] = edited_class_date.isoformat()
                        save_data(data)
                        st.rerun()
                if delete_topic:
                    data["class_topics"][selected_topic_course] = [
                        item for item in selected_topics if item["id"] != topic["id"]
                    ]
                    save_data(data)
                    st.rerun()
    else:
        st.info("No topics for this class yet. Use + Add topic to start the list.")

    st.divider()
    st.subheader("Course topic lists")
    st.caption("These colored dropdowns show each course's topics. Use the topic manager above to make changes.")
    for course_name, course_color in COURSE_COLORS.items():
        course_topics = data["class_topics"].get(course_name, [])
        topic_list_markup = (
            "<ul style='margin:0;padding-left:22px;'>"
            + "".join(
                f"<li>{html.escape(topic['name'])}"
                + (f" · {date.fromisoformat(topic['class_date']).strftime('%a, %b %d')}" if topic.get("class_date") else "")
                + "</li>"
                for topic in course_topics
            )
            + "</ul>"
            if course_topics else "<p style='margin:0;'>No topics added yet.</p>"
        )
        st.markdown(
            f'<div style="border:1px solid {course_color};border-left:6px solid {course_color};'
            f'border-radius:12px;background:{app_theme["surface"]};margin:0 0 10px 0;overflow:hidden;">'
            f'<details><summary style="background:{course_color};color:{app_theme["card_text"]};'
            f'padding:13px 16px;font-weight:750;cursor:pointer;">{html.escape(course_name)}</summary>'
            f'<div style="padding:12px 16px;color:{app_theme["text"]};">{topic_list_markup}</div>'
            f'</details></div>',
            unsafe_allow_html=True,
        )

with tab_schedule:
    st.subheader("Upcoming daily workload")
    day_info_by_key = {info["date"].isoformat(): info for info in day_rows[:21]}
    lecture_tasks_by_day = {}
    for lecture_task in data["lecture_tasks"]:
        try:
            due_key = date.fromisoformat(lecture_task["due_date"]).isoformat()
        except (KeyError, TypeError, ValueError):
            continue
        lecture_tasks_by_day.setdefault(due_key, []).append(lecture_task)
    schedule_day_keys = set()
    for day_key, day_info in day_info_by_key.items():
        if plan.get(day_key) or date.fromisoformat(day_key) <= today + timedelta(days=6):
            schedule_day_keys.add(day_key)
    schedule_day_keys.update((today + timedelta(days=day_offset)).isoformat() for day_offset in range(7))
    schedule_day_keys.update(lecture_tasks_by_day)

    if not schedule_day_keys:
        st.info("Add an assignment to build your schedule.")
    else:
        for day_key in sorted(schedule_day_keys):
            day = date.fromisoformat(day_key)
            items = plan.get(day_key, [])
            day_info = day_info_by_key.get(day_key, {})
            with st.container(border=True):
                st.write(f"**{day.strftime('%A, %b %d')}**")
                if day_info:
                    planned_units = sum(item.get("units", 0) for item in items)
                    planned_percent = sum(item.get("percent", 0) for item in items)
                    summary = []
                    if planned_units: summary.append(f"{planned_units} units")
                    if planned_percent: summary.append(f"{planned_percent}%")
                    st.caption(
                        f"Available: {day_info.get('free_hours', 0):.1f} h  ·  Assignments: "
                        + (" · ".join(summary) if summary else "None")
                    )

                if items:
                    st.markdown("**Assignments**")
                    for item in items:
                        linked_assignment = next((a for a in data["assignments"] if a["id"] == item["assignment_id"]), None)
                        item_is_due = bool(linked_assignment and date.fromisoformat(linked_assignment["due_date"]) == day)
                        if item.get("mode") == "percentage":
                            detail = f"{item['percent']}%"
                        else:
                            item_unit = item["unit"].lower()
                            if int(item["units"]) == 1 and item_unit.endswith("s"): item_unit = item_unit[:-1]
                            elif int(item["units"]) != 1 and not item_unit.endswith("s"): item_unit += "s"
                            detail = f"{item['units']} {item_unit}"
                        if item_is_due:
                            st.markdown(f'<div style="color:#ff7777;font-weight:750;">• {html.escape(item["name"])}: {detail} — DUE TODAY</div>', unsafe_allow_html=True)
                        else:
                            st.write(f"• {item['name']}: {detail}")

                class_tasks = lecture_tasks_by_day.get(day_key, [])
                if class_tasks:
                    st.markdown("**Class prep & review**")
                    class_tasks.sort(key=lambda task: (task.get("type") != "lecture_prep", task.get("course", "")))
                    for lecture_task in class_tasks:
                        course_name = lecture_task.get("course", "")
                        course_color = COURSE_COLORS.get(course_name, app_theme["border"])
                        class_date = date.fromisoformat(lecture_task["class_date"])
                        title = "Lecture prep" if lecture_task.get("type") == "lecture_prep" else "Lecture notes review"
                        related_topics = [
                            topic["name"] for topic in data["class_topics"].get(course_name, [])
                            if topic.get("class_date") == class_date.isoformat()
                        ]
                        detail = ", ".join(related_topics) if related_topics else f"Class on {class_date.strftime('%a, %b %d')}"
                        if lecture_task.get("completed"):
                            status = "✓ Done"
                            if lecture_task.get("type") == "lecture_notes_review" and lecture_task.get("review_color"):
                                status += f" · {lecture_task['review_color']}"
                        elif day > today:
                            status = "Upcoming"
                        else:
                            status = "Mark done in Today"
                        st.markdown(
                            f'<div style="border-left:4px solid {course_color};padding:3px 9px;margin:2px 0 6px 0;">'
                            f'<span style="color:{course_color};font-weight:750;">{html.escape(course_name)}</span> · '
                            f'{title} · {html.escape(detail)} <span style="opacity:.7;">({status})</span></div>',
                            unsafe_allow_html=True,
                        )

    overloaded = []
    for assignment in data["assignments"]:
        unscheduled = assignment.get("unscheduled_percent", 0) if assignment.get("mode") == "percentage" else assignment.get("unscheduled_units", 0)
        if unscheduled > 0:
            overloaded.append((assignment, unscheduled))
    if overloaded:
        st.warning("Some work could not be scheduled between its start and end dates. Check your dates and calendar availability.")
        for assignment, unscheduled in overloaded:
            unit_text = "%" if assignment.get("mode") == "percentage" else " units"
            st.write(f"• {assignment['name']}: {unscheduled:g}{unit_text} unscheduled")

with tab_settings:
    st.subheader("Appearance")
    st.caption("Choose colors for the main areas of the planner. Changes are saved with your data.")
    with st.expander("Customize theme colors", expanded=False):
        with st.form("app_theme_form"):
            theme_left, theme_right = st.columns(2)
            theme_background = theme_left.color_picker("Page background", app_theme["background"], key="theme_background")
            theme_sidebar = theme_right.color_picker("Sidebar and panels", app_theme["sidebar"], key="theme_sidebar")
            theme_text = theme_left.color_picker("Main text", app_theme["text"], key="theme_text")
            theme_border = theme_right.color_picker("Borders", app_theme["border"], key="theme_border")
            theme_button = theme_left.color_picker("Buttons", app_theme["button"], key="theme_button")
            theme_button_text = theme_right.color_picker("Button text", app_theme["button_text"], key="theme_button_text")
            theme_card = theme_left.color_picker("Assignment cards", app_theme["card"], key="theme_card")
            theme_card_text = theme_right.color_picker("Assignment card text", app_theme["card_text"], key="theme_card_text")
            theme_input = theme_left.color_picker("Input fields", app_theme["input"], key="theme_input")
            theme_surface = theme_right.color_picker("Forms and panels", app_theme["surface"], key="theme_surface")
            save_theme = st.form_submit_button("Save theme", type="primary")
            if save_theme:
                data["app_theme"] = {
                    "background": theme_background,
                    "sidebar": theme_sidebar,
                    "text": theme_text,
                    "border": theme_border,
                    "button": theme_button,
                    "button_text": theme_button_text,
                    "card": theme_card,
                    "card_text": theme_card_text,
                    "input": theme_input,
                    "surface": theme_surface,
                }
                save_data(data)
                st.rerun()
        if st.button("Reset to beige theme", key="reset_app_theme"):
            data["app_theme"] = dict(APP_THEME_DEFAULTS)
            save_data(data)
            st.session_state["reset_app_theme_pending"] = True
            st.rerun()

    st.divider()
    st.subheader("Courses and categories")
    st.caption("Add your own courses, choose their colors, and set the days each course meets.")
    with st.expander("Add a course or category", expanded=False):
        with st.form("add_course_category", clear_on_submit=True):
            new_category_name = st.text_input("Name")
            new_category_color = st.color_picker("Color", "#D8E6D3")
            new_category_meeting_days = st.multiselect("Meets on", WEEKDAY_NAMES, default=[])
            add_category = st.form_submit_button("Add category", type="primary")
            if add_category:
                normalized_name = new_category_name.strip()
                if not normalized_name:
                    st.error("Enter a course or category name.")
                elif any(name.casefold() == normalized_name.casefold() for name in COURSE_COLORS):
                    st.error("That course or category already exists.")
                else:
                    COURSE_COLORS[normalized_name] = new_category_color
                    COURSES[:] = list(COURSE_COLORS)
                    data["course_meeting_days"][normalized_name] = new_category_meeting_days
                    data["course_categories"] = dict(COURSE_COLORS)
                    save_data(data)
                    st.rerun()

    for category_name, category_color in list(COURSE_COLORS.items()):
        with st.form(f"edit_course_category_{category_name}"):
            name_col, color_col, save_col, delete_col = st.columns([2.2, 1, 0.8, 0.8])
            renamed_category = name_col.text_input("Name", category_name, key=f"category_name_{category_name}")
            recolored_category = color_col.color_picker("Color", category_color, key=f"category_color_{category_name}")
            category_meeting_days = st.multiselect(
                "Meets on", WEEKDAY_NAMES,
                default=data["course_meeting_days"].get(category_name, []),
                key=f"category_meeting_days_{category_name}",
            )
            save_category = save_col.form_submit_button("Save")
            delete_category = delete_col.form_submit_button("Delete")
            if save_category:
                normalized_name = renamed_category.strip()
                duplicate_name = any(
                    name != category_name and name.casefold() == normalized_name.casefold()
                    for name in COURSE_COLORS
                )
                if not normalized_name:
                    st.error("Enter a course or category name.")
                elif duplicate_name:
                    st.error("That course or category already exists.")
                else:
                    updated_categories = {
                        (normalized_name if name == category_name else name):
                        (recolored_category if name == category_name else color)
                        for name, color in COURSE_COLORS.items()
                    }
                    COURSE_COLORS.clear()
                    COURSE_COLORS.update(updated_categories)
                    if normalized_name != category_name and category_name in data["class_topics"]:
                        data["class_topics"][normalized_name] = data["class_topics"].pop(category_name)
                    if normalized_name != category_name and category_name in data["course_meeting_days"]:
                        data["course_meeting_days"][normalized_name] = data["course_meeting_days"].pop(category_name)
                    data["course_meeting_days"][normalized_name] = category_meeting_days
                    for assignment in data["assignments"]:
                        if assignment.get("course") == category_name:
                            assignment["course"] = normalized_name
                    for lecture_task in data["lecture_tasks"]:
                        if lecture_task.get("course") == category_name:
                            lecture_task["course"] = normalized_name
                            lecture_task["id"] = lecture_task["id"].replace(f"{category_name}|", f"{normalized_name}|", 1)
                    COURSES[:] = list(COURSE_COLORS)
                    data["course_categories"] = dict(COURSE_COLORS)
                    save_data(data)
                    st.rerun()
            if delete_category:
                if len(COURSE_COLORS) <= 1:
                    st.error("Keep at least one course or category.")
                else:
                    remaining_categories = {
                        name: color for name, color in COURSE_COLORS.items()
                        if name != category_name
                    }
                    replacement_category = next(iter(remaining_categories))
                    for assignment in data["assignments"]:
                        if assignment.get("course") == category_name:
                            assignment["course"] = replacement_category
                    data["class_topics"].pop(category_name, None)
                    data["course_meeting_days"].pop(category_name, None)
                    data["lecture_tasks"] = [
                        task for task in data["lecture_tasks"] if task.get("course") != category_name
                    ]
                    COURSE_COLORS.clear()
                    COURSE_COLORS.update(remaining_categories)
                    COURSES[:] = list(COURSE_COLORS)
                    data["course_categories"] = dict(COURSE_COLORS)
                    save_data(data)
                    st.rerun()

    st.divider()
    st.subheader("How scheduling works")
    st.markdown(
        "- Calendar events are treated as busy time.\\n"
        "- Gaps of 30 minutes or less between events are merged into the busy block.\\n"
        "- Free time is measured only inside your waking hours.\\n"
        "- The sidebar shows estimated free hours for each date and lets you override them individually.\\n"
        "- Work is distributed directly in proportion to the available hours you enter.\\n"
        "- Daily targets are whole units and are rounded up to build in a small early-completion buffer.\\n"
        "- Earlier deadlines are scheduled first.\\n"
        "- The plan is recalculated whenever you change progress, assignments, calendar, or settings."
    )
    st.markdown("**Progress types:** Unit-based assignments are scheduled as questions/pages/problems per day. Percentage assignments are scheduled as percentage points per day until they reach 100%. Both use the start date, due date, and the daily availability values shown in the sidebar.")
    st.caption("Calendar data and assignment data stay in this folder on your computer.")
    export_json = json.dumps(data, indent=2)
    st.download_button("Download assignment backup (JSON)", export_json, "assignments_backup.json", "application/json")
    if st.button("Export assignments as CSV"):
        import csv
        import io
        buffer = io.StringIO()
        fields = ["name", "mode", "start_date", "due_date", "total_units", "completed_units", "remaining_units", "completed_percent", "remaining_percent", "unit"]
        writer = csv.DictWriter(buffer, fieldnames=fields)
        writer.writeheader()
        for a in data["assignments"]:
            writer.writerow({field: a.get(field, "") for field in fields})
        st.download_button("Download CSV", buffer.getvalue(), "assignments.csv", "text/csv")

save_data(data)
