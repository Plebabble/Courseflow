import calendar as calendar_module
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
SLEEP_HOURS_PER_DAY = 8.0


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
    "button": "#A98767",
    "button_text": "#FFF8ED",
    "card": "#D7C2A6",
    "card_text": "#493D31",
    "input": "#FFFDF8",
    "border": "#B89C7B",
    "surface": "#F4EADB",
    "dropdown": "#E2D1B8",
    "progress": "#B9D8BD",
    "hover": "#D5C1A7",
}
APP_THEME_PALETTES = {
    "Beige": dict(APP_THEME_DEFAULTS),
    "Forest green": {
        "background": "#E6EBE2", "sidebar": "#D5DED1", "text": "#2F3D31",
        "button": "#5C765F", "button_text": "#F7F8F2", "card": "#D3DFD0",
        "card_text": "#304033", "input": "#FBFCF8", "border": "#A8B9A4",
        "surface": "#F0F3EC", "dropdown": "#DCE5D9", "progress": "#AFC3AD", "hover": "#C5D4C2",
    },
    "Mint": {
        "background": "#E6F2F0", "sidebar": "#D5E9E6", "text": "#304441",
        "button": "#78AAA2", "button_text": "#183C38", "card": "#CDE5E0",
        "card_text": "#304441", "input": "#FBFDFC", "border": "#A4C8C1",
        "surface": "#F1F8F6", "dropdown": "#D9EBE7", "progress": "#A8D9CF", "hover": "#C4E1DB",
    },
    "Pink": {
        "background": "#F5E8E9", "sidebar": "#EBD7D9", "text": "#503D42",
        "button": "#B97F8C", "button_text": "#FFF9F8", "card": "#EFD8DC",
        "card_text": "#503D42", "input": "#FFFCFC", "border": "#D2AEB4",
        "surface": "#FAF1F1", "dropdown": "#F0DFE1", "progress": "#E7BBC5", "hover": "#E8CDD2",
    },
    "Dark mode": {
        "background": "#25232B", "sidebar": "#302D38", "text": "#F0EDF5",
        "button": "#9D86C5", "button_text": "#211C2A", "card": "#3A3643",
        "card_text": "#F0EDF5", "input": "#302D38", "border": "#62576F",
        "surface": "#302D37", "dropdown": "#3B3645", "progress": "#806AA6", "hover": "#51475F",
    },
    "Autumn": {
        "background": "#F1E4D2", "sidebar": "#E5D1B5", "text": "#4D3B2D",
        "button": "#C17A45", "button_text": "#FFF8EF", "card": "#E9D0AE",
        "card_text": "#4D3B2D", "input": "#FFFCF7", "border": "#C9A77D",
        "surface": "#F8EFE2", "dropdown": "#EAD8BE", "progress": "#DDAE76", "hover": "#E4C49E",
    },
    "Lavender": {
        "background": "#EFECF5", "sidebar": "#E1DCEC", "text": "#433D51",
        "button": "#9482B4", "button_text": "#FFFCFF", "card": "#DED8EB",
        "card_text": "#433D51", "input": "#FDFCFF", "border": "#B9AFD0",
        "surface": "#F7F5FA", "dropdown": "#E7E1F0", "progress": "#C4B6DD", "hover": "#DBD3E8",
    },
    "Ocean": {
        "background": "#E7F1F7", "sidebar": "#D4E5EF", "text": "#2A3F50",
        "button": "#4F83A8", "button_text": "#F7FBFE", "card": "#D2E4EF",
        "card_text": "#2A3F50", "input": "#FBFDFF", "border": "#A9C5D7",
        "surface": "#F2F7FA", "dropdown": "#DCEAF2", "progress": "#A6CADF", "hover": "#C4DCEB",
    },
    "Peach": {
        "background": "#F8EEE7", "sidebar": "#EBD9CC", "text": "#4E3A32",
        "button": "#BD765C", "button_text": "#FFF8F4", "card": "#EFD7C8",
        "card_text": "#4E3A32", "input": "#FFFCFA", "border": "#D2B2A0",
        "surface": "#FBF4EF", "dropdown": "#EFDFD4", "progress": "#E8B99F", "hover": "#E6CAB9",
    },
    "Buttercup": {
        "background": "#F5F0DE", "sidebar": "#E9E0C4", "text": "#4C4532",
        "button": "#A58B45", "button_text": "#FFFDF5", "card": "#EBE2C6",
        "card_text": "#4C4532", "input": "#FFFEFA", "border": "#D0C39B",
        "surface": "#FAF6E9", "dropdown": "#EDE5CB", "progress": "#DDCF8C", "hover": "#E8DDB6",
    },
    "Berry": {
        "background": "#F4EAF1", "sidebar": "#E7D6E3", "text": "#473742",
        "button": "#996B91", "button_text": "#FFF9FD", "card": "#EAD8E7",
        "card_text": "#473742", "input": "#FFFCFE", "border": "#C8AFC4",
        "surface": "#F8F1F7", "dropdown": "#EADBE9", "progress": "#D5B4D0", "hover": "#DFC7DD",
    },
    "Slate": {
        "background": "#E9EDF2", "sidebar": "#D9E0E8", "text": "#343E4B",
        "button": "#657C99", "button_text": "#F8FAFD", "card": "#D7E0E9",
        "card_text": "#343E4B", "input": "#FCFDFE", "border": "#B2BECC",
        "surface": "#F3F5F8", "dropdown": "#DFE5EC", "progress": "#B6C5D8", "hover": "#CED8E3",
    },
    "Terracotta": {
        "background": "#F2E7DD", "sidebar": "#E5D1BF", "text": "#4B382F",
        "button": "#A96043", "button_text": "#FFF8F2", "card": "#E8D0BD",
        "card_text": "#4B382F", "input": "#FFFCF8", "border": "#C9A88D",
        "surface": "#F8F0E8", "dropdown": "#E9D7C7", "progress": "#DFAF91", "hover": "#DEC1AE",
    },
    "Monochrome": {
        "background": "#F0F0EF", "sidebar": "#E0E0DE", "text": "#353637",
        "button": "#62676C", "button_text": "#FFFFFF", "card": "#DEDFDE",
        "card_text": "#353637", "input": "#FCFCFB", "border": "#B9BCBC",
        "surface": "#F5F5F3", "dropdown": "#E5E6E5", "progress": "#B8C6C4", "hover": "#D3D8D7",
    },
}
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DEFAULT_COURSE_MEETING_DAYS = {}


def infer_course(name):
    text = str(name).casefold()
    for course_name in COURSES:
        if course_name != "Other" and course_name.casefold() in text:
            return course_name
    return "Other" if "Other" in COURSE_COLORS else next(iter(COURSE_COLORS))


def shift_schedule_calendar_anchor(amount):
    anchor = st.session_state.get("schedule_calendar_anchor", date.today())
    if not isinstance(anchor, date):
        anchor = date.today()
    if st.session_state.get("schedule_calendar_period", "Week") == "Week":
        st.session_state["schedule_calendar_anchor"] = anchor + timedelta(days=amount * 7)
        return
    month_index = anchor.month - 1 + amount
    year = anchor.year + month_index // 12
    month = month_index % 12 + 1
    day_number = min(anchor.day, calendar_module.monthrange(year, month)[1])
    st.session_state["schedule_calendar_anchor"] = date(year, month, day_number)


def set_schedule_calendar_anchor_today():
    st.session_state["schedule_calendar_anchor"] = date.today()

st.set_page_config(page_title="Assignment Planner", page_icon="📚", layout="wide")


