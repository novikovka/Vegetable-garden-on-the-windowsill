import telebot
from telebot import types
import json
import os
from typing import Dict, Any
from flask import Flask, request, jsonify
import threading
import requests

# Конфигурация
STATE_FILE = "state.json"
bot = telebot.TeleBot('7789381064:AAFFdBdqwiNBJrq16UExKKLiprnDpCpRACo')  # Чистовик

# Настройки соединения с ESP8266
ESP8266_URL = "http://<IP_ESP8266>/control"  # Замените на реальный IP ESP8266
ESP8266_UPDATE_INTERVAL = 5  # Интервал обновления данных с датчиков (в секундах)

# Инициализация Flask-сервера
app = Flask(__name__)

# Глобальные переменные для хранения данных с датчиков
sensor_data = {
    'temperature': 30,
    'humidity': 80,
    'illumination': 50,
    'water_level': 60
}

# Состояния пользователей
user_input_steps: Dict[str, Dict] = {}
user_states: Dict[str, Dict] = {}

authorized_users = {}  # user_id -> True/False

VALID_TOKENS = ["123", "456"]  # список допустимых токенов

@bot.message_handler(commands=['auth'])
def handle_auth(message):
    try:
        token = message.text.split()[1]
        if token in VALID_TOKENS:
            authorized_users[message.from_user.id] = True
            bot.reply_to(message, "✅ Вы успешно авторизованы.")
        else:
            bot.reply_to(message, "❌ Неверный токен.")
    except IndexError:
        bot.reply_to(message, "⚠️ Используйте: /auth <токен>")



# Загрузка состояний из файла
def load_states():
    global user_states
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            user_states = json.load(f)


def save_states():
    with open(STATE_FILE, "w") as f:
        json.dump(user_states, f, indent=4)


# Инициализация состояния пользователя
def init_user_state(user_id: str):
    if user_id not in user_states:
        user_states[user_id] = {
            "light": False,
            "watering": False,
            "actions": {},
            "notifications": {}
        }
        save_states()


# Эндпоинт для приема данных от ESP8266
@app.route('/update_sensors', methods=['POST'])
def update_sensors():
    global sensor_data
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Обновляем только те данные, которые пришли
        for key in data:
            if key in sensor_data:
                sensor_data[key] = data[key]

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Функция для отправки команд на ESP8266
def send_command_to_esp(command: str, value: Any) -> bool:
    try:
        payload = {command: value}
        response = requests.post(ESP8266_URL, json=payload, timeout=3)
        if response.status_code == 200:
            return True
        else:
            print(f"Ошибка отправки команды: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Ошибка соединения с ESP8266: {e}")
        return False

'''
# Обработчики команд Telegram
@bot.message_handler(commands=["settings", "sensors", "notifications"])
def handle_commands(message):
    user_id = str(message.chat.id)

    init_user_state(user_id)

    command = message.text[1:]
    if command == "settings":
        send_settings(message)
    elif command == "sensors":
        send_controls(message)
    elif command == "notifications":
        send_notifications(message)

'''
@bot.message_handler(commands=["settings", "sensors", "notifications"])
def handle_commands(message):
    user_id = message.from_user.id
    if not authorized_users.get(user_id):
        bot.reply_to(message, '❌ Вы не авторизованы. Введите Ваш уникальный токен в формате "/auth <токен>". Например "/auth token123"')
        return

    uid_str = str(user_id)
    init_user_state(uid_str)

    command = message.text[1:]
    if command == "settings":
        send_settings(message)
    elif command == "sensors":
        send_controls(message)
    elif command == "notifications":
        send_notifications(message)


# Обработчик callback-запросов
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    if not authorized_users.get(user_id):
        bot.answer_callback_query(call.id, "❌ Вы не авторизованы. Введите /auth <токен>.")
        return

    user_id = str(call.message.chat.id)
    init_user_state(user_id)


    call_handlers = {
        'settings': lambda: send_settings(call.message),
        'sensors': lambda: send_controls(call.message),
        'notifications': lambda: send_notifications(call.message),
        'light_on': lambda: toggle_light(user_id, True, call),
        'light_off': lambda: toggle_light(user_id, False, call),
        'watering_on': lambda: toggle_watering(user_id, True, call),
        'watering_off': lambda: toggle_watering(user_id, False, call),
        'custom_button_1': lambda: start_input_sequence(user_id, 1, call.message, "Введите час (целое число):"),
        'custom_button_2': lambda: start_input_sequence(user_id, 3, call.message, "Введите час (целое число):"),
        'custom_button_3': lambda: start_input_sequence(user_id, 5, call.message, "Введите час (целое число):"),
        'custom_button_4': lambda: start_input_sequence(user_id, 7, call.message, "Введите номер действия:"),
        'custom_1': lambda: add_notifications_buttons(call.message),
        'custom_2': lambda: start_input_sequence(user_id, 30, call.message, "Введите номер триггера:"),
        'custom_11': lambda: start_input_sequence(user_id, 8, call.message,
                                                  "Введите значение параметра 'влажность' при котором Вы хотите получать уведомление:"),
        'custom_12': lambda: start_input_sequence(user_id, 9, call.message,
                                                  "Введите значение параметра 'температура' при котором Вы хотите получать уведомление:"),
        'custom_13': lambda: start_input_sequence(user_id, 10, call.message,
                                                  "Введите значение параметра 'освещенность' при котором Вы хотите получать уведомление:"),
        'custom_14': lambda: start_input_sequence(user_id, 11, call.message,
                                                  "Введите значение параметра 'уровень воды' при котором Вы хотите получать уведомление:")
    }

    if call.data in call_handlers:
        call_handlers[call.data]()
        save_states()


