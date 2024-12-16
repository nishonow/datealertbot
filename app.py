import asyncio
import logging
import time
from aiogram import executor
from loader import dp
from datetime import datetime, timedelta
from loader import bot
import core
import handlers
import db
from core.db import get_all_users, get_tomorrows_events

BOT_START_TIME = time.time()
logging.basicConfig(
    format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.INFO,
)


from aiogram.utils.exceptions import BotBlocked, UserDeactivated, ChatNotFound

async def send_birthday_reminders():
    users = get_all_users()  # Fetch all users with their birthday and notification status
    today = datetime.now().date()

    for telegram_id, birthday, notifications_enabled in users:
        # Proceed if the birthday is set
        if birthday:
            birthday_date = datetime.strptime(birthday, "%Y-%m-%d").date()
            next_birthday = birthday_date.replace(year=today.year)
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)

            days_until_birthday = (next_birthday - today).days

            try:
                if days_until_birthday == 0:  # Birthday is today
                    # Always send "Happy Birthday" message regardless of notification settings
                    await bot.send_message(
                        chat_id=telegram_id,
                        text="🎉🎂 *Happy Birthday!* 🎂🎉\n\n"
                             "Wishing you a fantastic day filled with joy, laughter, and celebrations! 🥳",
                        parse_mode="Markdown"
                    )
                elif days_until_birthday > 0 and notifications_enabled:  # Birthday is in the future
                    # Send countdown message only if notifications are enabled
                    await bot.send_message(
                        chat_id=telegram_id,
                        text=f"🎉 Your birthday is in *{days_until_birthday} days*! 🎂 Get ready for the celebration! 🥳",
                        parse_mode="Markdown"
                    )
            except BotBlocked:
                pass  # Bot is blocked by the user, skip sending
            except UserDeactivated:
                pass  # User deactivated their account, skip sending
            except ChatNotFound:
                pass  # Chat not found, skip sending
            except Exception:
                pass  



async def daily_birthday_task():
    while True:
        now = datetime.utcnow()  # Use UTC for global scheduling
        next_run = (now + timedelta(days=1)).replace(hour=7, minute=0, second=0, microsecond=0)
        #next_run = now + timedelta(seconds=10)
        if next_run < now:  # If the next run is earlier than now, adjust to the next day
            next_run = next_run + timedelta(days=1)
        sleep_time = (next_run - now).total_seconds()

        #logging.info(f"Sleeping for {sleep_time} seconds until 6 AM UTC.")
        await asyncio.sleep(sleep_time)

        #logging.info("Sending daily birthday reminders...")
        await send_birthday_reminders()



from aiogram.utils.exceptions import BotBlocked, UserDeactivated, ChatNotFound

async def send_event_reminders():
    events = get_tomorrows_events()
    for user_id, event_name, event_date in events:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"⏰ Reminder: Your event *'{event_name}'* is scheduled for tomorrow, *{event_date}*! 🎉",
                parse_mode="Markdown"
            )
        except BotBlocked:
            pass  # Bot is blocked by the user, skip sending
        except UserDeactivated:
            pass  # User deactivated their account, skip sending
        except ChatNotFound:
            pass  # Chat not found, skip sending
        except Exception:
            pass  # Catch-all for any other unexpected errors


async def daily_event_task():
    while True:
        now = datetime.utcnow()  # Use UTC for global scheduling
        next_run = (now + timedelta(days=1)).replace(hour=7, minute=0, second=0, microsecond=0)
        if next_run < now:  # If the next run is earlier than now, adjust to the next day
            next_run = next_run + timedelta(days=1)
        sleep_time = (next_run - now).total_seconds()

        await asyncio.sleep(sleep_time)

        await send_event_reminders()




if __name__ == "__main__":
    from aiogram import executor

    loop = asyncio.get_event_loop()  # Get the event loop once
    loop.create_task(daily_event_task())  # Schedule the event reminder task
    loop.create_task(daily_birthday_task())  # Schedule the birthday reminder task

    executor.start_polling(dp, skip_updates=True, loop=loop)  # Start polling using the same loop