st.markdown("""
<style>
    .stApp { background: var(--planner-background); color: var(--planner-text); }
    [data-testid="stAppViewContainer"] { background: var(--planner-background); }
    [data-testid="stHeader"] { background: var(--planner-background); }
    #MainMenu, footer, .stDeployButton, [data-testid="stToolbar"],
    [data-testid="stToolbarActions"], [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
    }
    [data-testid="stSidebar"] { background: var(--planner-sidebar); border-right: 1px solid var(--planner-border); }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1180px; }
    h1, h2, h3, h4, p, label, span, div { letter-spacing: -0.015em; }
    h1, h2, h3 { color: var(--planner-text); letter-spacing: -0.035em; }
    [data-testid="stMarkdownContainer"] { color: var(--planner-text); }
    [data-testid="stCaptionContainer"] { color: var(--planner-text); }
    [data-testid="stWidgetLabel"] p, .stApp label, .stApp p { color: var(--planner-text); }
    [data-testid="stAlert"] { background: var(--planner-surface); border-color: var(--planner-border); color: var(--planner-text); }
    div[data-testid="stProgress"] > div > div { background: var(--planner-progress); }
    .stApp button[kind="primary"] { background: var(--planner-button); border-color: var(--planner-border); color: var(--planner-button_text); }
    .stApp button[kind="secondary"] { background: var(--planner-dropdown); border-color: var(--planner-border); color: var(--planner-text); }
    div[data-testid="stMetric"] {
        background: var(--planner-card); border: 1px solid var(--planner-border);
        padding: 16px 18px; border-radius: 14px;
    }
    div[data-testid="stMetricLabel"] { color: var(--planner-card_text); }
    div[data-testid="stMetricValue"] { color: var(--planner-button_text); font-weight: 750; }
    div[data-testid="stTabs"] button { font-weight: 650; }
    div[data-testid="stTabs"] button p { color: var(--planner-text); }
    div[data-testid="stForm"] {
        background: var(--planner-surface); border: 1px solid var(--planner-border);
        border-radius: 14px; padding: 14px 16px;
    }
    [data-testid="stFileUploaderDropzone"] {
        background: var(--planner-surface) !important; border: 1px dashed var(--planner-border) !important;
    }
    [data-testid="stFileUploaderDropzone"] * { color: var(--planner-text) !important; }
    [data-testid="stFileUploaderDropzone"] button {
        background: var(--planner-dropdown) !important; color: var(--planner-text) !important;
        border-color: var(--planner-border) !important;
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
        background: var(--planner-input) !important;
        color: var(--planner-text) !important;
        border: 1px solid var(--planner-border) !important;
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
        border-color: var(--planner-button) !important;
        box-shadow: 0 0 0 2px color-mix(in srgb, var(--planner-button) 16%, transparent) !important;
    }
    .stApp [data-testid="stTextInput"] input,
    .stApp [data-testid="stNumberInput"] input,
    .stApp [data-testid="stDateInput"] input,
    .stApp [data-testid="stTimeInput"] input,
    .stApp [data-testid="stTextArea"] textarea,
    .stApp [data-testid="stMultiSelect"] input {
        background: var(--planner-input) !important;
        color: var(--planner-text) !important;
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
    .stApp [data-testid="stDateInput"] [data-baseweb="input"] div,
    .stApp [data-testid="stDateInput"] [data-baseweb="input"] input {
        background-color: var(--planner-input) !important;
    }
    .stApp [data-testid="stNumberInput"] input { text-align: center; }
    .stApp [data-testid="stNumberInput"] button,
    .stApp [data-testid="stTimeInput"] button {
        background: var(--planner-surface) !important;
        color: var(--planner-text) !important;
        border: 0 !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        outline: 0 !important;
    }
    .stApp [data-testid="stMultiSelect"] [data-baseweb="tag"] {
        background: var(--planner-dropdown) !important; color: var(--planner-text) !important;
        border-radius: 8px !important;
    }
    .stApp [data-testid="stMultiSelect"] [data-baseweb="tag"] *,
    .stApp [data-testid="stMultiSelect"] [data-baseweb="tag"] button,
    .stApp [data-testid="stMultiSelect"] [data-baseweb="tag"] svg {
        background: transparent !important;
        color: var(--planner-text) !important;
        fill: var(--planner-text) !important;
    }
    .stApp [data-testid="stMultiSelect"] input {
        background: transparent !important;
        min-width: 2px !important;
        width: auto !important;
    }
    .stApp [data-testid="stDateInput"] button {
        color: var(--planner-text) !important; border: 0 !important;
        background: transparent !important; box-shadow: none !important;
    }
    .stApp [data-testid="stForm"] button,
    .stApp [data-testid="stSidebar"] button {
        background: var(--planner-dropdown) !important;
        color: var(--planner-text) !important;
        border-color: var(--planner-border) !important;
        box-shadow: none !important;
    }
    .stApp [data-baseweb="popover"] [role="listbox"],
    .stApp [data-baseweb="popover"] [role="option"] {
        background: var(--planner-input) !important;
        color: var(--planner-text) !important;
    }
    .stApp [data-baseweb="popover"] [data-testid="stDatePicker"] *,
    .stApp [data-baseweb="popover"] [data-testid="stTimePicker"] * {
        color: var(--planner-text) !important;
    }
    .stApp input[type="checkbox"], .stApp input[type="radio"] { accent-color: var(--planner-button); color-scheme: light; }
    .stApp [data-testid="stSlider"] [role="slider"] { background: var(--planner-button) !important; }
    .stApp [data-testid="stExpander"] details,
    .stApp [data-testid="stExpander"] summary {
        background: var(--planner-card) !important;
        color: var(--planner-text) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--planner-card) !important; border: 1px solid var(--planner-border) !important;
        border-radius: 15px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div { background: transparent !important; border-color: transparent !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"],
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"],
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stWidgetLabel"] p { color: var(--planner-text) !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"],
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"] { color: var(--planner-text) !important; }
    div[data-testid="stExpander"] { background: var(--planner-card); border: 1px solid var(--planner-border); border-radius: 13px; }
    div[data-testid="stExpander"] summary, div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] [data-testid="stMarkdownContainer"] { color: var(--planner-text) !important; }
    .assignment-card {
        border: 1px solid var(--planner-border); border-radius: 16px;
        background: linear-gradient(145deg, var(--planner-card), var(--planner-card));
        padding: 17px 18px; margin: 0 0 8px 0; min-height: 220px;
    }
    .assignment-card.due-today {
        border: 3px solid var(--planner-button);
        box-shadow: 0 0 0 1px color-mix(in srgb, var(--planner-button) 18%, transparent), 0 7px 20px color-mix(in srgb, var(--planner-text) 16%, transparent);
    }
    .due-today-tag {
        display: inline-block; color: var(--planner-text); border: 1px solid var(--planner-border);
        background: var(--planner-surface); border-radius: 999px;
        padding: 3px 9px; font-size: .72rem; font-weight: 800;
        letter-spacing: .06em; text-transform: uppercase; margin-left: 8px;
        vertical-align: middle;
    }
    .target-line { display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }

    .assignment-title {
        display: inline-block; color: var(--planner-card_text); font-size: 1.22rem;
        line-height: 1.35; font-weight: 750; padding: 9px 15px;
        border-radius: 10px; margin-bottom: 12px;
        overflow-wrap: anywhere;
    }
    .target-label {
        color: var(--planner-text); text-transform: uppercase; letter-spacing: .11em;
        font-size: .78rem; font-weight: 750; margin-top: 2px;
    }
    .target-number {
        color: var(--planner-card_text); font-size: 2.65rem; line-height: 1.12;
        font-weight: 850; letter-spacing: -.05em; margin: 4px 0 5px 0;
    }
    .target-unit { color: var(--planner-text); font-size: 1.35rem; font-weight: 700; letter-spacing: -.02em; }
    .assignment-meta { color: var(--planner-text); font-size: .9rem; margin-top: 7px; }
    .historical-progress {
        display: inline-flex; margin-top: 10px; padding: 5px 10px;
        border: 1px solid var(--planner-border); border-radius: 999px;
        background: var(--planner-surface); color: var(--planner-card_text); font-size: .8rem;
    }
    .today-progress-label { color: var(--planner-text); font-size: .88rem; font-weight: 650; }
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
    return {"assignments": [], "calendar_events": [], "calendar_name": None}


def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def save_course_settings(course_name):
    """Persist edited course fields as soon as a widget change is committed."""
    categories = data.get("course_categories", {})
    if course_name not in categories:
        return

    name_key = f"category_name_{course_name}"
    color_key = f"category_color_{course_name}"
    days_key = f"category_meeting_days_{course_name}"
    prep_key = f"category_prep_days_{course_name}"
    review_key = f"category_review_days_{course_name}"
    new_name = str(st.session_state.get(name_key, course_name)).strip()
    if not new_name:
        st.session_state[name_key] = course_name
        st.session_state["course_edit_error"] = "Course names cannot be blank."
        return
    if any(name != course_name and name.casefold() == new_name.casefold() for name in categories):
        st.session_state[name_key] = course_name
        st.session_state["course_edit_error"] = f"{new_name} is already in your course list."
        return

    new_color = st.session_state.get(color_key, categories[course_name])
    meeting_days = st.session_state.get(days_key, data["course_meeting_days"].get(course_name, []))
    prep_days = int(st.session_state.get(prep_key, data["course_prep_days_before"].get(course_name, 1)))
    prep_days = -1 if prep_days < 0 else min(14, max(0, prep_days))
    review_days = int(st.session_state.get(review_key, data["course_review_days_after"].get(course_name, 1)))
    review_days = min(14, max(0, review_days))

    updated_categories = {
        (new_name if name == course_name else name):
        (new_color if name == course_name else color)
        for name, color in categories.items()
    }
    if new_name != course_name:
        for linked_data_key in (
            "class_topics", "course_meeting_days", "course_prep_days_before",
            "course_review_days_after",
        ):
            linked_data = data.setdefault(linked_data_key, {})
            if course_name in linked_data:
                linked_data[new_name] = linked_data.pop(course_name)
        for assignment in data.get("assignments", []):
            if assignment.get("course") == course_name:
                assignment["course"] = new_name
        for lecture_task in data.get("lecture_tasks", []):
            if lecture_task.get("course") == course_name:
                lecture_task["course"] = new_name
                lecture_task["id"] = lecture_task["id"].replace(f"{course_name}|", f"{new_name}|", 1)
        for widget_key in ("topic_manager_course", "new_course"):
            if st.session_state.get(widget_key) == course_name:
                st.session_state[widget_key] = new_name
        for assignment in data.get("assignments", []):
            assignment_course_key = f"course_{assignment.get('id')}"
            if st.session_state.get(assignment_course_key) == course_name:
                st.session_state[assignment_course_key] = new_name

    data["course_categories"] = updated_categories
    data["course_meeting_days"][new_name] = list(meeting_days)
    data["course_prep_days_before"][new_name] = prep_days
    data["course_review_days_after"][new_name] = review_days
    COURSE_COLORS.clear()
    COURSE_COLORS.update(updated_categories)
    COURSES[:] = list(COURSE_COLORS)
    save_data(data)
    st.session_state["course_autosave_notice"] = f"{new_name} saved"


def delete_course_settings(course_name):
    categories = data.get("course_categories", {})
    if len(categories) <= 1:
        st.session_state["course_edit_error"] = "Keep at least one course or category."
        return

    remaining_categories = {name: color for name, color in categories.items() if name != course_name}
    replacement_course = next(iter(remaining_categories))
    for assignment in data.get("assignments", []):
        if assignment.get("course") == course_name:
            assignment["course"] = replacement_course
            assignment_course_key = f"course_{assignment.get('id')}"
            if st.session_state.get(assignment_course_key) == course_name:
                st.session_state[assignment_course_key] = replacement_course
    for widget_key in ("topic_manager_course", "new_course"):
        if st.session_state.get(widget_key) == course_name:
            st.session_state[widget_key] = replacement_course

    data.get("class_topics", {}).pop(course_name, None)
    data.get("course_meeting_days", {}).pop(course_name, None)
    data.get("course_prep_days_before", {}).pop(course_name, None)
    data.get("course_review_days_after", {}).pop(course_name, None)
    data["lecture_tasks"] = [
        task for task in data.get("lecture_tasks", []) if task.get("course") != course_name
    ]
    data["course_categories"] = remaining_categories
    COURSE_COLORS.clear()
    COURSE_COLORS.update(remaining_categories)
    COURSES[:] = list(COURSE_COLORS)
    save_data(data)
    st.session_state["course_autosave_notice"] = f"{course_name} deleted"


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


def daily_calendar_free_hours(day, events, ignore_gap_minutes):
    day_start = datetime.combine(day, time.min)
    day_end = day_start + timedelta(days=1)
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
    return max(0.0, free_minutes / 60 - SLEEP_HOURS_PER_DAY)


def get_calendar_estimate_hours(day, settings, events, has_calendar):
    """Estimate free time across the whole day, reserving eight hours for sleep."""
    return daily_calendar_free_hours(day, events, settings["ignore_gap_minutes"])


def get_daily_availability_hours(day, settings, events, has_calendar):
    """Use the calendar-based daily estimate for scheduling."""
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

        today_done = float(assignment.get("today_completed", 0))
        eligible = [
            d for d in days
            if max(today, start) <= d["date"] <= due and d["availability_weight"] > 0
        ]
        today_is_eligible = bool(eligible and eligible[0]["date"] == today)

        def allocate(amount, available_days):
            """Return this assignment's usual daily split across the given days."""
            amount = max(0.0, float(amount))
            total_weight = sum(day_info["availability_weight"] for day_info in available_days)
            if amount <= 0 or not available_days or total_weight <= 0:
                return [0] * len(available_days)
            if is_percentage:
                shares = [amount * day_info["availability_weight"] / total_weight for day_info in available_days]
                targets = [int(math.floor(value)) for value in shares]
                points_left = int(round(amount)) - sum(targets)
                order = sorted(range(len(shares)), key=lambda i: shares[i] - targets[i], reverse=True)
                for index in order[:max(0, points_left)]:
                    targets[index] += 1
                return targets

            total_units = int(amount)
            units_left = total_units
            targets = []
            for day_info in available_days:
                if units_left <= 0:
                    targets.append(0)
                    continue
                ideal_share = total_units * day_info["availability_weight"] / total_weight
                target = min(units_left, max(1, math.ceil(ideal_share)))
                targets.append(target)
                units_left -= target
            return targets

        if remaining > 0 and eligible:
            # Include today's completed work when calculating the daily split.
            # That keeps today's target stable across multiple progress updates.
            work_at_start_of_today = remaining + today_done if today_is_eligible else remaining
            scheduled_targets = allocate(work_at_start_of_today, eligible)
            future_days = eligible[1:] if today_is_eligible else eligible
            future_work = remaining

            if today_is_eligible:
                today_target = scheduled_targets[0]
                still_due_today = max(0, today_target - today_done)
                future_work = max(0, remaining - still_due_today)
                if still_due_today > 0:
                    item = {
                        "assignment_id": assignment["id"], "name": assignment["name"],
                        "mode": "percentage" if is_percentage else "units",
                    }
                    if is_percentage:
                        item["percent"] = today_target
                    else:
                        item["units"] = today_target
                        item["unit"] = assignment["unit"]
                    plan[today.isoformat()].append(item)

            future_targets = allocate(future_work, future_days)
            for day_info, target in zip(future_days, future_targets):
                if target <= 0:
                    continue
                item = {
                    "assignment_id": assignment["id"], "name": assignment["name"],
                    "mode": "percentage" if is_percentage else "units",
                }
                if is_percentage:
                    item["percent"] = target
                else:
                    item["units"] = target
                    item["unit"] = assignment["unit"]
                plan[day_info["date"].isoformat()].append(item)
            remaining = max(0.0, future_work - sum(future_targets))

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
saved_prep_offsets = data.get("course_prep_days_before", {})
if not isinstance(saved_prep_offsets, dict):
    saved_prep_offsets = {}
data["course_prep_days_before"] = {}
for course_name in COURSE_COLORS:
    try:
        prep_days_before = int(saved_prep_offsets.get(course_name, 1))
    except (TypeError, ValueError):
        prep_days_before = 1
    data["course_prep_days_before"][course_name] = -1 if prep_days_before < 0 else min(14, max(0, prep_days_before))
saved_review_offsets = data.get("course_review_days_after", {})
if not isinstance(saved_review_offsets, dict):
    saved_review_offsets = {}
data["course_review_days_after"] = {}
for course_name in COURSE_COLORS:
    try:
        review_days_after = int(saved_review_offsets.get(course_name, 1))
    except (TypeError, ValueError):
        review_days_after = 1
    data["course_review_days_after"][course_name] = min(14, max(0, review_days_after))
if not isinstance(data.get("lecture_tasks"), list):
    data["lecture_tasks"] = []
saved_theme = data.get("app_theme")
if not isinstance(saved_theme, dict):
    saved_theme = {}
app_theme = dict(APP_THEME_DEFAULTS)
for theme_key, theme_value in saved_theme.items():
    if theme_key in app_theme and isinstance(theme_value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", theme_value):
        app_theme[theme_key] = theme_value.upper()
if "hover" not in saved_theme:
    saved_theme_background = saved_theme.get("background")
    matching_palette = next(
        (palette for palette in APP_THEME_PALETTES.values()
         if isinstance(saved_theme_background, str)
         and saved_theme_background.upper() == palette["background"]),
        None,
    )
    if matching_palette:
        app_theme["hover"] = matching_palette["hover"]
data["app_theme"] = dict(app_theme)
if st.session_state.pop("refresh_theme_widgets_pending", False):
    for theme_widget_key in (
        "theme_background", "theme_sidebar", "theme_text", "theme_border",
        "theme_button", "theme_button_text", "theme_card", "theme_card_text",
        "theme_input", "theme_surface", "theme_dropdown", "theme_progress", "theme_hover",
    ):
        st.session_state.pop(theme_widget_key, None)
data.setdefault("planner_settings", {})

st.markdown(f"""
<style>
    :root {{
        --primary-color: {app_theme['button']};
        --planner-background: {app_theme['background']};
        --planner-sidebar: {app_theme['sidebar']};
        --planner-text: {app_theme['text']};
        --planner-button: {app_theme['button']};
        --planner-button_text: {app_theme['button_text']};
        --planner-card: {app_theme['card']};
        --planner-card_text: {app_theme['card_text']};
        --planner-input: {app_theme['input']};
        --planner-border: {app_theme['border']};
        --planner-surface: {app_theme['surface']};
        --planner-dropdown: {app_theme['dropdown']};
        --planner-progress: {app_theme['progress']};
        --planner-hover: {app_theme['hover']};
    }}
    .stApp, [data-testid="stAppViewContainer"] {{
        --primary-color: {app_theme['button']} !important;
        background: {app_theme['background']} !important;
        color: {app_theme['text']} !important;
    }}
    [data-testid="stHeader"] {{ background: {app_theme['background']} !important; }}
    #MainMenu, footer, .stDeployButton, [data-testid="stToolbar"],
    [data-testid="stToolbarActions"], [data-testid="stDecoration"] {{
        display: none !important;
        visibility: hidden !important;
    }}
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
    .stApp [data-testid="stExpander"] summary {{ background: {app_theme['dropdown']} !important; }}
    .stApp [data-testid="stExpander"] details {{ background: {app_theme['surface']} !important; }}
    .stApp [data-testid="stExpander"] details > summary,
    div[data-testid="stExpander"] details > summary {{
        background: {app_theme['dropdown']} !important;
    }}
    [data-testid="stForm"], [data-testid="stAlert"],
    [data-testid="stFileUploaderDropzone"],
    div[data-testid="stExpander"],
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {app_theme['surface']} !important;
        border-color: {app_theme['border']} !important;
    }}
    .stApp button, .stApp [data-testid="stFormSubmitButton"] button,
    .stApp button[kind="primary"], .stApp button[kind="secondary"] {{
        background: {app_theme['button']} !important;
        color: {app_theme['button_text']} !important;
        border-color: {app_theme['border']} !important;
    }}
    div[data-testid="stProgress"] > div > div {{
        background: {app_theme['progress']} !important;
    }}
    div[data-testid="stMetric"] {{
        background: {app_theme['card']} !important;
        border-color: {app_theme['border']} !important;
        color: {app_theme['card_text']} !important;
    }}
    div[data-testid="stMetricLabel"], div[data-testid="stMetricValue"] {{
        color: {app_theme['card_text']} !important;
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
    .stApp [data-testid="stDateInput"] [data-baseweb="input"] div {{
        background-color: {app_theme['input']} !important;
        color: {app_theme['text']} !important;
        border-color: {app_theme['border']} !important;
    }}
    .stApp [data-testid="stSelectbox"] [data-baseweb="select"],
    .stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    .stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div > div {{
        background: {app_theme['dropdown']} !important;
        background-color: {app_theme['dropdown']} !important;
        color: {app_theme['text']} !important;
    }}
    .stApp [data-testid="stDateInput"] [data-baseweb="input"],
    .stApp [data-testid="stDateInput"] [data-baseweb="input"] > div,
    .stApp [data-testid="stDateInput"] [data-baseweb="input"] input {{
        background: {app_theme['input']} !important;
        background-color: {app_theme['input']} !important;
        color: {app_theme['text']} !important;
    }}
    /* Streamlit/BaseWeb adds nested wrappers with their own default beige fill.
       Theme every wrapper in these controls, then restore the intentional button
       colors for dropdown arrows, date-picker icons, and weekday chips. */
    .stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    .stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
    .stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div > div > div,
    .stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div *:not(button):not(svg),
    .stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
    .stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div > div,
    .stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div > div > div,
    .stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div *:not(button):not(svg) {{
        background: {app_theme['dropdown']} !important;
        background-color: {app_theme['dropdown']} !important;
    }}
    .stApp [data-testid="stSelectbox"] [data-baseweb="select"] button,
    .stApp [data-testid="stMultiSelect"] [data-baseweb="select"] button {{
        background: {app_theme['button']} !important;
        background-color: {app_theme['button']} !important;
        color: {app_theme['button_text']} !important;
    }}
    .stApp [data-testid="stDateInput"] [data-baseweb="input"] > div,
    .stApp [data-testid="stDateInput"] [data-baseweb="input"] > div > div,
    .stApp [data-testid="stDateInput"] [data-baseweb="input"] > div > div > div,
    .stApp [data-testid="stDateInput"] [data-baseweb="input"] *:not(button):not(svg),
    .stApp [data-testid="stDateInput"] [data-baseweb="input"] input {{
        background: {app_theme['input']} !important;
        background-color: {app_theme['input']} !important;
    }}
    .stApp [data-testid="stDateInput"] [data-baseweb="input"] button {{
        background: {app_theme['surface']} !important;
        background-color: {app_theme['surface']} !important;
    }}
    .stApp [data-testid="stMultiSelect"] [data-baseweb="tag"] {{
        background: {app_theme['button']} !important;
        background-color: {app_theme['button']} !important;
        color: {app_theme['button_text']} !important;
        border-radius: 8px !important;
    }}
    .stApp [data-testid="stMultiSelect"] [data-baseweb="tag"] *,
    .stApp [data-testid="stMultiSelect"] [data-baseweb="tag"] button,
    .stApp [data-testid="stMultiSelect"] [data-baseweb="tag"] svg {{
        background: transparent !important;
        color: {app_theme['button_text']} !important;
        fill: {app_theme['button_text']} !important;
    }}
    .stApp [data-testid="stMultiSelect"] input {{
        background: transparent !important;
        color: {app_theme['text']} !important;
        min-width: 2px !important;
        width: auto !important;
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
        background: {app_theme['dropdown']} !important;
        color: {app_theme['text']} !important;
    }}
    .stApp [data-baseweb="popover"] [role="option"]:hover,
    .stApp [data-baseweb="popover"] [aria-selected="true"] {{
        background: {app_theme['hover']} !important;
        color: {app_theme['text']} !important;
    }}
    .stApp button:hover,
    .stApp [role="button"]:hover,
    .stApp [role="gridcell"]:hover,
    .stApp [data-baseweb="popover"] [role="option"]:hover,
    .stApp [data-baseweb="popover"] [aria-selected="true"],
    .stApp [data-testid="stExpander"] summary:hover,
    .stApp [data-testid="stExpander"] details > summary:hover,
    div[data-testid="stExpander"] details > summary:hover,
    .stApp details > summary:hover,
    .stApp [data-testid="stSelectbox"] [data-baseweb="select"]:hover,
    .stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div:hover,
    .stApp [data-testid="stMultiSelect"] [data-baseweb="select"]:hover,
    .stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div:hover,
    .stApp [data-testid="stDateInput"] [data-baseweb="input"]:hover,
    .stApp [data-testid="stNumberInput"] [data-baseweb="input"]:hover,
    .stApp [data-testid="stTextInput"] [data-baseweb="input"]:hover,
    .stApp [data-testid="stTextArea"] [data-baseweb="textarea"]:hover,
    .stApp [data-testid="stNumberInput"] button:hover,
    .stApp [data-testid="stTimeInput"] button:hover,
    .stApp [data-testid="stDateInput"] button:hover,
    .stApp [data-testid="stMultiSelect"] [data-baseweb="tag"] button:hover,
    .stApp [data-testid="stSidebar"] button:hover,
    .stApp [data-testid="stForm"] button:hover,
    .stApp [data-testid="stFileUploaderDropzone"]:hover,
    .stApp [data-testid="stFileUploaderDropzone"] button:hover {{
        background: {app_theme['hover']} !important;
        background-color: {app_theme['hover']} !important;
        color: {app_theme['text']} !important;
    }}
    .stApp button:hover *,
    .stApp [role="button"]:hover * {{
        color: {app_theme['text']} !important;
        fill: {app_theme['text']} !important;
    }}
    .assignment-card {{
        background: {app_theme['card']} !important;
        border-color: {app_theme['border']} !important;
        color: {app_theme['card_text']} !important;
    }}
    .assignment-card.due-today {{ border-color: {app_theme['button']} !important; }}
    .assignment-card .target-number, .assignment-card .target-unit,
    .assignment-card .target-label, .assignment-card .assignment-meta,
    .assignment-card .historical-progress {{ color: {app_theme['card_text']} !important; }}
    .assignment-card .historical-progress {{
        background: {app_theme['surface']} !important;
        border-color: {app_theme['border']} !important;
    }}
    /* BaseWeb's control markup differs between Streamlit releases. These
       palette rules target the rendered BaseWeb elements directly, without
       relying on Streamlit's changing widget test IDs. */
    .stApp [data-baseweb="select"],
    .stApp [data-baseweb="select"] > div,
    .stApp [data-baseweb="select"] > div > div:first-child,
    .stApp [data-baseweb="select"] > div > div:first-child > div {{
        background-color: {app_theme['dropdown']} !important;
    }}
    .stApp [data-baseweb="tag"] {{
        background: {app_theme['button']} !important;
        background-color: {app_theme['button']} !important;
        color: {app_theme['button_text']} !important;
    }}
    .stApp [data-baseweb="tag"] * {{
        background: transparent !important;
        color: {app_theme['button_text']} !important;
        fill: {app_theme['button_text']} !important;
    }}
    .stApp [data-baseweb="input"],
    .stApp [data-baseweb="input"] > div,
    .stApp [data-baseweb="input"] > div > div,
    .stApp [data-baseweb="input"] input,
    .stApp [data-baseweb="input"] textarea {{
        background-color: {app_theme['input']} !important;
        color: {app_theme['text']} !important;
    }}
    .stApp [data-baseweb="input"] button {{
        background-color: {app_theme['surface']} !important;
        color: {app_theme['text']} !important;
    }}
</style>
""", unsafe_allow_html=True)

saved_planner_settings = data.get("planner_settings", {})
if not isinstance(saved_planner_settings, dict):
    saved_planner_settings = {}
try:
    ignore_gap_minutes = min(120, max(0, int(saved_planner_settings.get("ignore_gap_minutes", 30))))
except (TypeError, ValueError):
    ignore_gap_minutes = 30
settings = {"ignore_gap_minutes": ignore_gap_minutes}
data["planner_settings"] = {"ignore_gap_minutes": ignore_gap_minutes}
data.pop("daily_availability_overrides", None)

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
        st.info("No calendar imported. Free-time estimates start at 16 hours per day after reserving 8 hours for sleep.")

    st.divider()

# Read-only date-by-date availability estimates.
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

with st.sidebar:
    with st.expander("Free time per day", expanded=True):
        st.caption("Calendar events and short gaps count as busy time; 8 hours are reserved each day for sleep.")
        header = st.columns([1.4, 1])
        header[0].markdown("**Date**")
        header[1].markdown("**Free time**")
        current_day = today_for_availability
        while current_day <= last_availability_day:
            estimate = get_calendar_estimate_hours(
                current_day, settings, data["calendar_events"], bool(data["calendar_name"])
            )
            row = st.columns([1.4, 1])
            row[0].write(current_day.strftime("%a %b ") + str(current_day.day))
            row[1].write(f"{estimate:.1f} h")
            current_day += timedelta(days=1)

save_data(data)
today = date.today()

# Create class-prep tasks for the next lecture and notes-review tasks for the
# previous lecture. Unfinished tasks roll forward without recreating history.
lecture_tasks_by_key = {
    task.get("id"): task for task in data["lecture_tasks"]
    if isinstance(task, dict) and task.get("id")
}
courses_without_prep = {
    course_name for course_name, prep_offset in data["course_prep_days_before"].items()
    if prep_offset < 0
}
if courses_without_prep:
    data["lecture_tasks"] = [
        task for task in data["lecture_tasks"]
        if not (
            task.get("course") in courses_without_prep
            and task.get("type") == "lecture_prep"
            and not task.get("completed")
        )
    ]
    lecture_tasks_by_key = {
        task.get("id"): task for task in data["lecture_tasks"]
        if isinstance(task, dict) and task.get("id")
    }
for course_name, meeting_days in data["course_meeting_days"].items():
    prep_days_before = data["course_prep_days_before"].get(course_name, 1)
    review_days_after = data["course_review_days_after"].get(course_name, 1)
    # Generate a short rolling window so Schedule can show upcoming work too.
    for day_offset in range(-1, 22):
        class_date = today + timedelta(days=day_offset)
        if class_date.strftime("%A") not in meeting_days:
            continue
        task_types = ["lecture_notes_review"]
        if prep_days_before >= 0:
            task_types.insert(0, "lecture_prep")
        for task_type in task_types:
            if task_type == "lecture_prep":
                target_due_date = class_date - timedelta(days=prep_days_before)
                # If the prep window has already started, keep the work due today.
                due_date = max(today, target_due_date)
                if class_date < today and target_due_date < today:
                    continue
            else:
                due_date = class_date + timedelta(days=review_days_after)
                if due_date < today:
                    continue
            task_id = f"{course_name}|{task_type}|{class_date.isoformat()}"
            existing_task = lecture_tasks_by_key.get(task_id)
            if existing_task:
                if not existing_task.get("completed") and class_date >= today:
                    existing_task["due_date"] = due_date.isoformat()
                continue
            else:
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

# Assignment creation
with st.expander("＋ Add an assignment", expanded=not data["assignments"]):
    # Keep this selector outside the form so changing it immediately switches fields.
    mode = st.radio(
        "Progress type",
        ["Units (questions, problems, pages)", "Percentage (0–100%)"],
        horizontal=True,
        key="new_assignment_mode",
    )
    if st.session_state.pop("reset_recurring_assignment_form", False):
        for state_key in list(st.session_state):
            if state_key.startswith(("recurring_name_", "recurring_due_", "recurring_start_")):
                st.session_state.pop(state_key, None)
        for state_key in (
            "recurring_occurrences",
            "recurring_course", "recurring_total_units", "recurring_unit",
            "recurring_completed_units", "recurring_completed_percent",
            "new_assignment_recurring",
        ):
            st.session_state.pop(state_key, None)

    recurring = st.checkbox("This assignment repeats", key="new_assignment_recurring")
    if recurring:
        occurrence_count = int(st.number_input(
            "Number of due dates", min_value=2, max_value=20, value=2, step=1,
            key="recurring_occurrences",
        ))
        course = st.selectbox("Course / category", COURSES, key="recurring_course")

        if mode.startswith("Units"):
            unit_columns = st.columns(3)
            total_units = unit_columns[0].number_input(
                "Total units for each", min_value=1, value=10, step=1,
                key="recurring_total_units",
            )
            unit = unit_columns[1].selectbox(
                "Unit type", ["Questions", "Pages", "Chapters", "Problems", "Other"],
                key="recurring_unit",
            )
            completed_before = unit_columns[2].number_input(
                "Already completed for each", min_value=0, value=0, step=1,
                key="recurring_completed_units",
            )
            completed_percent = 0
        else:
            total_units = 0
            unit = "Questions"
            completed_before = 0
            completed_percent = st.number_input(
                "Current completion for each (%)", min_value=0, max_value=100, value=0, step=1,
                key="recurring_completed_percent",
            )

        st.caption("Add a name, start date, and due date for each assignment. Each start date defaults to the previous assignment's due date, and you can change any date.")
        occurrence_names = []
        occurrence_starts = []
        occurrence_dues = []
        for occurrence_index in range(occurrence_count):
            previous_due = occurrence_dues[-1] if occurrence_dues else None
            default_due = (previous_due + timedelta(days=7)) if previous_due else today + timedelta(days=7)
            name_col, start_col, due_col = st.columns([1.6, 1, 1])
            occurrence_number = occurrence_index + 1
            occurrence_names.append(name_col.text_input(
                f"Assignment {occurrence_number} name",
                key=f"recurring_name_{occurrence_index}",
            ))
            start_key = f"recurring_start_{occurrence_index}"
            auto_start = previous_due if previous_due else today
            last_auto_start = st.session_state.get(f"{start_key}_auto")
            current_start = st.session_state.get(start_key)
            if current_start is None or current_start == last_auto_start:
                st.session_state[start_key] = auto_start
            st.session_state[f"{start_key}_auto"] = auto_start
            start_date = start_col.date_input("Start date", key=start_key)
            occurrence_starts.append(start_date)
            occurrence_dues.append(due_col.date_input(
                "Due date", value=default_due, key=f"recurring_due_{occurrence_index}",
            ))

        if st.button("Save recurring assignments", type="primary", key="save_recurring_assignments"):
            validation_error = None
            if any(not assignment_name.strip() for assignment_name in occurrence_names):
                validation_error = "Enter a name for every assignment."
            elif mode.startswith("Units") and completed_before > total_units:
                validation_error = "Completed units cannot exceed the total units for each assignment."
            else:
                for occurrence_index, (start_date, due_date) in enumerate(zip(occurrence_starts, occurrence_dues)):
                    if due_date < start_date:
                        validation_error = f"Assignment {occurrence_index + 1} is due before its start date."
                        break
                    if occurrence_index and due_date < occurrence_dues[occurrence_index - 1]:
                        validation_error = "Keep the due dates in order from earliest to latest."
                        break

            if validation_error:
                st.error(validation_error)
            else:
                series_id = str(uuid.uuid4())
                for occurrence_index, (assignment_name, start_date, due_date) in enumerate(
                    zip(occurrence_names, occurrence_starts, occurrence_dues), start=1
                ):
                    assignment = {
                        "id": str(uuid.uuid4()), "name": assignment_name.strip(), "course": course,
                        "mode": "units" if mode.startswith("Units") else "percentage",
                        "start_date": start_date.isoformat(), "due_date": due_date.isoformat(),
                        "today_completed": 0, "today_date": today.isoformat(),
                        "recurring_group_id": series_id,
                        "recurring_occurrence": occurrence_index,
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
                st.session_state["reset_recurring_assignment_form"] = True
                st.success(f"Saved {occurrence_count} recurring assignments.")
                st.rerun()
    else:
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

tab_today, tab_assignments, tab_class_test_prep, tab_schedule, tab_courses, tab_appearance = st.tabs(
    ["Today", "Assignments", "Class & Test Prep", "Schedule", "Courses", "Appearance"]
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
            completion_label = "Mark review done" if lecture_task.get("type") == "lecture_notes_review" else "Mark done"
            if done_col.button(completion_label, key=f"complete_lecture_{lecture_task['id']}", use_container_width=True):
                lecture_task["completed"] = True
                lecture_task["completed_date"] = today.isoformat()
                save_data(data)
                completion_message = "Lecture review recorded." if lecture_task.get("type") == "lecture_notes_review" else f"{title} complete!"
                st.toast(completion_message, icon="✅")
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
                completed_today = int(assignment.get("today_completed", 0))
                if item.get("mode") == "percentage":
                    daily_target = int(item["percent"])
                    remaining_today = max(0, daily_target - completed_today)
                    target_text, unit_label = f"{remaining_today}%", "completion"
                else:
                    daily_target = int(item["units"])
                    remaining_today = max(0, daily_target - completed_today)
                    unit_label = item["unit"].lower()
                    if remaining_today == 1 and unit_label.endswith("s"):
                        unit_label = unit_label[:-1]
                    elif remaining_today != 1 and not unit_label.endswith("s"):
                        unit_label += "s"
                    target_text = str(remaining_today)

                st.markdown(
                    f"""
                    <div class="{card_class}">
                        <div class="assignment-title" style="background:{course_color};">{html.escape(item['name'])}</div>{due_tag}
                        <div class="target-label">Left to do today</div>
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
                    progress_col.markdown('<div class="today-progress-label">Total completed today</div>', unsafe_allow_html=True)
                    if assignment.get("mode") == "percentage":
                        amount = progress_col.number_input(
                            "Total percentage completed today", min_value=0, max_value=100,
                            value=int(assignment.get("today_completed", 0)), step=1,
                            key=f"today_{assignment['id']}", label_visibility="collapsed"
                        )
                    else:
                        amount = progress_col.number_input(
                            "Total units completed today", min_value=0,
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
                        st.toast("Progress updated.", icon="✅")
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
    st.caption("Manage course topics here. Choose a class date from the meeting days configured in Courses, then add, edit, or remove topics.")

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
                st.info("Set this course's meeting days in the Courses tab before adding a dated topic.")
            add_topic = st.form_submit_button("Add topic", type="primary")
            cancel_topic = st.form_submit_button("Cancel")
            if add_topic:
                normalized_topic_name = new_topic_name.strip()
                if not normalized_topic_name:
                    st.error("Enter a topic name.")
                elif not selected_meeting_days:
                    st.error("Set this course's meeting days in the Courses tab first.")
                elif topic_class_date.strftime("%A") not in selected_meeting_days:
                    st.error("Choose a class date that matches this course's meeting days in the Courses tab.")
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
                    date_col.caption("Set meeting days in Courses to choose a date.")
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
                        st.error("Set this course's meeting days in the Courses tab first.")
                    elif edited_class_date.strftime("%A") not in topic_meeting_days:
                        st.error("Choose a class date that matches this course's meeting days in the Courses tab.")
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
    st.subheader("Schedule")
    schedule_view_mode = st.radio(
        "Schedule view", ["List", "Calendar"], horizontal=True, key="schedule_view_mode"
    )
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

    if schedule_view_mode == "List":
        st.caption("Upcoming assignments, lecture prep, and lecture reviews.")
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
                                st.markdown(f'<div style="color:{app_theme["button"]};font-weight:750;">• {html.escape(item["name"])}: {detail} — DUE TODAY</div>', unsafe_allow_html=True)
                            else:
                                st.write(f"• {item['name']}: {detail}")

                    class_tasks = lecture_tasks_by_day.get(day_key, [])
                    if class_tasks:
                        st.markdown("**Class prep & review**")
                        class_tasks.sort(key=lambda task: (task.get("type") != "lecture_prep", task.get("course", "")))
                        for lecture_task in class_tasks:
                            course_name = lecture_task.get("course", "")
                            course_color = COURSE_COLORS.get(course_name, app_theme["border"])
                            try:
                                class_date = date.fromisoformat(lecture_task["class_date"])
                            except (KeyError, TypeError, ValueError):
                                class_date = day
                            title = "Lecture prep" if lecture_task.get("type") == "lecture_prep" else "Lecture notes review"
                            related_topics = [
                                topic["name"] for topic in data["class_topics"].get(course_name, [])
                                if topic.get("class_date") == class_date.isoformat()
                            ]
                            detail = ", ".join(related_topics) if related_topics else f"Class on {class_date.strftime('%a, %b %d')}"
                            if lecture_task.get("completed"):
                                status = "✓ Done"
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
    else:
        if not isinstance(st.session_state.get("schedule_calendar_anchor"), date):
            st.session_state["schedule_calendar_anchor"] = today
        calendar_period = st.radio(
            "Calendar view", ["Week", "Month"], horizontal=True, key="schedule_calendar_period"
        )
        previous_col, date_col, today_col, next_col = st.columns([1, 2.8, 1, 1])
        with previous_col:
            st.button(
                "‹ Previous", key="schedule_calendar_previous",
                on_click=shift_schedule_calendar_anchor, args=(-1,),
            )
        with date_col:
            st.date_input(
                "Choose a date", key="schedule_calendar_anchor", label_visibility="collapsed"
            )
        with today_col:
            st.button("Today", key="schedule_calendar_today", on_click=set_schedule_calendar_anchor_today)
        with next_col:
            st.button(
                "Next ›", key="schedule_calendar_next",
                on_click=shift_schedule_calendar_anchor, args=(1,),
            )

        anchor = st.session_state["schedule_calendar_anchor"]
        if calendar_period == "Week":
            week_start = anchor - timedelta(days=anchor.weekday())
            calendar_days = [week_start + timedelta(days=offset) for offset in range(7)]
            st.caption(f"{calendar_days[0].strftime('%b %d')} – {calendar_days[-1].strftime('%b %d, %Y')}")
        else:
            month_weeks = calendar_module.Calendar(firstweekday=calendar_module.MONDAY).monthdatescalendar(
                anchor.year, anchor.month
            )
            calendar_days = [day for week in month_weeks for day in week]
            st.caption(anchor.strftime("%B %Y"))

        def safe_calendar_color(value):
            return value if isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value) else app_theme["button"]

        assignments_by_id = {assignment.get("id"): assignment for assignment in data["assignments"]}
        calendar_markup = [
            '<div style="display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:6px;">'
        ]
        for weekday in WEEKDAY_NAMES:
            calendar_markup.append(
                f'<div style="text-align:center;padding:9px 3px;background:{app_theme["dropdown"]};'
                f'color:{app_theme["text"]};border:1px solid {app_theme["border"]};border-radius:12px;font-weight:700;">'
                f'{html.escape(weekday[:3])}</div>'
            )

        for calendar_day in calendar_days:
            day_key = calendar_day.isoformat()
            day_style = "" if calendar_period == "Week" or calendar_day.month == anchor.month else "opacity:.55;"
            today_style = f"border:2px solid {app_theme['button']};" if calendar_day == today else f"border:1px solid {app_theme['border']};"
            blocks = []
            for plan_item in plan.get(day_key, []):
                assignment = assignments_by_id.get(plan_item.get("assignment_id"), {})
                course_name = assignment.get("course", "")
                course_color = safe_calendar_color(COURSE_COLORS.get(course_name, app_theme["button"]))
                if plan_item.get("mode") == "percentage":
                    detail = f"{plan_item.get('percent', 0)}%"
                else:
                    detail = f"{plan_item.get('units', 0)} {plan_item.get('unit', 'units')}"
                is_due = False
                try:
                    is_due = date.fromisoformat(assignment.get("due_date", "")) == calendar_day
                except (TypeError, ValueError):
                    pass
                block_title = html.escape(assignment.get("name", plan_item.get("name", "Assignment")))
                block_detail = "Due · " + detail if is_due else detail
                course_label = f'<span style="font-weight:750;color:{course_color};">{html.escape(course_name)}</span>' if course_name else "Assignment"
                blocks.append(
                    f'<div style="background:{app_theme["surface"]};color:{app_theme["text"]};border:1px solid {app_theme["border"]};'
                    f'border-left:4px solid {course_color};border-radius:9px;padding:5px 6px;margin-top:5px;font-size:12px;line-height:1.3;overflow-wrap:anywhere;">'
                    f'<div style="font-weight:700;">{block_title}</div><div>{course_label} · {html.escape(block_detail)}</div></div>'
                )
            for lecture_task in lecture_tasks_by_day.get(day_key, []):
                course_name = lecture_task.get("course", "")
                course_color = safe_calendar_color(COURSE_COLORS.get(course_name, app_theme["button"]))
                try:
                    class_date = date.fromisoformat(lecture_task.get("class_date", ""))
                except (TypeError, ValueError):
                    class_date = calendar_day
                related_topics = [
                    topic.get("name", "") for topic in data["class_topics"].get(course_name, [])
                    if topic.get("class_date") == class_date.isoformat()
                ]
                detail = ", ".join(related_topics) if related_topics else f"Class {class_date.strftime('%b %d')}"
                title = "Lecture prep" if lecture_task.get("type") == "lecture_prep" else "Lecture notes review"
                if lecture_task.get("completed"):
                    title = "✓ " + title
                blocks.append(
                    f'<div style="background:{app_theme["surface"]};color:{app_theme["text"]};border:1px solid {app_theme["border"]};'
                    f'border-left:4px solid {course_color};border-radius:9px;padding:5px 6px;margin-top:5px;font-size:12px;line-height:1.3;overflow-wrap:anywhere;">'
                    f'<div style="font-weight:700;">{html.escape(title)}</div>'
                    f'<div><span style="font-weight:750;color:{course_color};">{html.escape(course_name)}</span> · {html.escape(detail)}</div></div>'
                )
            calendar_markup.append(
                f'<div style="{today_style}{day_style}background:{app_theme["surface"]};color:{app_theme["text"]};'
                f'border-radius:13px;padding:7px;min-height:{125 if calendar_period == "Week" else 118}px;min-width:0;">'
                f'<div style="font-size:13px;font-weight:750;">{calendar_day.day}</div>'
                + "".join(blocks) + "</div>"
            )
        calendar_markup.append("</div>")
        st.markdown("".join(calendar_markup), unsafe_allow_html=True)

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

with tab_appearance:
    st.subheader("Appearance")
    st.caption("Choose a ready-made color palette or customize individual colors. Changes are saved with your data.")
    if palette_notice := st.session_state.pop("theme_palette_notice", None):
        st.toast(palette_notice, icon="✅")
    st.markdown("**Preset palettes**")
    palette_items = list(APP_THEME_PALETTES.items())
    for palette_row_start in range(0, len(palette_items), 4):
        palette_columns = st.columns(4)
        for palette_column, (palette_name, palette) in zip(
            palette_columns, palette_items[palette_row_start:palette_row_start + 4]
        ):
            with palette_column:
                swatches = [palette[key] for key in ("background", "button", "card", "dropdown", "progress", "hover", "border")]
                st.markdown(
                    '<div style="display:flex;height:14px;border-radius:8px;overflow:hidden;'
                    f'border:1px solid {palette["border"]};margin:4px 0 8px 0;">'
                    + "".join(f'<span style="flex:1;background:{color};"></span>' for color in swatches)
                    + "</div>",
                    unsafe_allow_html=True,
                )
                if st.button(f"Use {palette_name}", key=f"use_theme_palette_{palette_name}", use_container_width=True):
                    data["app_theme"] = dict(palette)
                    save_data(data)
                    st.session_state["refresh_theme_widgets_pending"] = True
                    st.session_state["theme_palette_notice"] = f"{palette_name} palette applied."
                    st.rerun()
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
            theme_dropdown = theme_left.color_picker("Dropdowns and expanders", app_theme["dropdown"], key="theme_dropdown")
            theme_progress = theme_right.color_picker("Progress bar", app_theme["progress"], key="theme_progress")
            theme_hover = theme_right.color_picker("Hover and menu highlight", app_theme["hover"], key="theme_hover")
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
                    "dropdown": theme_dropdown,
                    "progress": theme_progress,
                    "hover": theme_hover,
                }
                save_data(data)
                st.toast("Appearance settings saved.", icon="✅")
                st.rerun()

with tab_courses:
    st.subheader("Courses and categories")
    st.caption("Add your own courses, choose their colors, and set the days each course meets.")
    if message := st.session_state.pop("course_autosave_notice", None):
        st.toast(message, icon="✅")
    if error_message := st.session_state.pop("course_edit_error", None):
        st.error(error_message)
    st.caption("Course name, color, meeting days, and lecture prep/review timing save automatically when changed.")
    with st.expander("Add a course or category", expanded=False):
        with st.form("add_course_category", clear_on_submit=True):
            new_category_name = st.text_input("Name")
            new_category_color = st.color_picker("Color", app_theme["button"])
            new_category_meeting_days = st.multiselect("Meets on", WEEKDAY_NAMES, default=[])
            new_category_prep_days = st.selectbox(
                "Lecture prep",
                options=[-1] + list(range(15)),
                index=2,
                format_func=lambda days: "No lecture prep" if days == -1 else "Same day" if days == 0 else f"{days} day{'s' if days != 1 else ''} before class",
            )
            new_category_review_days = st.selectbox(
                "Lecture review",
                options=list(range(15)),
                index=1,
                format_func=lambda days: "Same day" if days == 0 else f"{days} day{'s' if days != 1 else ''} after class",
            )
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
                    data["course_prep_days_before"][normalized_name] = new_category_prep_days
                    data["course_review_days_after"][normalized_name] = new_category_review_days
                    data["course_categories"] = dict(COURSE_COLORS)
                    save_data(data)
                    st.toast(f"{normalized_name} added.", icon="✅")
                    st.rerun()

    for category_name, category_color in list(COURSE_COLORS.items()):
        with st.container(border=True):
            st.markdown(f"**{html.escape(category_name)}**")
            name_col, color_col, prep_col, review_col = st.columns([2.1, 1, 1.25, 1.25])
            name_col.text_input(
                "Course name", category_name,
                key=f"category_name_{category_name}",
                on_change=save_course_settings, args=(category_name,),
            )
            color_col.color_picker(
                "Color", category_color,
                key=f"category_color_{category_name}",
                on_change=save_course_settings, args=(category_name,),
            )
            prep_options = [-1] + list(range(15))
            prep_value = data["course_prep_days_before"].get(category_name, 1)
            prep_col.selectbox(
                "Lecture prep",
                options=prep_options,
                index=prep_options.index(prep_value),
                format_func=lambda days: "No lecture prep" if days == -1 else "Same day" if days == 0 else f"{days} day{'s' if days != 1 else ''} before class",
                key=f"category_prep_days_{category_name}",
                on_change=save_course_settings, args=(category_name,),
            )
            review_col.selectbox(
                "Lecture review",
                options=list(range(15)),
                index=data["course_review_days_after"].get(category_name, 1),
                format_func=lambda days: "Same day" if days == 0 else f"{days} day{'s' if days != 1 else ''} after class",
                key=f"category_review_days_{category_name}",
                on_change=save_course_settings, args=(category_name,),
            )
            st.multiselect(
                "Meets on", WEEKDAY_NAMES,
                default=data["course_meeting_days"].get(category_name, []),
                key=f"category_meeting_days_{category_name}",
                on_change=save_course_settings, args=(category_name,),
            )
            st.button(
                "Delete course", key=f"delete_course_{category_name}",
                on_click=delete_course_settings, args=(category_name,),
            )

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
