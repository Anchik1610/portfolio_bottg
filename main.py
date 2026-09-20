import html
from logic import DB_Manager
from config import *
from telebot import TeleBot, types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

# parse_mode='HTML' включает <b>жирный</b>, <i>курсив</i> во всех сообщениях бота
bot = TeleBot(TOKEN, parse_mode='HTML')
hideBoard = types.ReplyKeyboardRemove()

cancel_button = "Отмена 🚫"
LINE = "━━━━━━━━━━━━━━━"

# ==================== ОФОРМЛЕНИЕ ====================

STATUS_EMOJI = {
    'На этапе проектирования': '📝',
    'В процессе разработки': '🛠',
    'Разработан. Готов к использованию.': '✅',
    'Обновлен': '🔄',
    'Завершен. Не поддерживается': '🏁',
}

SKILL_EMOJI = {
    'Python': '🐍',
    'SQL': '🗄',
    'API': '🔌',
    'Telegram': '✈️',
}


def esc(text):
    """Экранируем пользовательский текст, чтобы символы < > & не ломали HTML-разметку."""
    return html.escape(str(text))


def format_skills(skills):
    """'Python, SQL' -> '🐍 Python  •  🗄 SQL'"""
    if not skills:
        return "пока не добавлены"
    names = [s.strip() for s in skills.split(',')]
    return "  •  ".join(f"{SKILL_EMOJI.get(s, '🔹')} {esc(s)}" for s in names)


def format_project_card(name, description, url, status, skills):
    emoji = STATUS_EMOJI.get(status, '📌')
    return (
        f"📁 <b>{esc(name)}</b>\n"
        f"{LINE}\n"
        f"📄 <b>Описание:</b> {esc(description) if description else 'не указано'}\n"
        f"🔗 <b>Ссылка:</b> {esc(url) if url else 'не указана'}\n"
        f"{emoji} <b>Статус:</b> {esc(status)}\n"
        f"🧩 <b>Навыки:</b> {format_skills(skills)}"
    )


def format_projects_list(projects):
    """projects — строки из SELECT * FROM Project:
    (project_id, user_id, project_name, description, url, status_id)"""
    status_names = dict(manager.get_statuses())  # {status_id: status_name}
    blocks = []
    for i, x in enumerate(projects, start=1):
        status = status_names.get(x[5], 'без статуса')
        emoji = STATUS_EMOJI.get(status, '📌')
        blocks.append(
            f"{i}. 📁 <b>{esc(x[2])}</b>\n"
            f"     🔗 {esc(x[4]) if x[4] else 'ссылка не указана'}\n"
            f"     {emoji} {esc(status)}"
        )
    return f"📋 <b>Твои проекты</b>\n{LINE}\n\n" + "\n\n".join(blocks)


# ==================== КЛАВИАТУРЫ ====================

def cansel(message):
    bot.send_message(message.chat.id, "❌ Действие отменено.\nЧтобы посмотреть команды, используй /info",
                     reply_markup=hideBoard)


def no_projects(message):
    bot.send_message(message.chat.id,
                     '📭 У тебя пока нет проектов!\nМожешь добавить их с помощью команды /new_project')


def gen_inline_markup(rows):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for row in rows:
        markup.add(InlineKeyboardButton(f"📁 {row}", callback_data=row))
    return markup


def gen_markup(rows):
    # Задание 1:
    # one_time_keyboard=True — клавиатура сама скрывается после нажатия на кнопку
    # resize_keyboard=True   — кнопки подгоняются по размеру (не занимают пол-экрана)
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row_width = 1
    for row in rows:
        markup.add(KeyboardButton(row))
    markup.add(KeyboardButton(cancel_button))
    return markup


attributes_of_projects = {
    '✏️ Имя проекта': ["Введите новое имя проекта ✏️", "project_name"],
    "📄 Описание": ["Введите новое описание проекта 📄", "description"],
    "🔗 Ссылка": ["Введите новую ссылку на проект 🔗", "url"],
    "📊 Статус": ["Выберите новый статус проекта 📊", "status_id"],
}


def info_project(message, user_id, project_name):
    rows = manager.get_project_info(user_id, project_name)
    if not rows:
        bot.send_message(message.chat.id, "🤷 Не могу найти такой проект.")
        return
    name, description, url, status = rows[0]
    skills = manager.get_project_skills(project_name, user_id)
    bot.send_message(message.chat.id, format_project_card(name, description, url, status, skills))


