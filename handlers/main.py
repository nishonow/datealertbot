import re
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from core.db import add_user, user_exists, get_user_birthday, get_user_notifications_status, toggle_user_notifications, \
    update_user_birthday, add_task, get_tasks_by_user, delete_task, get_all_users, add_event, get_events_by_user, \
    delete_event
from core.keyboards import start_keyboard, get_settings_keyboard, generate_calendar
from loader import dp, bot


from aiogram.dispatcher.filters.state import any_state

@dp.message_handler(commands=['cancel'], state=any_state)
async def cancel_handler(message: Message, state: FSMContext):

    # Cancel the current state
    await state.finish()
    await message.answer("✅ Action cancelled. You can start again whenever you like.")

@dp.message_handler(text="⚙️ Settings")
async def show_settings(message: Message):
    user_id = message.from_user.id
    birthday = get_user_birthday(user_id)
    notifications_enabled = get_user_notifications_status(user_id)
    if birthday:
        birthday_message = f"🎂 Your birthday is currently set to: *{birthday}*"
    else:
        birthday_message = "❌ You haven't set your birthday yet."

    await message.answer(
        f"⚙️ *Settings Menu*\n\n"
        f"{birthday_message}\n\n"
        "Choose an option below:",
        reply_markup=get_settings_keyboard(notifications_enabled),
        parse_mode='Markdown'
    )

@dp.callback_query_handler(text="toggle_notifications")
async def toggle_notifications_handler(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    current_status = get_user_notifications_status(user_id)
    new_status = 0 if current_status == 1 else 1
    toggle_user_notifications(user_id, new_status)
    updated_keyboard = get_settings_keyboard(new_status)
    birthday = get_user_birthday(user_id)
    if birthday:
        birthday_message = f"🎂 Your birthday is currently set to: *{birthday}*"
    else:
        birthday_message = "❌ You haven't set your birthday yet."
    inline_answer = (
        "🔔 Great! You will now receive notifications for your events and reminders!"
        if new_status
        else "🔕 Notifications are now turned off. Don't worry, you can always turn them back on in settings!"
    )
    await bot.answer_callback_query(callback_query_id=callback_query.id, text=inline_answer, show_alert=True)
    await callback_query.message.edit_text(
        f"⚙️ *Settings Menu*\n\n"
        f"{birthday_message}\n\n"
        "Choose an option below:",
        reply_markup=updated_keyboard,
        parse_mode='Markdown'
    )


@dp.callback_query_handler(text="edit_birthday")
async def edit_birthday_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(
        "✏️ Please enter your new birthday in the format: *YYYY-MM-DD*\n\n"
        "For example: `1990-05-25`\n\nUse /cancel to stop the action.",
        parse_mode='Markdown'
    )
    await state.set_state("waiting_for_new_birthday")

@dp.message_handler(state="waiting_for_new_birthday")
async def save_new_birthday(message: Message, state: FSMContext):
    user_id = message.from_user.id
    new_birthday = message.text

    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if re.match(date_pattern, new_birthday):
        update_user_birthday(user_id, new_birthday)
        await message.answer(
            f"🎉 Your birthday has been updated to: *{new_birthday}*\n\n"
            "I’ll make sure to remind you when your special day is near!",
            parse_mode='Markdown'
        )
        await state.finish()
    else:
        await message.answer(
            "❌ Invalid date format. Please enter your birthday in the format: *YYYY-MM-DD*\n\n"
            "For example: `1990-05-25`\n\nUse /cancel to stop the action.",
            parse_mode='Markdown'
        )


# TASKS

@dp.message_handler(text=['📝 Add Task', '/add_task'])
async def ask_task_name(message: Message, state: FSMContext):
    await message.answer("📝 Please enter the name of the task:\n\nUse /cancel to stop the action.")
    await state.set_state("waiting_for_task_name")

@dp.message_handler(state="waiting_for_task_name")
async def save_task_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    task_name = message.text

    add_task(user_id, task_name)

    await message.answer(f"✅ Task {task_name} has been added successfully. Use /view_tasks to see your tasks!")
    await state.finish()

@dp.message_handler(text=["✅ View Tasks", "/view_tasks"])
async def show_tasks(message: Message):
    user_id = message.from_user.id
    tasks = get_tasks_by_user(user_id)

    if not tasks:
        await message.answer("🗂️ You have no tasks yet. Use /add_task to create one!")
        return

    task_keyboard = InlineKeyboardMarkup(row_width=1)
    for task_id, task_name in tasks:
        task_keyboard.add(InlineKeyboardButton(text=task_name, callback_data=f"task_{task_id}"))

    await message.answer("📝 Here are your tasks:", reply_markup=task_keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("task_"))
async def delete_task_handler(callback_query: CallbackQuery):
    task_id = int(callback_query.data.split("_")[1])
    user_id = callback_query.from_user.id
    tasks = get_tasks_by_user(user_id)
    task_name = next((task[1] for task in tasks if task[0] == task_id), None)
    if task_id:
        delete_task(task_id)
        remaining_tasks = get_tasks_by_user(user_id)
        task_keyboard = InlineKeyboardMarkup(row_width=1)
        for t_id, t_name in remaining_tasks:
            task_keyboard.add(InlineKeyboardButton(text=t_name, callback_data=f"task_{t_id}"))

        if remaining_tasks:
            await callback_query.message.edit_text(
                f"✅ Task {task_name} has been deleted successfully!\n\n"
                "📝 Here are your remaining tasks:",
                reply_markup=task_keyboard
            )
        else:
            await callback_query.message.edit_text(
                f"✅ Task {task_name} has been deleted successfully!\n\n"
                "🗂️ You have no remaining tasks. Use /add_task to create one!"
            )
    else:
        await callback_query.answer("❌ Task not found or already deleted.", show_alert=True)

# EVENTS

@dp.message_handler(text=["➕ Add Event", '/add_event'])
async def ask_event_details(message: Message, state: FSMContext):
    await message.answer("📝 Please enter the event name:\n\nUse /cancel to stop the action.")
    await state.set_state("waiting_for_event_name")


@dp.message_handler(state="waiting_for_event_name")
async def ask_event_date(message: Message, state: FSMContext):
    await state.update_data(event_name=message.text)
    now = datetime.now()
    await message.answer("📅 Now, select the event date:\n\nUse /cancel to stop the action.", reply_markup=generate_calendar(now.year, now.month))
    await state.set_state("waiting_for_event_date")


@dp.callback_query_handler(lambda c: c.data.startswith("change_month"), state="waiting_for_event_date")
async def change_calendar_month(callback: CallbackQuery, state: FSMContext):
    _, date_str = callback.data.split(":")
    year, month = map(int, date_str.split("-"))
    await callback.message.edit_reply_markup(reply_markup=generate_calendar(year, month))
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("select_date"), state="waiting_for_event_date")
async def save_event(callback: CallbackQuery, state: FSMContext):
    _, date_str = callback.data.split(":")
    event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    user_id = callback.from_user.id
    data = await state.get_data()
    event_name = data['event_name']

    add_event(user_id, event_name, event_date)  # Your function to save the event

    await callback.message.answer(
        f"✅ Event '{event_name}' on {event_date} has been added successfully. Use /view_events to see your upcoming events!")
    await state.finish()
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "ignore", state="waiting_for_event_date")
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()


