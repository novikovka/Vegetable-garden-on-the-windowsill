import telebot
from telebot import types
import json
import os
from typing import Dict, Any
import requests
import threading

STATE_FILE = "state.json"
TOKEN = '7789381064:AAFFdBdqwiNBJrq16UExKKLiprnDpCpRACo'
ESP_URL = 'http://192.168.0.109'
VALID_TOKENS = ["123", "456"]
authorized_users = {}
bot = telebot.TeleBot(TOKEN)

TEMPER = 88  # Примерная температура, её вы можете менять по ходу
TEMPER_2 = 30
TEMPER_3 = 90

global_state = {}
sent_notifications = set()  # Храним пары (user_id, trigger_value)

DEFAULT_SENSOR_VALUES = {
    'temperature': 30,
    'humidity': 80,
    'illumination': 50,
    'water_level': 60
}

user_input_steps: Dict[str, Dict] = {}
user_states: Dict[str, Dict] = {}

def load_states():
    global user_states
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            user_states = json.load(f)

def save_states():
    with open(STATE_FILE, "w") as f:
        json.dump(user_states, f, indent=4)

def init_user_state(user_id: str):
    if user_id not in user_states:
        user_states[user_id] = {
            "light": False,
            "watering": False,
            "actions": {},
            "notifications": {}
        }
        save_states()

def load_state():
    try:
        with open("state.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка чтения state.json: {e}")
        return {}

'''
def check_temperature_triggers():
    global global_state, TEMPER, sent_notifications

    new_state = load_state()
    data = fetch_sensor_data()

    for user_id, settings in new_state.items():
        notifications = settings.get("notifications", {})
        for _, notif in notifications.items():
            if notif.get("type") == "temperature":
                trigger = notif.get("trigger")
                key = (user_id, trigger)
                if data.get('temperature', '?') == trigger and key not in sent_notifications:
                    try:
                        bot.send_message(user_id, f"🌡 Температура достигла значения {data.get('temperature', '?')}°C")
                        sent_notifications.add(key)  # Отметили как отправленное
                    except Exception as e:
                        print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
                elif data.get('temperature', '?') != trigger and key in sent_notifications:
                    sent_notifications.remove(
                        key)  # Если температура ушла от триггера — можно снова уведомлять в будущем
            elif notif.get("type") == "humidity":
                trigger = notif.get("trigger")
                key = (user_id, trigger)
                if data.get('humidity', '?') == trigger and key not in sent_notifications:
                    try:
                        bot.send_message(user_id, f"🌡 Влажность воздуха достигла значения {data.get('humidity', '?')}°C")
                        sent_notifications.add(key)  # Отметили как отправленное
                    except Exception as e:
                        print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
                elif data.get('humidity', '?') != trigger and key in sent_notifications:
                    sent_notifications.remove(
                        key)  # Если температура ушла от триггера — можно снова уведомлять в будущем
            elif notif.get("type") == "soil_moisture":
                trigger = notif.get("trigger")
                key = (user_id, trigger)
                if data.get('soil_moisture', '?') == trigger and key not in sent_notifications:
                    try:
                        bot.send_message(user_id, f"🌡 Влажность почвы достигла значения {data.get('soil_moisture', '?')}°C")
                        sent_notifications.add(key)  # Отметили как отправленное
                    except Exception as e:
                        print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
                elif data.get('soil_moisture', '?') != trigger and key in sent_notifications:
                    sent_notifications.remove(
                        key)  # Если температура ушла от триггера — можно снова уведомлять в будущем

    global_state = new_state

    # Повторить через 60 секунд
    threading.Timer(60, check_temperature_triggers).start()
'''