def toggle_light(user_id: str, state: bool, call):
    user_states[user_id]["light"] = state
    emoji = "💡" if state else "🌑"
    if send_command_to_esp("light", int(state)):
        bot.answer_callback_query(call.id, f"Свет {'включен' if state else 'выключен'} {emoji}")
    else:
        bot.answer_callback_query(call.id, "⚠️ Ошибка отправки команды на устройство")
    update_controls_inline_keyboard(call)


def toggle_watering(user_id: str, state: bool, call):
    user_states[user_id]["watering"] = state
    emoji = "💦" if state else "🚱"
    if send_command_to_esp("watering", int(state)):
        bot.answer_callback_query(call.id, f"Полив {'включен' if state else 'выключен'} {emoji}")
    else:
        bot.answer_callback_query(call.id, "⚠️ Ошибка отправки команды на устройство")
    update_controls_inline_keyboard(call)


def start_input_sequence(user_id: str, step: int, message, prompt: str):
    user_input_steps[user_id] = {"step": step}
    bot.send_message(message.chat.id, prompt)


# Обработчик ввода данных пользователем
@bot.message_handler(func=lambda message: str(message.chat.id) in user_input_steps)
def handle_user_input(message):
    user_id = str(message.chat.id)
    step_info = user_input_steps[user_id]
    step = step_info["step"]

    try:
        if step in [1, 3, 5]:  # Ввод часа
            hour = validate_number(message.text, 0, 23)
            step_info["hour"] = hour
            step_info["step"] += 1
            bot.send_message(message.chat.id, "Теперь введите минуту (целое число):")

        elif step in [2, 4, 6]:  # Ввод минуты
            minute = validate_number(message.text, 0, 59)
            hour = step_info["hour"]

            action_types = {
                2: ("watering", "on"),
                4: ("light", "on"),
                6: ("light", "off")
            }

            action_type, action_state = action_types[step]
            add_action(user_id, action_type, action_state, hour, minute, message)

        elif step in [8, 9, 10, 11]:  # Триггеры уведомлений
            trigger = validate_number(message.text, 0, 100)
            trigger_types = {
                8: "humidity",
                9: "temperature",
                10: "illumination",
                11: "water_level"
            }
            add_notification(user_id, trigger_types[step], trigger, message)

        elif step in [7, 30]:  # Удаление действий/триггеров
            action_id = message.text
            target = "actions" if step == 7 else "notifications"

            if user_id in user_states and action_id in user_states[user_id].get(target, {}):
                del user_states[user_id][target][action_id]
                save_states()
                bot.send_message(message.chat.id,
                                 f"{'Действие' if step == 7 else 'Триггер'} #{action_id} успешно удалено.")
                user_input_steps.pop(user_id)
            else:
                bot.send_message(message.chat.id,
                                 f"{'Действие' if step == 7 else 'Триггер'} с таким ID не найдено. Пожалуйста, введите корректный ID:")

    except ValueError as e:
        bot.send_message(message.chat.id, str(e))


def validate_number(text: str, min_val: int, max_val: int) -> int:
    num = int(text)
    if not (min_val <= num <= max_val):
        raise ValueError(f"Пожалуйста, введите число от {min_val} до {max_val}.")
    return num


def add_action(user_id: str, action_type: str, action_state: str, hour: int, minute: int, message):
    actions = user_states[user_id].setdefault("actions", {})
    next_id = str(max([int(k) for k in actions.keys()] + [0]) + 1)

    actions[next_id] = {
        "type": action_type,
        "boolean": action_state,
        "hour": hour,
        "minute": minute
    }

    save_states()
    bot.send_message(message.chat.id, f"Сохранено как действие #{next_id}.")
    user_input_steps.pop(user_id)


