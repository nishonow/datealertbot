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
from core.db import get_all_users, get_tomorrows_events, get_todays_events

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
                    await bot.send_message(
                        chat_id=telegram_id,
                        text="🎉🎂 *Happy Birthday!* 🎂🎉\n\n"
                             "Wishing you a fantastic day filled with joy, laughter, and celebrations!",
                        parse_mode="Markdown"
                    )
                elif days_until_birthday > 0 and notifications_enabled:  # Birthday is in the future
                    await bot.send_message(
                        chat_id=telegram_id,
                        text=f"🎉 Your birthday is in *{days_until_birthday} days*!",
                        parse_mode="Markdown"
                    )
            except BotBlocked:
                pass
            except UserDeactivated:
                pass
            except ChatNotFound:
                pass
            except Exception:
                pass

            # Add delay to respect rate limits
            await asyncio.sleep(0.04)


async def daily_birthday_task():
    while True:
        now = datetime.utcnow()  # Use UTC for global scheduling
        next_run = (now + timedelta(days=1)).replace(hour=1, minute=0, second=0, microsecond=0)
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
    # Send reminders for tomorrow's events
    events_tomorrow = get_tomorrows_events()
    for user_id, event_name, event_date in events_tomorrow:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"⏰ Reminder: Your event *{event_name}* is scheduled for tomorrow, *{event_date}*!",
                parse_mode="Markdown"
            )
        except (BotBlocked, UserDeactivated, ChatNotFound):
            pass
        except Exception:
            pass

        # Add delay to respect rate limits
        await asyncio.sleep(0.04)

    # Send reminders for today's events
    events_today = get_todays_events()
    for user_id, event_name, event_date in events_today:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"⏰ Reminder: Your event *{event_name}* is happening today, *{event_date}*!",
                parse_mode="Markdown"
            )
        except (BotBlocked, UserDeactivated, ChatNotFound):
            pass
        except Exception:
            pass

        # Add delay to respect rate limits
        await asyncio.sleep(0.04)


async def daily_event_task():
    while True:
        now = datetime.utcnow()  # Use UTC for global scheduling
        next_run = (now + timedelta(days=1)).replace(hour=1, minute=0, second=0, microsecond=0)
        #next_run = now + timedelta(seconds=10)
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

