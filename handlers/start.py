import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from core.db import add_user, user_exists, update_user_birthday, get_user_birthday
from core.keyboards import start_keyboard
from loader import dp, bot


@dp.message_handler(commands=['start'])
async def send_start_message(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = message.from_user.full_name
    username = message.from_user.username

    # Add user if not exists
    add_user(user_id, name, username)

    # Check if the birthday exists
    birthday = get_user_birthday(user_id)

    if birthday:  # If birthday exists
        await message.answer(
            f"🎉 *Welcome to Date Alert Bot!* 🎉\n\n"
            "📅 I'm here to help you manage your events and daily tasks.\n\n"
            "🔔 I will remind you one day before your events, so you never miss anything important.\n"
            "📝 You can also use me to keep track of your to-do tasks effortlessly.\n\n"
            "Let's get started and make your life more organized!",
            parse_mode='Markdown',
            reply_markup=start_keyboard
        )
    else:  # If birthday doesn't exist
        await message.answer(
            "🎉 *Welcome to Date Alert Bot!* 🎉\n\n"
            "I'm here to help you remember birthdays, events, and your daily to-do tasks.\n"
            "Let's start by adding your *birthday*.\n\n"
            "📅 Please enter your birthday in this format: *YYYY-MM-DD*",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardRemove()  # No reply markup
        )
        await state.set_state("waiting_for_birthday")


@dp.message_handler(state="waiting_for_birthday")
async def save_birthday(message: Message, state: FSMContext):
    # Regex for YYYY-MM-DD format
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"

    if re.match(date_pattern, message.text):
        birthday = message.text
        telegram_id = message.from_user.id
        update_user_birthday(telegram_id, birthday)
        await message.answer(
            f"🎂 Got it! Your birthday is saved as *{birthday}*. I'll remind you every day! 🎉",
            reply_markup=start_keyboard,
            parse_mode='Markdown'
        )
        await state.finish()
    else:
        await message.answer("❌ Please enter the date in the correct format: **YYYY-MM-DD**.")


