# ===================================================================
# IMPORTS
# ===================================================================

import time
import asyncio

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from app import BOT_START_TIME
from config import ADMINS
from core.db import (
    count_users, get_user_ids, count_new_users_last_24_hours,
    clear_db, get_admins, add_admin, remove_admin,
    count_admins, get_admin_details,
)
from core.keyboards import (
    adminKey, ConfirmBroadcast, backToSettings, settingsKey,
    statsKey, adminBack, adminConfirmDB, adminCancelKey, dbBack,
)
from loader import dp, bot


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _is_admin(user_id: int) -> bool:
    return user_id in get_admins() or user_id in ADMINS


def _build_admins_text() -> str:
    """Return a formatted string of current admins for display."""
    admins_details = get_admin_details()
    known_ids = {admin[0] for admin in admins_details}
    all_admin_ids = get_admins()

    lines = []
    for admin_id, admin_name in admins_details:
        link = f"[{admin_id}](tg://user?id={admin_id})"
        lines.append(f"{link} — {admin_name or 'Unknown'}")

    for missing_id in set(all_admin_ids) - known_ids:
        lines.append(f"{missing_id} — _(not in users table)_")

    return "\n".join(lines) if lines else "_No admins configured._"


# ===================================================================
# /admin COMMAND
# ===================================================================

@dp.message_handler(commands=["admin"])
async def admin_command(message: Message):
    if not _is_admin(message.from_user.id):
        return  # silently ignore non-admins
    await message.answer("🛠 *Admin Panel*\n\nChoose an action:", reply_markup=adminKey, parse_mode="Markdown")


# ===================================================================
# BROADCAST
# ===================================================================

@dp.callback_query_handler(text="broadcast")
async def broadcast_prompt(callback_query: CallbackQuery, state: FSMContext):
    if not _is_admin(callback_query.from_user.id):
        await callback_query.answer("⛔ Access denied.", show_alert=True)
        return
    msg = await callback_query.message.edit_text(
        "📤 *Broadcast*\n\nSend the message you want to broadcast to all users.\n"
        "Supports text, photos, videos, stickers — any content type.",
        reply_markup=adminBack,
        parse_mode="Markdown"
    )
    await state.set_state("getMessage")
    await state.update_data(id=msg.message_id)


@dp.message_handler(content_types="any", state="getMessage")
async def get_broadcast_message(message: Message, state: FSMContext):
    message_id = message.message_id
    await state.update_data(msgID=message_id)
    data = await state.get_data()
    prompt_id = data.get("id")

    # Remove the prompt markup
    if prompt_id:
        try:
            await bot.edit_message_reply_markup(
                chat_id=message.chat.id, message_id=prompt_id
            )
        except Exception:
            pass

    await bot.copy_message(message.from_user.id, message.from_user.id, message_id)
    await message.answer(
        "👆 *Preview above.*\n\nConfirm to send this to all users:",
        reply_markup=ConfirmBroadcast,
        parse_mode="Markdown"
    )
    await state.set_state("getAction")


@dp.callback_query_handler(text="confirm", state="getAction")
async def broadcast_confirm(callback_query: CallbackQuery, state: FSMContext):
    if not _is_admin(callback_query.from_user.id):
        await callback_query.answer("⛔ Access denied.", show_alert=True)
        return
    data = await state.get_data()
    msg_id = data.get("msgID")
    await callback_query.message.edit_reply_markup()

    user_ids = get_user_ids()
    success, blocked = 0, 0
    status_msg = await callback_query.message.answer(f"📤 Sending to {len(user_ids)} users...")

    for uid in user_ids:
        try:
            await bot.copy_message(chat_id=uid, from_chat_id=callback_query.message.chat.id, message_id=msg_id)
            success += 1
        except Exception:
            blocked += 1
        await asyncio.sleep(0.04)

    await state.finish()
    try:
        await status_msg.delete()
    except Exception:
        pass
    await callback_query.message.answer(
        f"✅ *Broadcast complete!*\n\n"
        f"📨 Delivered: *{success}*\n"
        f"🚫 Failed/Blocked: *{blocked}*",
        reply_markup=adminBack,
        parse_mode="Markdown"
    )