# ==================== КОМАНДЫ ====================

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, f"""👋 <b>Привет, {esc(message.from_user.first_name)}!</b>

Я — бот-менеджер проектов 🗂
Помогу сохранить твои проекты, ссылки, статусы и навыки в одном месте!
""")
    info(message)


# Задание 2: описание каждой команды
@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, f"""🤖 <b>Что я умею</b>
{LINE}

🆕 /new_project
Добавить новый проект: я спрошу название, описание, ссылку и статус.

📋 /projects
Показать список всех твоих проектов. Нажми на кнопку под списком, чтобы увидеть полную карточку проекта.

🧩 /skills
Привязать навык (Python, SQL, API, Telegram) к выбранному проекту.

✏️ /update_projects
Изменить проект: название, описание, ссылку или статус.

🗑 /delete
Удалить проект (вместе с привязанными навыками).

ℹ️ /info
Показать это сообщение со списком команд.

👋 /start
Перезапустить бота и увидеть приветствие.

{LINE}
💡 <b>Подсказка:</b> просто напиши название проекта, и я покажу информацию о нём.
🚫 На любом шаге можно нажать «{cancel_button}», чтобы выйти.""")


# ---------- Новый проект ----------

@bot.message_handler(commands=['new_project'])
def addtask_command(message):
    bot.send_message(message.chat.id, "🆕 <b>Новый проект</b>\n\nВведите название проекта:")
    bot.register_next_step_handler(message, name_project)


def name_project(message):
    name = message.text
    user_id = message.from_user.id
    data = [user_id, name]
    bot.send_message(message.chat.id, "📄 Введите описание проекта:")
    bot.register_next_step_handler(message, description_project, data=data)


def description_project(message, data):
    data.append(message.text)  # description
    bot.send_message(message.chat.id, "🔗 Введите ссылку на проект:")
    bot.register_next_step_handler(message, link_project, data=data)


def link_project(message, data):
    data.append(message.text)  # url
    statuses = [x[1] for x in manager.get_statuses()]
    bot.send_message(message.chat.id, "📊 Выберите текущий статус проекта:",
                     reply_markup=gen_markup(statuses))
    bot.register_next_step_handler(message, callback_project, data=data, statuses=statuses)


def callback_project(message, data, statuses):
    status = message.text
    if message.text == cancel_button:
        cansel(message)
        return
    if status not in statuses:
        bot.send_message(message.chat.id, "🤔 Ты выбрал статус не из списка, попробуй ещё раз!",
                         reply_markup=gen_markup(statuses))
        bot.register_next_step_handler(message, callback_project, data=data, statuses=statuses)
        return
    status_id = manager.get_status_id(status)
    data.append(status_id)
    manager.insert_project([tuple(data)])
    bot.send_message(message.chat.id, "🎉 <b>Проект сохранён!</b>\nПосмотреть все проекты: /projects",
                     reply_markup=hideBoard)


# ---------- Навыки ----------

@bot.message_handler(commands=['skills'])
def skill_handler(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, '🧩 Выбери проект, для которого нужно добавить навык:',
                         reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, skill_project, projects=projects)
    else:
        no_projects(message)


def skill_project(message, projects):
    project_name = message.text
    if message.text == cancel_button:
        cansel(message)
        return

    if project_name not in projects:
        bot.send_message(message.chat.id, '🤔 У тебя нет такого проекта, попробуй ещё раз!\nВыбери проект:',
                         reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, skill_project, projects=projects)
    else:
        skills = [x[1] for x in manager.get_skills()]
        bot.send_message(message.chat.id, '🎯 Выбери навык:', reply_markup=gen_markup(skills))
        bot.register_next_step_handler(message, set_skill, project_name=project_name, skills=skills)


def set_skill(message, project_name, skills):
    skill = message.text
    user_id = message.from_user.id
    if message.text == cancel_button:
        cansel(message)
        return

    if skill not in skills:
        bot.send_message(message.chat.id, '🤔 Такого навыка нет в списке, попробуй ещё раз!\nВыбери навык:',
                         reply_markup=gen_markup(skills))
        bot.register_next_step_handler(message, set_skill, project_name=project_name, skills=skills)
        return
    manager.insert_skill(user_id, project_name, skill)
    bot.send_message(message.chat.id,
                     f'✅ Навык {SKILL_EMOJI.get(skill, "🔹")} <b>{esc(skill)}</b> '
                     f'добавлен проекту <b>{esc(project_name)}</b>',
                     reply_markup=hideBoard)


# ---------- Список проектов ----------

