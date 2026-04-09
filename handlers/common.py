import re
from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from core.db import (
    get_user_birthday, get_user_notifications_status, toggle_user_notifications,
    update_user_birthday, add_task, get_tasks_by_user, delete_task, delete_all_tasks,
    toggle_task, add_event, get_events_by_user, delete_event,
    get_friend_birthdays, add_friend_birthday, delete_friend_birthday
)
from core.keyboards import (
    start_keyboard, get_settings_keyboard, generate_calendar, make_back_to_settings,
    generate_year_picker, generate_month_picker
)
from loader import dp, bot
import pytz

KYRGYZSTAN_TZ = pytz.timezone('Asia/Bishkek')

KNOWN_BUTTON_TEXTS = {
    '🎂 My Birthday', '➕ Add Event', '📅 View Events',
    '📝 Add Task', '✅ View Tasks', '⚙️ Settings',
}

MAX_NAME_LENGTH = 100

def make_cancel_keyboard(callback_data: str = 'inline_cancel') -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton('❌ Cancel', callback_data=callback_data))
    return kb

def escape_md(text: str) -> str:
    special = r'\_*[]()~`>#+-=|{}.!'
    for ch in special:
        text = text.replace(ch, f'\\{ch}')
    return text

def format_date_str(date_str) -> str:
    try:
        if isinstance(date_str, str):
            dt = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            dt = date_str
        return dt.strftime('%B %d, %Y').replace(' 0', ' ')
    except Exception:
        return str(date_str)

@dp.message_handler(commands=['cancel'], state="*")
@dp.message_handler(text="❌ Cancel", state="*")
async def cancel_handler(message: Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "✅ *Action cancelled.*\n\nReturning to the main menu.",
        parse_mode="Markdown",
        reply_markup=start_keyboard
    )

@dp.callback_query_handler(text="inline_cancel", state="*")
async def inline_cancel_handler(callback_query: CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.message.edit_text(
        "✅ *Action cancelled.*",
        parse_mode="Markdown"
    )
    await callback_query.answer()

# ─── Shared Shared Birthday Picker ───

@dp.callback_query_handler(lambda c: c.data.startswith("change_month"), state="*")
async def process_change_month(callback_query: CallbackQuery, state: FSMContext):
    try:
        _, date_str = callback_query.data.split(":")
        year, month = map(int, date_str.split("-"))
        
        current_state = await state.get_state()
        is_birthday = current_state in [
            "waiting_for_birthday_picker",
            "waiting_for_personal_birthday_picker",
            "waiting_for_friend_birthday_picker"
        ]
        
        await callback_query.message.edit_reply_markup(
            reply_markup=generate_calendar(year, month, is_birthday=is_birthday)
        )
    except Exception:
        pass
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("year_page"), state="*")
async def process_year_page(callback_query: CallbackQuery):
    _, page = callback_query.data.split(":")
    start_year = None if page == "default" else int(page)
    await callback_query.message.edit_reply_markup(reply_markup=generate_year_picker(start_year))
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("set_year"), state="*")
async def process_set_year(callback_query: CallbackQuery):
    _, year = callback_query.data.split(":")
    await callback_query.message.edit_reply_markup(reply_markup=generate_month_picker(int(year)))
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("set_month"), state="*")
async def process_set_month(callback_query: CallbackQuery):
    _, date_part = callback_query.data.split(":")
    year, month = map(int, date_part.split("-"))
    await callback_query.message.edit_reply_markup(reply_markup=generate_calendar(year, month, is_birthday=True))
    await callback_query.answer()


@dp.callback_query_handler(text="ignore", state="*")
async def ignore_callback(callback_query: CallbackQuery):
    await callback_query.answer()