def check_temperature_triggers(): #для тестирования
    global global_state, TEMPER, sent_notifications

    new_state = load_state()
    # data = fetch_sensor_data()

    for user_id, settings in new_state.items():
        notifications = settings.get("notifications", {})
        for _, notif in notifications.items():
            if notif.get("type") == "temperature":
                trigger = notif.get("trigger")
                key = (user_id, trigger)
                if TEMPER == trigger and key not in sent_notifications:
                    try:
                        bot.send_message(user_id, f"🌡 Температура достигла значения {TEMPER}°C")
                        sent_notifications.add(key)  # Отметили как отправленное
                    except Exception as e:
                        print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
                elif TEMPER != trigger and key in sent_notifications:
                    sent_notifications.remove(
                        key)  # Если температура ушла от триггера — можно снова уведомлять в будущем
            elif notif.get("type") == "humidity":
                trigger = notif.get("trigger")
                key = (user_id, trigger)
                if TEMPER_2 == trigger and key not in sent_notifications:
                    try:
                        bot.send_message(user_id, f"🌡 Влажность воздуха достигла значения {TEMPER_2}°C")
                        sent_notifications.add(key)  # Отметили как отправленное
                    except Exception as e:
                        print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
                elif TEMPER_2 != trigger and key in sent_notifications:
                    sent_notifications.remove(
                        key)  # Если температура ушла от триггера — можно снова уведомлять в будущем
            elif notif.get("type") == "soil_moisture":
                trigger = notif.get("trigger")
                key = (user_id, trigger)
                if TEMPER_3 == trigger and key not in sent_notifications:
                    try:
                        bot.send_message(user_id, f"🌡 Влажность почвы достигла значения {TEMPER_3}°C")
                        sent_notifications.add(key)  # Отметили как отправленное
                    except Exception as e:
                        print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
                elif TEMPER_3 != trigger and key in sent_notifications:
                    sent_notifications.remove(
                        key)  # Если температура ушла от триггера — можно снова уведомлять в будущем

    global_state = new_state

    # Повторить через 60 секунд
    threading.Timer(60, check_temperature_triggers).start()

# Инициализация
global_state = load_state()
print(global_state)
check_temperature_triggers()


@bot.message_handler(commands=["settings", "sensors", "notifications"])
def handle_commands(message):
    user_id = str(message.chat.id)
    init_user_state(user_id)

    if message.from_user.id not in authorized_users:
        bot.reply_to(message, "❌ Вы не авторизованы. Используйте /auth <токен>")
        return

    command = message.text[1:]
    if command == "settings":
        send_settings(message)
    elif command == "sensors":
        send_controls(message)
    elif command == "notifications":
        send_notifications(message)

@bot.message_handler(commands=['auth'])
def handle_auth(message):
    try:
        token = message.text.split()[1]
        if token in VALID_TOKENS:
            authorized_users[message.from_user.id] = True
            bot.reply_to(message, "✅ Авторизация успешна.")
        else:
            bot.reply_to(message, "❌ Неверный токен.")
    except IndexError:
        bot.reply_to(message, "⚠️ Используйте: /auth <токен>")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = str(call.message.chat.id)
    init_user_state(user_id)

    call_handlers = {
        'settings': lambda: send_settings(call.message),
        'sensors': lambda: send_controls(call.message),
        'notifications': lambda: send_notifications(call.message),
        'light_on': lambda: handle_device_switch(user_id, call, 1, True, 'light'),
        'light_off': lambda: handle_device_switch(user_id, call, 1, False, 'light'),
        'watering_on': lambda: handle_device_switch(user_id, call, 2, True, 'watering'),
        'watering_off': lambda: handle_device_switch(user_id, call, 2, False, 'watering'),
        'custom_button_1': lambda: start_input_sequence(user_id, 1, call.message, "Введите час (целое число):"),
        'custom_button_2': lambda: start_input_sequence(user_id, 3, call.message, "Введите час (целое число):"),
        'custom_button_3': lambda: start_input_sequence(user_id, 5, call.message, "Введите час (целое число):"),
        'custom_button_4': lambda: start_input_sequence(user_id, 7, call.message, "Введите номер действия:"),
        'custom_1': lambda: add_notifications_buttons(call.message),
        'custom_2': lambda: start_input_sequence(user_id, 30, call.message, "Введите номер триггера:"),
        'custom_11': lambda: start_input_sequence(user_id, 8, call.message, "Введите значение параметра 'температура' при котором Вы хотите получать уведомление:"),
        'custom_12': lambda: start_input_sequence(user_id, 9, call.message, "Введите значение параметра 'влажность воздуха' при котором Вы хотите получать уведомление:"),
        'custom_13': lambda: start_input_sequence(user_id, 10, call.message, "Введите значение параметра 'влажность почвы' при котором Вы хотите получать уведомление:")
        #'custom_14': lambda: start_input_sequence(user_id, 11, call.message, "Введите значение параметра 'уровень воды' при котором Вы хотите получать уведомление:")
    }

    if call.data in call_handlers:
        call_handlers[call.data]()
        save_states()

