import calendar as cal_module
from datetime import datetime

from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup,
)

# ─────────────────────────────────────────────
# USER REPLY KEYBOARD
# ─────────────────────────────────────────────

start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
start_keyboard.add(KeyboardButton("🎂 My Birthday"))
start_keyboard.row(KeyboardButton("➕ Add Event"), KeyboardButton("📅 View Events"))
start_keyboard.row(KeyboardButton("📝 Add Task"), KeyboardButton("✅ View Tasks"))
start_keyboard.add(KeyboardButton("⚙️ Settings"))


# ─────────────────────────────────────────────
# SETTINGS INLINE KEYBOARD
# ─────────────────────────────────────────────

def get_settings_keyboard(notifications_enabled: bool) -> InlineKeyboardMarkup:
    toggle_text = "🔔 Notifications: ON" if notifications_enabled else "🔕 Notifications: OFF"
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="✏️ Edit Birthday", callback_data="edit_birthday"),
        InlineKeyboardButton(text="👥 Friends' Birthdays", callback_data="friends_birthdays")
    )
    keyboard.add(
        InlineKeyboardButton(text=toggle_text, callback_data="toggle_notifications"),
        InlineKeyboardButton(text="📥 Export My Data", callback_data="export_data")
    )
    return keyboard

def make_back_to_settings() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⬅️ Back to Settings", callback_data="settings_back"))
    return kb


# ─────────────────────────────────────────────
# CALENDAR INLINE KEYBOARD
# ─────────────────────────────────────────────

WEEKDAY_LABELS = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


def generate_year_picker(current_page_start: int = None) -> InlineKeyboardMarkup:
    if current_page_start is None:
        current_page_start = (datetime.now().year // 15) * 15 - 15  # Default to recent years
    
    markup = InlineKeyboardMarkup(row_width=3)
    markup.row(InlineKeyboardButton("📅 Select Year", callback_data="ignore"))
    
    years = range(current_page_start, current_page_start + 15)
    row = []
    for y in reversed(list(years)):
        row.append(InlineKeyboardButton(str(y), callback_data=f"set_year:{y}"))
        if len(row) == 3:
            markup.row(*row)
            row = []
    if row:
        markup.row(*row)
        
    markup.row(
        InlineKeyboardButton("◀", callback_data=f"year_page:{current_page_start - 15}"),
        InlineKeyboardButton("▶", callback_data=f"year_page:{current_page_start + 15}")
    )
    markup.row(InlineKeyboardButton("❌ Cancel", callback_data="inline_cancel"))
    return markup

def generate_month_picker(year: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=3)
    markup.row(InlineKeyboardButton(f"📅 Year: {year} | Select Month", callback_data="ignore"))
    
    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    row = []
    for i, m in enumerate(months, 1):
        row.append(InlineKeyboardButton(m, callback_data=f"set_month:{year}-{i}"))
        if len(row) == 3:
            markup.row(*row)
            row = []
            
    markup.row(InlineKeyboardButton("⬅️ Back to Years", callback_data="year_page:default"))
    return markup


def generate_calendar(year: int, month: int, is_birthday: bool = False) -> InlineKeyboardMarkup:
    """
    Build a month-calendar inline keyboard.
    """
    markup = InlineKeyboardMarkup(row_width=7)

    # ── Header: month name + year ──
    month_name = datetime(year, month, 1).strftime("%B %Y")
    markup.row(
        InlineKeyboardButton(f"📅 {month_name}", callback_data="ignore")
    )

    # ── Weekday labels ──
    markup.row(
        *[InlineKeyboardButton(d, callback_data="ignore") for d in WEEKDAY_LABELS]
    )

    # ── Day grid ──
    weeks = cal_module.monthcalendar(year, month)
    for week in weeks:
        row_buttons = []
        for day in week:
            if day == 0:
                row_buttons.append(InlineKeyboardButton(" ", callback_data="ignore"))
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                cb = f"birthday_date:{date_str}" if is_birthday else f"select_date:{date_str}"
                row_buttons.append(
                    InlineKeyboardButton(str(day), callback_data=cb)
                )
        markup.row(*row_buttons)

    # ── Navigation: prev / next month ──
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1

    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    markup.row(
        InlineKeyboardButton("◀", callback_data=f"change_month:{prev_year}-{prev_month}"),
        InlineKeyboardButton("▶", callback_data=f"change_month:{next_year}-{next_month}"),
    )

    if is_birthday:
        markup.row(InlineKeyboardButton("⬅️ Back to Months", callback_data=f"set_year:{year}"))

    # ── Cancel button ──
    markup.row(
        InlineKeyboardButton("❌ Cancel", callback_data="inline_cancel")
    )

    return markup


# ─────────────────────────────────────────────
# ADMIN KEYBOARDS
# ─────────────────────────────────────────────

adminKey = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistics", callback_data="stats")],
        [InlineKeyboardButton(text="📤 Broadcast", callback_data="broadcast")],
        [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")],
    ]
)

settingsKey = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Clear Database", callback_data="clear_db")],
        [
            InlineKeyboardButton(text="➕ Add Admin", callback_data="add_admin"),
            InlineKeyboardButton(text="➖ Remove Admin", callback_data="remove_admin"),
        ],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="goback")],
    ]
)

statsKey = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Refresh", callback_data="update")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="goback")],
    ]
)

adminBack = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="goback")]
    ]
)

dbBack = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="cancel_add_admin")]
    ]
)

ConfirmBroadcast = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm", callback_data="confirm")],
        [InlineKeyboardButton(text="🚫 Cancel", callback_data="decline")],
    ]
)

adminConfirmDB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Yes, clear", callback_data="confirm_clear_db")],
        [InlineKeyboardButton(text="❌ No, go back", callback_data="cancel_clear_db")],
    ]
)

adminCancelKey = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_add_admin")]
    ]
)

backToSettings = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="cancel_add_admin")]
    ]
)