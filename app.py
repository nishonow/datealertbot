import asyncio
import logging
import time
from datetime import datetime, timedelta

from aiogram import executor
from aiogram.utils.exceptions import BotBlocked, UserDeactivated, ChatNotFound

from core.db import get_all_users, get_tomorrows_events, get_todays_events, get_all_friend_birthdays
from loader import dp, bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ... your other imports ...
import core
import handlers
import db

BOT_START_TIME = time.time()

logging.basicConfig(
    format="%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# BIRTHDAY REMINDERS
# ─────────────────────────────────────────────

async def send_birthday_reminders():
    logger.info("Executing scheduled birthday reminders...")
    users = get_all_users()
    today = datetime.now().date()
    count = 0

    for telegram_id, birthday, notifications_enabled in users:
        if not birthday:
            continue

        try:
            birthday_date = datetime.strptime(birthday, "%Y-%m-%d").date()
        except ValueError:
            continue

        next_birthday = birthday_date.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)

        days_until = (next_birthday - today).days

        if days_until == 0:
            text = (
                "🎉🎂 *Happy Birthday!* 🎂🎉\n\n"
                "Today is your special day! Wishing you joy, laughter, and all the best! 🥳"
            )
        elif days_until == 1 and notifications_enabled:
            text = (
                "🎂 *Your birthday is tomorrow!*\n\n"
                "Get ready to celebrate — your special day is just around the corner! 🥳"
            )
        elif days_until == 7 and notifications_enabled:
            text = (
                "🎂 *One week until your birthday!*\n\n"
                "Only 7 days to go — hope you're planning something fun! 🎉"
            )
        elif days_until == 30 and notifications_enabled:
            text = (
                "📅 *30 days until your birthday!*\n\n"
                "Just a heads-up — your special day is a month away! 🎂"
            )
        else:
            continue

        try:
            await bot.send_message(chat_id=telegram_id, text=text, parse_mode="Markdown")
            count += 1
        except (BotBlocked, UserDeactivated, ChatNotFound):
            pass
        except Exception as e:
            logger.warning(f"Failed to send birthday reminder to {telegram_id}: {e}")

        await asyncio.sleep(0.04)
        
    # --- Friend Birthdays ---
    friend_bdays = get_all_friend_birthdays()
    for user_id, friend_name, bday_str, notifications_enabled in friend_bdays:
        if not notifications_enabled:
            continue
        try:
            bday_date = datetime.strptime(bday_str, "%Y-%m-%d").date()
        except ValueError:
            continue
            
        next_bday = bday_date.replace(year=today.year)
        if next_bday < today:
            next_bday = next_bday.replace(year=today.year + 1)
            
        days_until = (next_bday - today).days
        
        if days_until == 0:
            text = f"🎉🎂 *It's {friend_name}'s Birthday Today!* 🎂🎉\n\nDon't forget to wish them well!"
        elif days_until == 1:
            text = f"🎂 *Reminder: {friend_name}'s birthday is tomorrow!*\n\nMake sure to prepare a gift! 🎁"
        elif days_until == 7:
            text = f"🎂 *{friend_name}'s birthday is in exactly 1 week!*\n\nTime to start planning! 🎉"
        else:
            continue
            
        try:
            await bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")
            count += 1
        except Exception as e:
            pass
        await asyncio.sleep(0.04)

    if count:
        logger.info(f"Birthday reminders sent: {count}")


# ─────────────────────────────────────────────
# EVENT REMINDERS
# ─────────────────────────────────────────────

async def send_event_reminders():
    logger.info("Executing scheduled event reminders...")
    count = 0

    # Tomorrow's events
    for user_id, event_name, event_date in get_tomorrows_events():
        try:
            formatted_date = datetime.strptime(str(event_date), "%Y-%m-%d").strftime("%B %d, %Y").replace(" 0", " ")
            await bot.send_message(
                chat_id=user_id,
                text=(
                    f"⏰ *Reminder: Tomorrow's Event*\n\n"
                    f"📅 *{event_name}*\n"
                    f"🗓 {formatted_date}\n\n"
                    "Make sure you're prepared! 💪"
                ),
                parse_mode="Markdown"
            )
            count += 1
        except (BotBlocked, UserDeactivated, ChatNotFound):
            pass
        except Exception as e:
            logger.warning(f"Failed to send tomorrow event reminder to {user_id}: {e}")
        await asyncio.sleep(0.04)

    # Today's events
    for user_id, event_name, event_date in get_todays_events():
        try:
            formatted_date = datetime.strptime(str(event_date), "%Y-%m-%d").strftime("%B %d, %Y").replace(" 0", " ")
            await bot.send_message(
                chat_id=user_id,
                text=(
                    f"🔴 *Today's Event*\n\n"
                    f"📅 *{event_name}*\n"
                    f"🗓 {formatted_date}\n\n"
                    "It's happening today — good luck! 🌟"
                ),
                parse_mode="Markdown"
            )
            count += 1
        except (BotBlocked, UserDeactivated, ChatNotFound):
            pass
        except Exception as e:
            logger.warning(f"Failed to send today event reminder to {user_id}: {e}")
        await asyncio.sleep(0.04)

    if count:
        logger.info(f"Event reminders sent: {count}")


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("Bot is starting...")
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_birthday_reminders, trigger='cron', hour=1, minute=0)
    scheduler.add_job(send_event_reminders, trigger='cron', hour=1, minute=0)
    
    async def on_startup(dispatcher):
        scheduler.start()

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