@dp.message_handler(text=["📅 View Events", '/view_events'])
async def view_events(message: Message):
    user_id = message.from_user.id
    events = get_events_by_user(user_id)

    if not events:
        await message.answer("🗂️ You have no events. Use /add_event to create one!")
        return

    event_keyboard = InlineKeyboardMarkup(row_width=1)
    for event_id, event_name, event_date in events:
        event_keyboard.add(InlineKeyboardButton(
            text=f"{event_name} ({event_date})", callback_data=f"event_{event_id}"
        ))

    await message.answer("📅 Here are your events:", reply_markup=event_keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("event_"))
async def delete_event_handler(callback_query: CallbackQuery):
    event_id = int(callback_query.data.split("_")[1])
    events = get_events_by_user(callback_query.from_user.id)

    event_name = next((event[1] for event in events if event[0] == event_id), None)
    if event_name:
        delete_event(event_id)

        remaining_events = get_events_by_user(callback_query.from_user.id)
        event_keyboard = InlineKeyboardMarkup(row_width=1)
        for event_id, event_name, event_date in remaining_events:
            event_keyboard.add(InlineKeyboardButton(
                text=f"{event_name} ({event_date})", callback_data=f"event_{event_id}"
            ))

        if remaining_events:
            await callback_query.message.edit_text(
                f"✅ Event {event_name} has been deleted.\n\n"
                "📅 Here are your remaining events:",
                reply_markup=event_keyboard
            )
        else:
            await callback_query.message.edit_text(
                f"✅ Event {event_name} has been deleted.\n\n"
                "🗂️ You have no remaining events. Use /add_event to create one!"
            )
    else:
        await callback_query.answer("❌ Event not found or already deleted.", show_alert=True)


# MY BIRTHDAY
import pytz

KRYGYZSTAN_TZ = pytz.timezone("Asia/Bishkek")

@dp.message_handler(text="🎂 My Birthday")
async def show_birthday(message: Message):
    user_id = message.from_user.id
    birthday = get_user_birthday(user_id)  # Fetch the user's birthday from the database

    if birthday:
        now = datetime.now(KRYGYZSTAN_TZ)
        today = now.date()
        birthday_date = datetime.strptime(birthday, "%Y-%m-%d").date()
        next_birthday = birthday_date.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)

        days_until_birthday = (next_birthday - today).days
        await message.answer(f"🎉 Your birthday is on *{birthday}*.\n"
                             f"🎂 Only *{days_until_birthday} days* left until your next birthday!",
                             parse_mode="Markdown")
    else:
        await message.answer("❌ You haven't set your birthday yet. Use the settings menu to add it!")
