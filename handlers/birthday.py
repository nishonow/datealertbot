from .common import *

@dp.message_handler(text="🎂 My Birthday")
async def show_birthday(message: Message):
    user_id = message.from_user.id
    birthday = get_user_birthday(user_id)

    if birthday:
        now = datetime.now(KYRGYZSTAN_TZ)
        today = now.date()
        birthday_date = datetime.strptime(birthday, "%Y-%m-%d").date()
        next_birthday = birthday_date.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)

        days_until = (next_birthday - today).days
        await message.answer(
            f"🎉 Your birthday is on *{format_date_str(birthday)}*.\n"
            f"🎂 Only *{days_until} days* left until your next birthday!",
            parse_mode="Markdown"
        )
    else:
        await message.answer("❌ You haven't set your birthday yet. Go to ⚙️ Settings to add it!")

@dp.callback_query_handler(text="edit_birthday")
async def edit_birthday_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(
        "✏️ *Edit Birthday*\n\nPlease select your *birth year*:",
        parse_mode='Markdown',
        reply_markup=generate_year_picker()
    )
    await state.set_state("waiting_for_personal_birthday_picker")

@dp.callback_query_handler(lambda c: c.data.startswith("birthday_date"), state="waiting_for_personal_birthday_picker")
async def save_personal_birthday_inline(callback_query: CallbackQuery, state: FSMContext):
    _, date_text = callback_query.data.split(":")
    update_user_birthday(callback_query.from_user.id, date_text)
    await state.finish()
    await callback_query.message.edit_text(
        f"🎉 *Birthday updated!*\n\nSet to *{format_date_str(date_text)}*.",
        parse_mode='Markdown'
    )
    await callback.answer("Updated ✅")

# ─── Friends' Birthdays ───

@dp.callback_query_handler(text="friends_birthdays")
async def show_friends_birthdays(callback_query: CallbackQuery, state: FSMContext):
    await state.finish()
    user_id = callback_query.from_user.id
    friends = get_friend_birthdays(user_id)
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    if friends:
        for f_id, f_name, f_date in friends:
            display = f_name if len(f_name) <= 25 else f_name[:22] + "..."
            title = f"🗑 {display} ({format_date_str(f_date)})"
            keyboard.add(InlineKeyboardButton(title, callback_data=f"askdelfriend_{f_id}"))
    
    keyboard.add(InlineKeyboardButton("➕ Add Friend", callback_data="addfriendbday"))
    keyboard.add(InlineKeyboardButton("⬅️ Back to Settings", callback_data="settings_back"))

    await callback_query.message.edit_text(
        f"👥 *Friends' Birthdays* ({len(friends)})\n\n"
        "Tap a friend to delete them, or add a new one:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query_handler(text="addfriendbday")
async def add_friend_prompt(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(
        "➕ *Add Friend's Birthday*\n\n"
        "Please type the *name* of your friend:",
        reply_markup=make_cancel_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state("waiting_for_friend_name")
    await state.update_data(id=callback_query.message.message_id)

@dp.message_handler(state="waiting_for_friend_name")
async def save_friend_name(message: Message, state: FSMContext):
    if message.text in KNOWN_BUTTON_TEXTS or message.text.startswith("/"):
        await message.answer("⚠️ Please type the friend's name.")
        return
        
    f_name = message.text.strip()
    if not f_name or len(f_name) > 50:
        await message.answer("❌ Invalid name. Keep it under 50 characters.")
        return

    # Cleanup previous markup
    data = await state.get_data()
    old_id = data.get('id')
    if old_id:
        try:
            await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=old_id, reply_markup=None)
        except Exception:
            pass

    await state.update_data(friend_name=f_name)
    msg = await message.answer(
        f"👤 Friend: _{escape_md(f_name)}_\n\n"
        "📅 Now please select their *birth year*:",
        reply_markup=generate_year_picker(),
        parse_mode="Markdown"
    )
    await state.set_state("waiting_for_friend_birthday_picker")
    await state.update_data(id=msg.message_id)

@dp.callback_query_handler(lambda c: c.data.startswith("birthday_date"), state="waiting_for_friend_birthday_picker")
async def save_friend_birthday_inline(callback_query: CallbackQuery, state: FSMContext):
    _, date_text = callback_query.data.split(":")
    data = await state.get_data()
    f_name = data.get('friend_name', 'Unknown')
    user_id = callback_query.from_user.id

    add_friend_birthday(user_id, f_name, date_text)
    await state.finish()

    await callback_query.message.edit_text(
        f"✅ *Friend's birthday added!*\n\n"
        f"👤 {escape_md(f_name)}\n"
        f"🎂 {format_date_str(date_text)}",
        reply_markup=make_back_to_settings(),
        parse_mode="Markdown"
    )
    await callback.answer("Added ✅")

@dp.callback_query_handler(lambda c: c.data.startswith("askdelfriend_"))
async def ask_delete_friend_confirm(callback_query: CallbackQuery):
    f_id = int(callback_query.data.split("_")[1])
    friends = get_friend_birthdays(callback_query.from_user.id)
    f_name = next((f[1] for f in friends if f[0] == f_id), "this friend")
    
    confirm_kb = InlineKeyboardMarkup(row_width=2)
    confirm_kb.add(
        InlineKeyboardButton("✅ Yes", callback_data=f"confirdelfriend_{f_id}"),
        InlineKeyboardButton("❌ No", callback_data="friends_birthdays")
    )
    
    await callback_query.message.edit_text(
        f"🗑 *Remove Friend?*\n\nAre you sure you want to remove: *{escape_md(f_name)}*?",
        reply_markup=confirm_kb,
        parse_mode="Markdown"
    )
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("confirdelfriend_"))
async def delete_friend_confirmed(callback_query: CallbackQuery, state: FSMContext):
    f_id = int(callback_query.data.split("_")[1])
    delete_friend_birthday(f_id)
    await callback_query.answer("Removed! ✅")
    await show_friends_birthdays(callback_query, state)
