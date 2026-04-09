from .common import *

@dp.message_handler(text=['📝 Add Task', '/add_task'])
async def ask_task_name(message: Message, state: FSMContext):
    msg = await message.answer(
        "📝 *New Task*\n\n"
        "Please enter the name for your task:",
        parse_mode="Markdown",
        reply_markup=make_cancel_keyboard()
    )
    await state.set_state("waiting_for_task_name")
    await state.update_data(id=msg.message_id)

@dp.message_handler(state="waiting_for_task_name")
async def save_task_name(message: Message, state: FSMContext):
    if message.text in KNOWN_BUTTON_TEXTS or message.text.startswith("/"):
        await message.answer("⚠️ Please type the task name.", parse_mode="Markdown")
        return

    task_name = message.text.strip()
    if not task_name or len(task_name) > MAX_NAME_LENGTH:
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

    add_task(message.from_user.id, task_name)
    await state.finish()
    await message.answer(
        f"✅ *Task added!*\n\n📝 _{escape_md(task_name)}_",
        parse_mode="Markdown",
        reply_markup=start_keyboard
    )

@dp.message_handler(text=["✅ View Tasks", "/view_tasks"])
async def show_tasks(message: Message):
    tasks = get_tasks_by_user(message.chat.id)
    if not tasks:
        await message.answer("🗂 *No tasks yet!*", parse_mode="Markdown", reply_markup=start_keyboard)
        return

    task_keyboard = InlineKeyboardMarkup(row_width=2)
    for task_id, task_name, status in tasks:
        prefix = "✅" if status == 1 else "⬜️"
        display = task_name[:35] + "..." if len(task_name) > 35 else task_name
        btn_status = InlineKeyboardButton(f"{prefix} {display}", callback_data=f"toggletask_{task_id}")
        btn_delete = InlineKeyboardButton("🗑", callback_data=f"askdeltask_{task_id}")
        task_keyboard.row(btn_status, btn_delete)
    
    task_keyboard.row(InlineKeyboardButton("🗑 Clear All Tasks", callback_data="clearalltasks"))
    await message.answer("📝 *Your Tasks*\n\nTap a task to toggle status, or 🗑 to delete:", reply_markup=task_keyboard, parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data.startswith("toggletask_"))
async def toggle_task_status_handler(callback_query: CallbackQuery):
    task_id = int(callback_query.data.split("_")[1])
    toggle_task(task_id)
    await callback_query.answer("Toggled! ✅")
    
    tasks = get_tasks_by_user(callback_query.from_user.id)
    task_keyboard = InlineKeyboardMarkup(row_width=2)
    for t_id, t_name, status in tasks:
        prefix = "✅" if status == 1 else "⬜️"
        display = t_name[:35] + "..." if len(t_name) > 35 else t_name
        task_keyboard.row(
            InlineKeyboardButton(f"{prefix} {display}", callback_data=f"toggletask_{t_id}"),
            InlineKeyboardButton("🗑", callback_data=f"askdeltask_{t_id}")
        )
    task_keyboard.row(InlineKeyboardButton("🗑 Clear All Tasks", callback_data="clearalltasks"))
    await callback_query.message.edit_reply_markup(reply_markup=task_keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("askdeltask_"))
async def ask_delete_task_confirm(callback_query: CallbackQuery):
    task_id = int(callback_query.data.split("_")[1])
    tasks = get_tasks_by_user(callback_query.from_user.id)
    task_name = next((t[1] for t in tasks if t[0] == task_id), "this task")
    
    confirm_kb = InlineKeyboardMarkup(row_width=2)
    confirm_kb.add(
        InlineKeyboardButton("✅ Yes", callback_data=f"confirdeltask_{task_id}"),
        InlineKeyboardButton("❌ No", callback_data="view_tasks_refresh")
    )
    
    await callback_query.message.edit_text(
        f"🗑 *Delete Task?*\n\nAre you sure you want to delete: *{escape_md(task_name)}*?",
        reply_markup=confirm_kb,
        parse_mode="Markdown"
    )
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("confirdeltask_"))
async def delete_task_confirmed(callback_query: CallbackQuery):
    task_id = int(callback_query.data.split("_")[1])
    delete_task(task_id)
    await callback_query.answer("Task deleted! ✅")
    await show_tasks(callback_query.message)

@dp.callback_query_handler(text="view_tasks_refresh")
async def refresh_tasks_view(callback_query: CallbackQuery):
    await callback_query.message.delete()
    await show_tasks(callback_query.message)
    await callback_query.answer()

@dp.callback_query_handler(text="clearalltasks")
async def confirm_clear_all_tasks(callback_query: CallbackQuery):
    confirm_kb = InlineKeyboardMarkup(row_width=2)
    confirm_kb.add(
        InlineKeyboardButton("✅ Yes, clear all", callback_data="confirmclearall"),
        InlineKeyboardButton("❌ Cancel", callback_data="view_tasks_refresh")
    )
    await callback_query.message.edit_text("🗑 *Clear ALL tasks?*", reply_markup=confirm_kb, parse_mode="Markdown")

@dp.callback_query_handler(text="confirmclearall")
async def clear_all_tasks_confirmed(callback_query: CallbackQuery):
    delete_all_tasks(callback_query.from_user.id)
    await callback_query.message.edit_text("✅ *All tasks cleared!*", parse_mode="Markdown")
    await callback_query.answer()