@bot.message_handler(commands=['projects'])
def get_projects(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        text = format_projects_list(projects) + "\n\n👇 Нажми на проект, чтобы увидеть подробности"
        bot.send_message(message.chat.id, text, reply_markup=gen_inline_markup([x[2] for x in projects]))
    else:
        no_projects(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.answer_callback_query(call.id)  # убирает "часики" на нажатой кнопке
    info_project(call.message, call.from_user.id, call.data)


# ---------- Удаление ----------

@bot.message_handler(commands=['delete'])
def delete_handler(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        text = format_projects_list(projects) + "\n\n🗑 Выбери проект, который нужно удалить:"
        names = [x[2] for x in projects]
        bot.send_message(message.chat.id, text, reply_markup=gen_markup(names))
        bot.register_next_step_handler(message, delete_project, projects=names)
    else:
        no_projects(message)


def delete_project(message, projects):
    project = message.text
    user_id = message.from_user.id

    if message.text == cancel_button:
        cansel(message)
        return
    if project not in projects:
        bot.send_message(message.chat.id, '🤔 У тебя нет такого проекта, попробуй выбрать ещё раз!',
                         reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, delete_project, projects=projects)
        return
    project_id = manager.get_project_id(project, user_id)
    manager.delete_project(user_id, project_id)
    bot.send_message(message.chat.id, f'🗑 Проект <b>{esc(project)}</b> удалён!', reply_markup=hideBoard)


# ---------- Изменение проекта ----------

@bot.message_handler(commands=['update_projects'])
def update_project(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, "✏️ Выбери проект, который хочешь изменить:",
                         reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, update_project_step_2, projects=projects)
    else:
        no_projects(message)


def update_project_step_2(message, projects):
    project_name = message.text
    if message.text == cancel_button:
        cansel(message)
        return
    if project_name not in projects:
        bot.send_message(message.chat.id, "🤔 Что-то пошло не так! Выбери проект, который хочешь изменить, ещё раз:",
                         reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, update_project_step_2, projects=projects)
        return
    bot.send_message(message.chat.id, "🔧 Выбери, что требуется изменить в проекте:",
                     reply_markup=gen_markup(attributes_of_projects.keys()))
    bot.register_next_step_handler(message, update_project_step_3, project_name=project_name)


def update_project_step_3(message, project_name):
    attribute = message.text
    reply_markup = hideBoard  # для текстовых полей клавиатура не нужна — убираем её
    if message.text == cancel_button:
        cansel(message)
        return
    if attribute not in attributes_of_projects.keys():
        bot.send_message(message.chat.id, "🤔 Кажется, ты ошибся, попробуй ещё раз!",
                         reply_markup=gen_markup(attributes_of_projects.keys()))
        bot.register_next_step_handler(message, update_project_step_3, project_name=project_name)
        return
    elif attribute == "📊 Статус":
        rows = manager.get_statuses()
        reply_markup = gen_markup([x[1] for x in rows])  # x[1] — название статуса
    bot.send_message(message.chat.id, attributes_of_projects[attribute][0], reply_markup=reply_markup)
    bot.register_next_step_handler(message, update_project_step_4, project_name=project_name,
                                   attribute=attributes_of_projects[attribute][1])


def update_project_step_4(message, project_name, attribute):
    update_info = message.text
    if attribute == "status_id":
        rows = manager.get_statuses()
        status_names = [x[1] for x in rows]
        if update_info in status_names:
            update_info = manager.get_status_id(update_info)
        elif update_info == cancel_button:
            cansel(message)
            return
        else:
            bot.send_message(message.chat.id, "🤔 Был выбран неверный статус, попробуй ещё раз!",
                             reply_markup=gen_markup(status_names))
            bot.register_next_step_handler(message, update_project_step_4,
                                           project_name=project_name, attribute=attribute)
            return
    user_id = message.from_user.id
    data = (update_info, project_name, user_id)
    manager.update_projects(attribute, data)
    bot.send_message(message.chat.id, "✨ Готово! Обновления внесены!", reply_markup=hideBoard)


# ---------- Любой другой текст ----------

@bot.message_handler(func=lambda message: True)
def text_handler(message):
    user_id = message.from_user.id
    projects = [x[2] for x in manager.get_projects(user_id)]
    project = message.text
    if project in projects:
        info_project(message, user_id, project)
        return
    bot.reply_to(message, "🤖 Тебе нужна помощь?")
    info(message)


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    bot.delete_webhook()
    bot.infinity_polling()