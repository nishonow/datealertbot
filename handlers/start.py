import re
from datetime import datetime
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from core.db import add_user, update_user_birthday, get_user_birthday
from core.keyboards import start_keyboard, generate_year_picker
from loader import dp, bot

KNOWN_BUTTON_TEXTS = {
    "🎂 My Birthday", "➕ Add Event", "📅 View Events",
    "📝 Add Task", "✅ View Tasks", "⚙️ Settings",
}


@dp.message_handler(commands=['start'])
async def send_start_message(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = message.from_user.first_name or message.from_user.full_name
    username = message.from_user.username

    # Cancel any existing state first
    current_state = await state.get_state()
    if current_state:
        await state.finish()

    add_user(user_id, name or "User", username)

    birthday = get_user_birthday(user_id)

    if birthday:
        await message.answer(
            f"👋 *Welcome back, {name}!*\n\n"
            "📅 I'm your personal reminder bot.\n\n"
            "🎂 *Birthday reminders* — I'll notify you as your special day approaches\n"
            "📅 *Events* — Schedule important dates and get reminders\n"
            "📝 *Tasks* — Keep a to-do list at your fingertips\n\n"
            "Use the buttons below to get started!",
            parse_mode='Markdown',
            reply_markup=start_keyboard
        )
    else:
        await message.answer(
            f"👋 *Welcome, {name}!*\n\n"
            "I'm your personal *Date Alert Bot* — I'll help you track birthdays, events, and tasks.\n\n"
            "Let's start by setting up your *birthday* so I can remind you when it's near! 🎂\n\n"
            "Please select your *birth year* from the menu below:",
            parse_mode='Markdown',
            reply_markup=generate_year_picker()
        )
        await state.set_state("waiting_for_birthday_picker")


@dp.callback_query_handler(lambda c: c.data.startswith("birthday_date"), state="waiting_for_birthday_picker")
async def save_birthday_inline(callback_query: CallbackQuery, state: FSMContext):
    _, date_text = callback_query.data.split(":")
    telegram_id = callback_query.from_user.id
    update_user_birthday(telegram_id, date_text)
    
    parsed = datetime.strptime(date_text, "%Y-%m-%d")
    await state.finish()
    
    formatted = parsed.strftime('%B %d, %Y').replace(' 0', ' ')
    await callback_query.message.edit_text(
        f"🎉 *Birthday saved!*\n\n"
        f"Your birthday is set to *{formatted}* 🎂\n"
        "I'll remind you as your special day gets closer!",
        parse_mode='Markdown'
    )
    await callback_query.message.answer(
        "Now, use the menu below to explore all features:",
        reply_markup=start_keyboard
    )
    await callback_query.answer()