@dp.callback_query_handler(text="decline", state="getAction")
async def broadcast_decline(callback_query: CallbackQuery, state: FSMContext):
    await state.finish()
    try:
        await callback_query.message.delete()
    except Exception:
        pass
    await callback_query.message.answer(
        "🚫 *Broadcast cancelled.*",
        reply_markup=adminKey,
        parse_mode="Markdown"
    )


# ===================================================================
# ADMIN MANAGEMENT
# ===================================================================

@dp.callback_query_handler(text="add_admin")
async def add_admin_prompt(callback_query: CallbackQuery, state: FSMContext):
    if not _is_admin(callback_query.from_user.id):
        await callback_query.answer("⛔ Access denied.", show_alert=True)
        return
    admins_text = _build_admins_text()
    await callback_query.message.edit_text(
        f"➕ *Add Admin*\n\nSend the *Telegram ID* of the user you want to promote.\n\n"
        f"📋 Current admins:\n{admins_text}",
        reply_markup=adminCancelKey,
        parse_mode="Markdown"
    )
    await state.update_data(msgID=callback_query.message.message_id)
    await state.set_state("add_admin")


@dp.message_handler(state="add_admin")
async def add_new_admin(message: Message, state: FSMContext):
    data = await state.get_data()
    prompt_msg_id = data.get("msgID")

    # Clean up prompt
    if prompt_msg_id:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=prompt_msg_id)
        except Exception:
            pass

    await state.finish()

    # Guard: reject non-numeric and menu-button text
    try:
        new_admin_id = int(message.text.strip())
    except (ValueError, AttributeError):
        await message.answer(
            "❌ *Invalid ID.*\n\nPlease send a valid numeric Telegram ID.",
            reply_markup=backToSettings,
            parse_mode="Markdown"
        )
        return

    if new_admin_id in get_admins():
        await message.answer(
            f"⚠️ User `{new_admin_id}` is *already an admin*.",
            reply_markup=backToSettings,
            parse_mode="Markdown"
        )
        return

    add_admin(new_admin_id)
    await message.answer(
        f"✅ User `{new_admin_id}` has been *added as admin*.",
        reply_markup=backToSettings,
        parse_mode="Markdown"
    )


@dp.callback_query_handler(text="remove_admin")
async def remove_admin_prompt(callback_query: CallbackQuery, state: FSMContext):
    if not _is_admin(callback_query.from_user.id):
        await callback_query.answer("⛔ Access denied.", show_alert=True)
        return
    admins_text = _build_admins_text()
    await callback_query.message.edit_text(
        f"➖ *Remove Admin*\n\nSend the *Telegram ID* of the admin you want to remove.\n\n"
        f"📋 Current admins:\n{admins_text}",
        reply_markup=adminCancelKey,
        parse_mode="Markdown"
    )
    await state.update_data(msgID=callback_query.message.message_id)
    await state.set_state("remove_admin")


@dp.message_handler(state="remove_admin")
async def remove_old_admin(message: Message, state: FSMContext):
    data = await state.get_data()
    prompt_msg_id = data.get("msgID")

    if prompt_msg_id:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=prompt_msg_id)
        except Exception:
            pass

    await state.finish()

    try:
        admin_to_remove = int(message.text.strip())
    except (ValueError, AttributeError):
        await message.answer(
            "❌ *Invalid ID.*\n\nPlease send a valid numeric Telegram ID.",
            reply_markup=backToSettings,
            parse_mode="Markdown"
        )
        return

    if admin_to_remove not in get_admins():
        await message.answer(
            f"⚠️ User `{admin_to_remove}` is *not an admin*.",
            reply_markup=backToSettings,
            parse_mode="Markdown"
        )
        return

    remove_admin(admin_to_remove)
    await message.answer(
        f"✅ User `{admin_to_remove}` has been *removed from admins*.",
        reply_markup=backToSettings,
        parse_mode="Markdown"
    )


