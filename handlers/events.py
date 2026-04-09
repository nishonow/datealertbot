from .common import *

@dp.message_handler(text=["➕ Add Event", '/add_event'])
async def ask_event_details(message: Message, state: FSMContext):
    msg = await message.answer(
        "📅 *New Event*\n\nPlease enter the name of the event:",
        parse_mode="Markdown",
        reply_markup=make_cancel_keyboard()
    )
    await state.set_state("waiting_for_event_name")
    await state.update_data(id=msg.message_id)

@dp.message_handler(state="waiting_for_event_name")
async def ask_event_date_calendar(message: Message, state: FSMContext):
    # Guard against commands/buttons
    if message.text in KNOWN_BUTTON_TEXTS or message.text.startswith("/"):
        await message.answer("⚠️ Please type the event name.")
        return

    event_name = message.text.strip()
    if not event_name or len(event_name) > MAX_NAME_LENGTH:
        await message.answer("❌ Invalid name length.")
        return

    # Cleanup previous markup
    data = await state.get_data()
    old_id = data.get('id')
    if old_id:
        try:
            await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=old_id, reply_markup=None)
        except Exception:
            pass

    await state.update_data(event_name=event_name)
    now = datetime.now()
    cal_msg = await message.answer(
        f"📅 Event: _{escape_md(event_name)}_\n\n"
        "Now select the date from the calendar below:",
        reply_markup=generate_calendar(now.year, now.month),
        parse_mode="Markdown"
    )
    await state.set_state("waiting_for_event_date_calendar")
    await state.update_data(id=cal_msg.message_id)

@dp.callback_query_handler(lambda c: c.data.startswith("change_month"), state="waiting_for_event_date_calendar")
async def change_month_event(callback_query: CallbackQuery, state: FSMContext):
    try:
        _, date_str = callback_query.data.split(":")
        year, month = map(int, date_str.split("-"))
        await callback_query.message.edit_reply_markup(reply_markup=generate_calendar(year, month))
    except Exception:
        pass
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("select_date"), state="waiting_for_event_date_calendar")
async def save_event_calendar(callback_query: CallbackQuery, state: FSMContext):
    try:
        _, date_str = callback_query.data.split(":")
        event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        await callback_query.answer("❌ Invalid date.", show_alert=True)
        return

    if event_date < datetime.now().date():
        await callback_query.answer("❌ You cannot schedule an event in the past!", show_alert=True)
        return

    data = await state.get_data()
    add_event(callback_query.from_user.id, data.get('event_name', 'Event'), event_date)
    await state.finish()

    await callback_query.message.edit_text(
        f"✅ *Event added!*\n\n📅 {format_date_str(event_date)}",
        parse_mode="Markdown"
    )
    await callback_query.answer("Event saved! ✅")

# ─── VIEW & DELETE ───

@dp.message_handler(text=["📅 View Events", '/view_events'])
async def view_events_handler(message: Message):
    events = get_events_by_user(message.chat.id)
    if not events:
        await message.answer("🗂 *No events yet!*", parse_mode="Markdown", reply_markup=start_keyboard)
        return

    event_keyboard = InlineKeyboardMarkup(row_width=1)
    today = datetime.now().date()
    for e_id, e_name, e_date in events:
        try:
            ev_date = datetime.strptime(str(e_date), "%Y-%m-%d").date()
            indicator = "🟢" if ev_date > today else "🔴" if ev_date == today else "⏮"
            label = f"{indicator} {e_name[:25]} ({format_date_str(ev_date)})"
        except Exception:
            label = f"📅 {e_name}"
        event_keyboard.add(InlineKeyboardButton(label, callback_data=f"askdelevent_{e_id}"))

    await message.answer(
        "📅 *Your Events*\n\n"
        "🟢 Upcoming | 🔴 Today | ⏮ Past\n\n"
        "Tap an event to delete it:",
        reply_markup=event_keyboard, parse_mode="Markdown"
    )

@dp.callback_query_handler(lambda c: c.data.startswith("askdelevent_"))
async def ask_delete_event_confirm(callback_query: CallbackQuery):
    event_id = int(callback_query.data.split("_")[1])
    events = get_events_by_user(callback_query.from_user.id)
    event_name = next((e[1] for e in events if e[0] == event_id), "this event")
    
    confirm_kb = InlineKeyboardMarkup(row_width=2)
    confirm_kb.add(
        InlineKeyboardButton("✅ Yes", callback_data=f"confirdelfull_{event_id}"),
        InlineKeyboardButton("❌ No", callback_data="view_events_refresh")
    )
    
    await callback_query.message.edit_text(
        f"🗑 *Delete Event?*\n\nAre you sure you want to delete: *{escape_md(event_name)}*?",
        reply_markup=confirm_kb,
        parse_mode="Markdown"
    )
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("confirdelfull_"))
async def delete_event_confirmed(callback_query: CallbackQuery):
    event_id = int(callback_query.data.split("_")[1])
    delete_event(event_id)
    await callback_query.answer("Deleted! ✅")
    await view_events_handler(callback_query.message)

@dp.callback_query_handler(text="view_events_refresh")
async def refresh_events_view(callback_query: CallbackQuery):
    await callback_query.message.delete() # Remove the confirmation message
    await view_events_handler(callback_query.message)
    await callback_query.answer()
