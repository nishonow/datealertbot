messages = {
  "en": {
    "welcome_with_birthday": (
            "*Welcome to Date Alert Bot!*\n\n"
            "📅 I'm here to help you manage your events and daily tasks.\n\n"
            "🔔 I will remind you one day before your events, so you never miss anything important.\n"
            "📝 You can also use me to keep track of your to-do tasks effortlessly.\n\n"
            "Let's get started and make your life more organized!"
        ),
        "welcome_without_birthday": (
            "*Welcome to Date Alert Bot!*\n\n"
            "I'm here to help you remember birthdays, events, and your daily to-do tasks.\n"
            "Let's start by adding your *birthday*.\n\n"
            "📅 Please enter your birthday in this format: *YYYY-MM-DD*"
        ),
        "birthday_saved": "🎂 Got it! Your birthday is saved as *{birthday}*. I'll remind you every day! 🎉",
        "invalid_birthday_format": "❌ Please enter the date in the correct format: *YYYY-MM-DD*.",
    "action_cancelled": "✅ Action cancelled. You can start again whenever you like.",
    "settings_menu": "⚙️ *Settings Menu*\n\n{birthday_message}\n\nChoose an option below:",
    "no_birthday_set": "❌ You haven't set your birthday yet.",
    "birthday_set": "🎂 Your birthday is currently set to: *{birthday}*",
    "toggle_notifications_on": "🔔 Great! You will now receive notifications for your events and reminders!",
    "toggle_notifications_off": "🔕 Notifications are now turned off. Don't worry, you can always turn them back on in settings!",
    "enter_new_birthday": "✏️ Please enter your new birthday in the format: *YYYY-MM-DD*\n\nFor example: `1990-05-25`\n\nUse /cancel to stop the action.",
    "birthday_updated": "🎉 Your birthday has been updated to: *{birthday}*\n\nI’ll make sure to remind you when your special day is near!",
    "invalid_date_format": "❌ Invalid date format. Please enter your birthday in the format: *YYYY-MM-DD*\n\nFor example: `1990-05-25`\n\nUse /cancel to stop the action.",
    "add_task_prompt": "📝 Please enter the name of the task:\n\nUse /cancel to stop the action.",
    "task_added": "✅ Task {task_name} has been added successfully. Use /view_tasks to see your tasks!",
    "no_tasks": "🗂️ You have no tasks yet. Use /add_task to create one!",
    "task_deleted": "✅ Task {task_name} has been deleted successfully!",
    "add_event_prompt": "📝 Please enter the event name:\n\nUse /cancel to stop the action.",
    "enter_event_date": "📅 Now, enter the event date in the format YYYY-MM-DD:\n\nUse /cancel to stop the action.",
    "event_added": "✅ Event {event_name} on {event_date} has been added successfully. Use /view_events to see your upcoming events!",
    "no_events": "🗂️ You have no events. Use /add_event to create one!",
    "event_deleted": "✅ Event {event_name} has been deleted.",
    "your_birthday": "🎉 Your birthday is on *{birthday}*.\n🎂 Only *{days_until_birthday} days* left until your next birthday!",
    "no_birthday_set_short": "❌ You haven't set your birthday yet. Use the settings menu to add it!"
  },
  "ru": {
    "welcome_with_birthday": (
            "*Добро пожаловать в Date Alert Bot!*\n\n"
            "📅 Я помогу вам управлять событиями и ежедневными задачами.\n\n"
            "🔔 Я напомню вам за день до событий, чтобы вы ничего не пропустили.\n"
            "📝 Вы также можете использовать меня для отслеживания ваших задач.\n\n"
            "Давайте начнем и сделаем вашу жизнь более организованной!"
        ),
        "welcome_without_birthday": (
            "*Добро пожаловать в Date Alert Bot!*\n\n"
            "Я помогу вам запомнить дни рождения, события и ежедневные задачи.\n"
            "Давайте начнем с добавления вашей *даты рождения*.\n\n"
            "📅 Пожалуйста, введите дату рождения в формате: *YYYY-MM-DD*"
        ),
        "birthday_saved": "🎂 Отлично! Ваша дата рождения сохранена как *{birthday}*. Я буду напоминать вам каждый год! 🎉",
        "invalid_birthday_format": "❌ Пожалуйста, введите дату в правильном формате: *YYYY-MM-DD*.",
    "action_cancelled": "✅ Действие отменено. Вы можете начать заново в любое время.",
    "settings_menu": "⚙️ *Меню настроек*\n\n{birthday_message}\n\nВыберите опцию ниже:",
    "no_birthday_set": "❌ Вы еще не установили дату своего дня рождения.",
    "birthday_set": "🎂 Ваша дата рождения: *{birthday}*",
    "toggle_notifications_on": "🔔 Отлично! Теперь вы будете получать уведомления о событиях и напоминаниях!",
    "toggle_notifications_off": "🔕 Уведомления отключены. Не волнуйтесь, вы всегда можете включить их в настройках!",
    "enter_new_birthday": "✏️ Пожалуйста, введите новую дату рождения в формате: *ГГГГ-ММ-ДД*\n\nНапример: `1990-05-25`\n\nИспользуйте /cancel, чтобы остановить действие.",
    "birthday_updated": "🎉 Ваша дата рождения обновлена: *{birthday}*\n\nЯ напомню вам, когда ваш особенный день приблизится!",
    "invalid_date_format": "❌ Неверный формат даты. Пожалуйста, введите дату рождения в формате: *ГГГГ-ММ-ДД*\n\nНапример: `1990-05-25`\n\nИспользуйте /cancel, чтобы остановить действие.",
    "add_task_prompt": "📝 Пожалуйста, введите название задачи:\n\nИспользуйте /cancel, чтобы остановить действие.",
    "task_added": "✅ Задача {task_name} успешно добавлена. Используйте /view_tasks, чтобы увидеть ваши задачи!",
    "no_tasks": "🗂️ У вас еще нет задач. Используйте /add_task, чтобы создать задачу!",
    "task_deleted": "✅ Задача {task_name} успешно удалена!",
    "add_event_prompt": "📝 Пожалуйста, введите название события:\n\nИспользуйте /cancel, чтобы остановить действие.",
    "enter_event_date": "📅 Теперь введите дату события в формате ГГГГ-ММ-ДД:\n\nИспользуйте /cancel, чтобы остановить действие.",
    "event_added": "✅ Событие {event_name} на {event_date} успешно добавлено. Используйте /view_events, чтобы увидеть предстоящие события!",
    "no_events": "🗂️ У вас нет событий. Используйте /add_event, чтобы создать одно!",
    "event_deleted": "✅ Событие {event_name} успешно удалено.",
    "your_birthday": "🎉 Ваш день рождения: *{birthday}*.\n🎂 Осталось всего *{days_until_birthday} дней* до следующего дня рождения!",
    "no_birthday_set_short": "❌ Вы еще не установили дату своего дня рождения. Используйте меню настроек, чтобы добавить её!"
  }
}

keyboards = {
    "en": {
        "my_birthday": "🎂 My Birthday",
        "add_event": "➕ Add Event",
        "view_events": "📅 View Events",
        "add_task": "📝 Add Task",
        "view_tasks": "✅ View Tasks",
        "settings": "⚙️ Settings",
        "edit_birthday": "✏️ Edit Birthday",
        "notifications_on": "🔔 Notifications ON",
        "notifications_off": "🔕 Notifications OFF"
    },
    "ru": {
        "my_birthday": "🎂 Мой День Рождения",
        "add_event": "➕ Добавить Событие",
        "view_events": "📅 Просмотреть События",
        "add_task": "📝 Добавить Задачу",
        "view_tasks": "✅ Просмотреть Задачи",
        "settings": "⚙️ Настройки",
        "edit_birthday": "✏️ Изменить День Рождения",
        "notifications_on": "🔔 Уведомления ВКЛ",
        "notifications_off": "🔕 Уведомления ВЫКЛ"
    }
}