@dp.callback_query_handler(text="cancel_add_admin", state="*")
async def cancel_admin_action(callback_query: CallbackQuery, state: FSMContext):
    await state.finish()
    admins_text = _build_admins_text()
    await callback_query.message.edit_text(
        f"⚙️ *Admin Settings*\n\n📋 Admins:\n{admins_text}",
        reply_markup=settingsKey,
        parse_mode="Markdown"
    )


# ===================================================================
# STATS
# ===================================================================

def _build_stats_text() -> str:
    total_users = count_users()
    new_users = count_new_users_last_24_hours()
    total_admins = count_admins()
    elapsed = int(time.time() - BOT_START_TIME)
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    uptime = f"{hours}h {minutes}m {seconds}s"
    return (
        f"📊 *Bot Statistics*\n\n"
        f"👤 Total users: *{total_users}*\n"
        f"🆕 New (last 24h): *{new_users}*\n"
        f"🛡 Admins: *{total_admins}*\n"
        f"⏱ Uptime: *{uptime}*"
    )


@dp.callback_query_handler(text="stats")
async def show_stats(callback_query: CallbackQuery):
    if not _is_admin(callback_query.from_user.id):
        await callback_query.answer("⛔ Access denied.", show_alert=True)
        return
    await callback_query.message.edit_text(_build_stats_text(), reply_markup=statsKey, parse_mode="Markdown")


@dp.callback_query_handler(text="update")
async def refresh_stats(callback_query: CallbackQuery):
    if not _is_admin(callback_query.from_user.id):
        await callback_query.answer("⛔ Access denied.", show_alert=True)
        return
    await callback_query.message.edit_text(_build_stats_text(), reply_markup=statsKey, parse_mode="Markdown")
    await callback_query.answer("✅ Stats refreshed!")


# ===================================================================
# DATABASE CLEAR
# ===================================================================

@dp.callback_query_handler(text="clear_db")
async def ask_clear_db(callback_query: CallbackQuery):
    if not _is_admin(callback_query.from_user.id):
        await callback_query.answer("⛔ Access denied.", show_alert=True)
        return
    await callback_query.message.edit_text(
        "⚠️ *Clear Database*\n\n"
        "This will *permanently delete all users* from the database.\n"
        "Events, tasks, and birthdays will all be lost.\n\n"
        "Are you absolutely sure?",
        reply_markup=adminConfirmDB,
        parse_mode="Markdown"
    )


@dp.callback_query_handler(text="confirm_clear_db")
async def confirm_clear_db(callback_query: CallbackQuery):
    if not _is_admin(callback_query.from_user.id):
        await callback_query.answer("⛔ Access denied.", show_alert=True)
        return
    clear_db()
    await callback_query.message.edit_text(
        "🗑 *Database cleared.*\n\nAll user data has been removed.",
        reply_markup=dbBack,
        parse_mode="Markdown"
    )


@dp.callback_query_handler(text="cancel_clear_db")
async def cancel_clear_db(callback_query: CallbackQuery):
    admins_text = _build_admins_text()
    await callback_query.message.edit_text(
        f"⚙️ *Admin Settings*\n\n📋 Admins:\n{admins_text}",
        reply_markup=settingsKey,
        parse_mode="Markdown"
    )


# ===================================================================
# SETTINGS
# ===================================================================

@dp.callback_query_handler(text="settings")
async def open_admin_settings(callback_query: CallbackQuery):
    if not _is_admin(callback_query.from_user.id):
        await callback_query.answer("⛔ Access denied.", show_alert=True)
        return
    admins_text = _build_admins_text()
    await callback_query.message.edit_text(
        f"⚙️ *Admin Settings*\n\n📋 Admins:\n{admins_text}",
        reply_markup=settingsKey,
        parse_mode="Markdown"
    )


@dp.callback_query_handler(text="goback", state="*")
async def go_back(callback_query: CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.message.edit_text(
        "🛠 *Admin Panel*\n\nChoose an action:",
        reply_markup=adminKey,
        parse_mode="Markdown"
    )
