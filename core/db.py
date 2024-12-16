import sqlite3
from datetime import datetime
from datetime import timedelta

DB_PATH = "db/bot.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            name TEXT NOT NULL,
            username TEXT,
            birthday DATE, -- New column for birthday,
            notifications_enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        event_name TEXT NOT NULL,
        event_date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        task_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    # Create admins table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# Check if a user exists by Telegram ID
def user_exists(telegram_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

# Add a user (only if new)
def add_user(telegram_id, name, username):
    if not user_exists(telegram_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO users (telegram_id, name, username) 
        VALUES (?, ?, ?)
        """, (telegram_id, name, username))
        conn.commit()
        conn.close()

#=========================================================================

def update_user_birthday(telegram_id, birthday):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET birthday = ? WHERE telegram_id = ?
    """, (birthday, telegram_id))
    conn.commit()
    conn.close()

def get_user_birthday(telegram_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT birthday FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def toggle_user_notifications(telegram_id, new_status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET notifications_enabled = ? WHERE telegram_id = ?", (new_status, telegram_id))
    conn.commit()
    conn.close()

def get_user_notifications_status(telegram_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT notifications_enabled FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def add_task(user_id, task_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (user_id, task_name) 
        VALUES (?, ?)
    """, (user_id, task_name))
    conn.commit()
    conn.close()

def get_tasks_by_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, task_name FROM tasks WHERE user_id = ?
    """, (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def delete_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id, birthday, notifications_enabled FROM users WHERE birthday IS NOT NULL")
    users = cursor.fetchall()
    conn.close()
    return users

def add_event(user_id, event_name, event_date):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO events (user_id, event_name, event_date)
        VALUES (?, ?, ?)
    """, (user_id, event_name, event_date))
    conn.commit()
    conn.close()

def delete_event(event_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM events WHERE id = ?
    """, (event_id,))
    conn.commit()
    conn.close()

def get_events_by_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, event_name, event_date FROM events WHERE user_id = ?
        ORDER BY event_date ASC
    """, (user_id,))
    events = cursor.fetchall()
    conn.close()
    return events


def get_tomorrows_events():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    cursor.execute("""
        SELECT user_id, event_name, event_date 
        FROM events 
        WHERE event_date = ?
    """, (tomorrow,))
    events = cursor.fetchall()
    conn.close()
    return events

def get_todays_events():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today = datetime.now().date()
    cursor.execute("""
        SELECT user_id, event_name, event_date 
        FROM events 
        WHERE event_date = ?
    """, (today,))
    events = cursor.fetchall()
    conn.close()
    return events


#=====================================================================================================


# Count total users
def count_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    conn.close()
    return total_users

# Count users who joined in the past 24 hours
def count_new_users_last_24_hours():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    past_24_hours = datetime.now() - timedelta(hours=24)
    cursor.execute("SELECT COUNT(*) FROM users WHERE created_at >= ?", (past_24_hours,))
    new_users = cursor.fetchone()[0]
    conn.close()
    return new_users

def clear_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users")  # Clear all rows from the users table
    conn.commit()
    conn.close()

# Get all user Telegram IDs
def get_user_ids():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id FROM users")
    telegram_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return telegram_ids

def add_admin(telegram_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR IGNORE INTO admins (telegram_id) 
    VALUES (?)
    """, (telegram_id,))
    conn.commit()
    conn.close()

def remove_admin(telegram_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    DELETE FROM admins 
    WHERE telegram_id = ?
    """, (telegram_id,))
    conn.commit()
    conn.close()

def count_admins():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM admins")
    total_admins = cursor.fetchone()[0]
    conn.close()
    return total_admins

def get_admins():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id FROM admins")
    admins = [row[0] for row in cursor.fetchall()]
    conn.close()
    return admins


def get_admin_details():
    admin_ids = get_admins()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT telegram_id, name FROM users WHERE telegram_id IN ({})
    """.format(','.join('?' * len(admin_ids))), admin_ids)
    admins_details = cursor.fetchall()
    conn.close()
    return admins_details


# Initialize the database
init_db()