def handle_device_switch(user_id: str, call, relay_num: int, state: bool, state_key: str):
    user_states[user_id][state_key] = state
    flag = "on" if state else "off"
    try:
        requests.get(f"{ESP_URL}/relay?num={relay_num}&state={flag}", timeout=3)
        emoji = "💦" if state_key == "watering" and state else "🚱"
        if state_key == "light":
            emoji = "💡" if state else "🌑"
        bot.answer_callback_query(call.id, f"{state_key.capitalize()} {'включен' if state else 'выключен'} {emoji}")
    except Exception as e:
        bot.answer_callback_query(call.id, f"Ошибка подключения к ESP: {e}")

    update_controls_inline_keyboard(call)


def toggle_light(user_id: str, state: bool, call):
    user_states[user_id]["light"] = state
    emoji = "💡" if state else "🌑"
    bot.answer_callback_query(call.id, f"Свет {'включен' if state else 'выключен'} {emoji}")
    update_controls_inline_keyboard(call)


def toggle_watering(user_id: str, state: bool, call):
    user_states[user_id]["watering"] = state
    emoji = "💦" if state else "🚱"
    bot.answer_callback_query(call.id, f"Полив {'включен' if state else 'выключен'} {emoji}")
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

        elif step in [8, 9, 10]:  # Триггеры уведомлений
            trigger = validate_number(message.text, 0, 100)
            trigger_types = {
                8: "temperature",
                9: "humidity",
                10: "soil_moisture"
                #11: "water_level"
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


# ========== Работа с ESP ==========

# Функция для получения данных с датчиков с ESP8266
def fetch_sensor_data():
    try:
        resp = requests.get(f"{ESP_URL}/update_sensors", timeout=3)
        if resp.status_code == 200:
            return resp.json()  # Возвращает словарь с данными
        else:
            return {"error": "ESP вернул ошибку"}
    except Exception as e:
        return {"error": f"Ошибка подключения: {e}"}

# Функция для кратковременного включения реле (включить и сразу выключить)
def control_relay(num):
    try:
        requests.get(f"{ESP_URL}/relay?num={num}&state=on", timeout=3)
        #requests.get(f"{ESP_URL}/relay?num={num}&state=off", timeout=3)
        return True
    except:
        return False

# ========== Работа с ESP ==========

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
        "temperature": "🌡 Температура",
        "humidity": "🔆 Влажность воздуха",
        "soil_moisture": "💧 Влажность почвы"
    }

    notifications_text = "Триггеры уведомлений\n\n" + "\n".join(
        f"• #{note_id} — {type_emoji.get(note['type'], note['type'])}: {note['trigger']}"
        for note_id, note in notifications.items()
    ) if notifications else "_У вас пока нет триггеров уведомлений._"

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Добавить триггер", callback_data="custom_1"),
        types.InlineKeyboardButton("Удалить триггер", callback_data="custom_2")
    )

    bot.send_message(message.chat.id, notifications_text, reply_markup=markup)


def add_notifications_buttons(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Влажность воздуха", callback_data="custom_12"),
        types.InlineKeyboardButton("Влажность почвы", callback_data="custom_13"),
        types.InlineKeyboardButton("Температура", callback_data="custom_11")
        #types.InlineKeyboardButton("Уровень воды", callback_data="custom_14")
    )

    bot.send_message(message.chat.id, "Выберите параметр для триггера:", reply_markup=markup)


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
    text = ""

    data = fetch_sensor_data()
    if "error" in data:

        text = (
            "*Текущие показания датчиков:*\n\n"
            f"🌡 Температура: 20°C\n"
            f"💧 Влажность воздуха: 80 %\n"
            f"🌱 Влажность почвы: 90 %\n"
            f"🚰 Вода в резервуаре: 15 %"
        )

        #bot.reply_to(message, f"❌ {data['error']}")

    else:
        text = (
            "*Текущие показания датчиков:*\n\n"
            f"🌡 Температура: {data.get('temperature', '?')}°C\n"
            f"💧 Влажность воздуха: {data.get('humidity', '?')}%\n"
            f"🌱 Влажность почвы: {data.get('soil_moisture', '?')}%\n"
            f"🚰 Вода в резервуаре: {data.get('soil', '?')}%"
        )
        #bot.send_message(message.chat.id, text)

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

    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

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

# Запуск бота
if __name__ == "__main__":
    load_states()
    print(user_states)
    bot.polling(none_stop=True)

