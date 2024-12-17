from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(KeyboardButton("🎂 My Birthday"))  # Add the "My Birthday" button in the first row
start_keyboard.add(KeyboardButton("➕ Add Event"),
                   KeyboardButton("📅 View Events"))
start_keyboard.add(KeyboardButton("📝 Add Task"),
                   KeyboardButton("✅ View Tasks"))
start_keyboard.add(KeyboardButton("⚙️ Settings"))


def get_settings_keyboard(notifications_enabled):
    toggle_text = "🔔 Notifications ON" if notifications_enabled else "🔕 Notifications OFF"
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="✏️ Edit Birthday", callback_data="edit_birthday"),
        InlineKeyboardButton(text=toggle_text, callback_data="toggle_notifications")
    )
    return keyboard


def generate_calendar(year, month):
    markup = InlineKeyboardMarkup(row_width=7)
    days = ["M", "T", "W", "T", "F", "S", "S"]

    # Month Name and Year at the Top
    month_name = datetime(year, month, 1).strftime('%b')  # Short month name (e.g., "Jan")
    markup.row(
        InlineKeyboardButton(f"{month_name}", callback_data="ignore"),
        InlineKeyboardButton(f"{year}", callback_data="ignore")
    )

    # Weekday Header
    markup.row(*[InlineKeyboardButton(day, callback_data="ignore") for day in days])

    # Days in Month
    first_day = datetime(year, month, 1)
    weekday = first_day.weekday()
    days_in_month = (first_day.replace(month=month % 12 + 1, day=1) - timedelta(days=1)).day

    # Fill calendar grid dynamically, skipping completely empty rows
    week = [" " for _ in range(7)]
    for day in range(1, days_in_month + 1):
        week[weekday] = str(day)
        weekday += 1
        if weekday == 7:  # End of the week
            markup.row(*[InlineKeyboardButton(text,
                                              callback_data=f"select_date:{year}-{month:02}-{text}" if text != " " else "ignore")
                         for text in week])
            week = [" " for _ in range(7)]
            weekday = 0

    # Add the last row only if it has valid days
    if any(day != " " for day in week):
        markup.row(*[InlineKeyboardButton(text,
                                          callback_data=f"select_date:{year}-{month:02}-{text}" if text != " " else "ignore")
                     for text in week])

    # Navigation Buttons (Only < and > at the Bottom)
    prev_month = (month - 1) if month > 1 else 12
    next_month = (month + 1) if month < 12 else 1
    prev_year = year if month > 1 else year - 1
    next_year = year if month < 12 else year + 1

    markup.row(
        InlineKeyboardButton("<", callback_data=f"change_month:{prev_year}-{prev_month}"),
        InlineKeyboardButton(" ", callback_data="ignore"),  # Placeholder for alignment
        InlineKeyboardButton(">", callback_data=f"change_month:{next_year}-{next_month}")
    )
    return markup


# ADMIN KEYBOARDS ==========================================================================

adminKey = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistics", callback_data="stats")],
        [InlineKeyboardButton(text="📤 Broadcast", callback_data='broadcast')],
        [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")],
    ]
)
settingsKey = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Clear Database", callback_data="clear_db")],
        [
            InlineKeyboardButton(text="➕ Add Admin", callback_data="add_admin"),
            InlineKeyboardButton(text="➖ Remove Admin", callback_data="remove_admin")
        ],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="goback")],
    ]
)

statsKey = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Update", callback_data="update")],
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
        [InlineKeyboardButton(text="🚫 Decline", callback_data="decline")]
    ]
)
adminConfirmDB = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm", callback_data="confirm_clear_db")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_clear_db")]
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