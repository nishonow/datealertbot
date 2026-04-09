from .common import *

@dp.message_handler(text="⚙️ Settings")
async def show_settings(message: Message):
    user_id = message.from_user.id
    birthday = get_user_birthday(user_id)
    notifications_enabled = get_user_notifications_status(user_id)

    birthday_message = (
        f"🎂 Birthday: *{format_date_str(birthday)}*"
        if birthday
        else "❌ Birthday not set yet"
    )
    notif_status = "🔔 ON" if notifications_enabled else "🔕 OFF"

    await message.answer(
        f"⚙️ *Settings*\n\n"
        f"{birthday_message}\n"
        f"Notifications: {notif_status}\n\n"
        "Choose an option:",
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
    birthday_message = (
        f"🎂 Birthday: *{format_date_str(birthday)}*"
        if birthday
        else "❌ Birthday not set yet"
    )
    notif_status = "🔔 ON" if new_status else "🔕 OFF"

    inline_answer = (
        "🔔 Notifications enabled!" if new_status else "🔕 Notifications disabled."
    )
    await bot.answer_callback_query(callback_query.id, text=inline_answer)
    await callback_query.message.edit_text(
        f"⚙️ *Settings*\n\n"
        f"{birthday_message}\n"
        f"Notifications: {notif_status}\n\n"
        "Choose an option:",
        reply_markup=updated_keyboard,
        parse_mode='Markdown'
    )

@dp.callback_query_handler(text="settings_back", state="*")
async def back_to_settings_handler(callback_query: CallbackQuery, state: FSMContext):
    await state.finish()
    user_id = callback_query.from_user.id
    birthday = get_user_birthday(user_id)
    notifications_enabled = get_user_notifications_status(user_id)

    birthday_message = (
        f"🎂 Birthday: *{format_date_str(birthday)}*"
        if birthday
        else "❌ Birthday not set yet"
    )
    notif_status = "🔔 ON" if notifications_enabled else "🔕 OFF"

    try:
        await callback_query.message.edit_text(
            f"⚙️ *Settings*\n\n"
            f"{birthday_message}\n"
            f"Notifications: {notif_status}\n\n"
            "Choose an option:",
            reply_markup=get_settings_keyboard(notifications_enabled),
            parse_mode='Markdown'
        )
    except Exception:
        pass

@dp.callback_query_handler(text="export_data")
async def export_data_handler(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    birthday = get_user_birthday(user_id)
    tasks = get_tasks_by_user(user_id)
    events = get_events_by_user(user_id)
    
    export_text = "📦 *Your Data Export*\n\n"
    export_text += f"🎂 *Birthday:* {format_date_str(birthday) if birthday else 'Not set'}\n\n"
    
    export_text += f"📝 *Tasks ({len(tasks)}):*\n"
    if tasks:
        for _, t_name, status in tasks:
            prefix = "✅" if status == 1 else "⬜️"
            export_text += f"{prefix} {escape_md(t_name)}\n"
    else:
        export_text += "_No tasks._\n"
        
    export_text += f"\n📅 *Events ({len(events)}):*\n"
    if events:
        for _, e_name, e_date in events:
            export_text += f"📅 {escape_md(e_name)} ({format_date_str(e_date)})\n"
    else:
        export_text += "_No events._\n"
        
    await callback_query.message.answer(export_text, parse_mode="Markdown")
    await callback_query.answer("Data exported! ✅")