def add_notification(user_id: str, note_type: str, trigger: int, message):
    notifications = user_states[user_id].setdefault("notifications", {})
    next_id = str(max([int(k) for k in notifications.keys()] + [0]) + 1)

    notifications[next_id] = {
        "type": note_type,
        "trigger": trigger
    }

    save_states()
    bot.send_message(message.chat.id, f"Сохранено как триггер #{next_id}.")
    user_input_steps.pop(user_id)


# Функции отправки сообщений
def send_notifications(message):
    user_id = str(message.chat.id)
    notifications = user_states.get(user_id, {}).get("notifications", {})

    type_emoji = {
        "humidity": "💧 Влажность",
        "temperature": "🌡 Температура",
        "illumination": "🔆 Освещённость",
        "water_level": "🚰 Уровень воды"
    }

    notifications_text = "*Уведомления:*\n\n" + "\n".join(
        f"• #{note_id} — {type_emoji.get(note['type'], note['type'])}, триггер: {note['trigger']}"
        for note_id, note in notifications.items()
    ) if notifications else "_У вас пока нет триггеров уведомлений._"

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Добавить триггер", callback_data="custom_1"),
        types.InlineKeyboardButton("Удалить триггер", callback_data="custom_2")
    )

    bot.send_message(message.chat.id, notifications_text, parse_mode='Markdown', reply_markup=markup)


def add_notifications_buttons(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Влажность", callback_data="custom_11"),
        types.InlineKeyboardButton("Температура", callback_data="custom_12"),
        types.InlineKeyboardButton("Освещенность", callback_data="custom_13"),
        types.InlineKeyboardButton("Уровень воды", callback_data="custom_14")
    )

    bot.send_message(message.chat.id, "Выберите параметр для триггера:", parse_mode='Markdown', reply_markup=markup)


def send_settings(message):
    user_id = str(message.chat.id)
    actions = user_states.get(user_id, {}).get("actions", {})

    action_types = {
        "watering": "💧 Полив",
        "light": "💡 Свет"
    }

    actions_text = "*Ваши сохранённые действия:*\n\n" + "\n".join(
        f"• #{action_id} — {action_types.get(action['type'], action['type'])}, "
        f"{'вкл' if action['boolean'] == 'on' else 'выкл'} в {action['hour']:02d}:{action['minute']:02d}"
        for action_id, action in actions.items()
    ) if actions else "_У вас пока нет сохранённых действий._"

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💧 Добавить включение полива", callback_data="custom_button_1"),
        types.InlineKeyboardButton("💡 Добавить включение освещения", callback_data="custom_button_2"),
        types.InlineKeyboardButton("🔌 Добавить выключение освещения", callback_data="custom_button_3"),
        types.InlineKeyboardButton("🚫 Удалить действие", callback_data="custom_button_4")
    )

    bot.send_message(message.chat.id, actions_text, parse_mode='Markdown')
    bot.send_message(message.chat.id, "Настройки системы:", reply_markup=markup)


def send_controls(message):
    user_id = str(message.chat.id)
    state = user_states.get(user_id, {"light": False, "watering": False})

    sensor_text = (
        "*Текущие показания датчиков:*\n\n"
        f"🌡️ Температура: *{sensor_data['temperature']}°C*\n\n"
        f"💧 Влажность: *{sensor_data['humidity']}%*\n\n"
        f"💡 Освещение: *{sensor_data['illumination']} лк*\n\n"
        f"🚰 Уровень воды: *{sensor_data['water_level']}%*"
    )

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            "💡 Включить свет" if not state["light"] else "🔌 Выключить свет",
            callback_data="light_off" if state["light"] else "light_on"
        ),
        types.InlineKeyboardButton(
            "💧 Включить полив" if not state["watering"] else "🚫 Выключить полив",
            callback_data="watering_off" if state["watering"] else "watering_on"
        )
    )

    bot.send_message(message.chat.id, sensor_text, parse_mode='Markdown', reply_markup=markup)


def update_controls_inline_keyboard(call):
    user_id = str(call.message.chat.id)
    state = user_states.get(user_id, {"light": False, "watering": False})

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            "💡 Включить свет" if not state["light"] else "🔌 Выключить свет",
            callback_data="light_off" if state["light"] else "light_on"
        ),
        types.InlineKeyboardButton(
            "💧 Включить полив" if not state["watering"] else "🚫 Выключить полив",
            callback_data="watering_off" if state["watering"] else "watering_on"
        )
    )

    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )


def run_flask():
    app.run(host='0.0.0.0', port=5000)


# Запуск бота
if __name__ == "__main__":
    load_states()

    # Запускаем Flask-сервер в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Запускаем Telegram-бота
    bot.polling(none_stop=True)