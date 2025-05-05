import telebot
from telebot import types
import json
import os

#bot = telebot.TeleBot('7634133767:AAF_vQNs8f-eu3Ec6aYVlG7ndkXKyluYoI4') #тестовый бот
bot = telebot.TeleBot('7789381064:AAFFdBdqwiNBJrq16UExKKLiprnDpCpRACo') #чистовик

STATE_FILE = "state.json"

temperature = 30
humidity = 80
illumination = 50
water_level = 60

# Состояние ввода чисел пользователями
user_input_steps = {}

# Загружаем состояния из файла или создаём пустой словарь
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        user_states = json.load(f)
else:
    user_states = {}

def save_states():
    with open(STATE_FILE, "w") as f:
        json.dump(user_states, f, indent=4)

@bot.message_handler(commands=["settings"])
def settings_command(message):
   user_id = str(message.chat.id)
   if user_id not in user_states:
       user_states[user_id] = {"light": False, "watering": False, "actions": {}, "notifications": {}}
       save_states()
   send_settings(message)  

@bot.message_handler(commands=["sensors"])
def sensors_command(message):
   user_id = str(message.chat.id)
   if user_id not in user_states:
       user_states[user_id] = {"light": False, "watering": False, "actions": {}, "notifications": {}}
       save_states()
   send_controls(message)  

@bot.message_handler(commands=["notifications"])
def notifications_command(message):
   user_id = str(message.chat.id)
   if user_id not in user_states:
       user_states[user_id] = {"light": False, "watering": False, "actions": {}, "notifications": {}}
       save_states()
   send_notifications(message)  


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = str(call.message.chat.id)

    if user_id not in user_states:
        user_states[user_id] = {"light": False, "watering": False, "actions": {}}

    if call.data == 'settings':
        send_settings(call.message)
    elif call.data == 'sensors':
        send_controls(call.message)
    elif call.data == 'notifications':
        send_notifications(call.message)
        #bot.send_message(call.message.chat.id, '<em>уведомления</em>', parse_mode='html')
    elif call.data == 'light_on':
        user_states[user_id]["light"] = True
        bot.answer_callback_query(call.id, "Свет включен 💡")
        update_controls_inline_keyboard(call)
    elif call.data == 'light_off':
        user_states[user_id]["light"] = False
        bot.answer_callback_query(call.id, "Свет выключен 🌑")
        update_controls_inline_keyboard(call)
    elif call.data == 'watering_on':
        user_states[user_id]["watering"] = True
        bot.answer_callback_query(call.id, "Полив включен 💦")
        update_controls_inline_keyboard(call)
    elif call.data == 'watering_off':
        user_states[user_id]["watering"] = False
        bot.answer_callback_query(call.id, "Полив выключен 🚱")
        update_controls_inline_keyboard(call)
    elif call.data == 'custom_button_1':
        user_input_steps[user_id] = {"step": 1}
        bot.send_message(call.message.chat.id, "Введите час (целое число):")
    elif call.data == 'custom_button_2':
        user_input_steps[user_id] = {"step": 3}
        bot.send_message(call.message.chat.id, "Введите час (целое число):")
    elif call.data == 'custom_button_3':
        user_input_steps[user_id] = {"step": 5}
        bot.send_message(call.message.chat.id, "Введите час (целое число):")
    elif call.data == 'custom_button_4':
        user_input_steps[user_id] = {"step": 7}
        bot.send_message(call.message.chat.id, "Введите номер действия:")
    elif call.data == 'custom_1': #добавить триггер
        add_notifications_buttons(call.message)
    elif call.data == 'custom_2': #удалить существующий триггер
        user_input_steps[user_id] = {"step": 30}
        bot.send_message(call.message.chat.id, "Введите номер триггера:")
    elif call.data == 'custom_11':
        user_input_steps[user_id] = {"step": 8}
        bot.send_message(call.message.chat.id, "Введите значение параметра 'влажность' при котором Вы хотите получать уведомление:")
    elif call.data == 'custom_12':
        user_input_steps[user_id] = {"step": 9}
        bot.send_message(call.message.chat.id, "Введите значение параметра 'температура' при котором Вы хотите получать уведомление:")
    elif call.data == 'custom_13':
        user_input_steps[user_id] = {"step": 10}
        bot.send_message(call.message.chat.id, "Введите значение параметра 'освещенность' при котором Вы хотите получать уведомление:")
    elif call.data == 'custom_14':
        user_input_steps[user_id] = {"step": 11}
        bot.send_message(call.message.chat.id, "Введите значение параметра 'уровень воды' при котором Вы хотите получать уведомление:")

    save_states()

# Обработчик сообщений, который активируется только для пользователей, находящихся в процессе ввода данных
@bot.message_handler(func=lambda message: str(message.chat.id) in user_input_steps)
def handle_user_input(message):
    user_delete_steps = {}  # {"user_id": {"step": 1}}

    # Получаем ID чата пользователя
    user_id = str(message.chat.id)
    # Извлекаем информацию о текущем шаге ввода для этого пользователя
    step_info = user_input_steps[user_id]

    # Шаг 1: обработка ввода часов
    if step_info["step"] == 1:  # добавляем часы в файл
        try:
            # Пытаемся преобразовать текст сообщения в число (час)
            hour = int(message.text)
            # Проверяем, что час в допустимом диапазоне (0-23)
            if not (0 <= hour <= 23):
                raise ValueError
            # Сохраняем введенный час и переходим к следующему шагу
            step_info["hour"] = hour
            step_info["step"] = 2
            # Запрашиваем у пользователя ввод минут
            bot.send_message(message.chat.id, "Теперь введите минуту (целое число):")
        except ValueError:
            # В случае ошибки просим ввести корректное значение
            bot.send_message(message.chat.id, "Пожалуйста, введите корректный час (от 0 до 23).")
    # Шаг 2: обработка ввода минут
    elif step_info["step"] == 2:  # добавляем минуты в файл
        try:
            # Пытаемся преобразовать текст сообщения в число (минуты)
            minute = int(message.text)
            # Проверяем, что минуты в допустимом диапазоне (0-59)
            if not (0 <= minute <= 59):
                raise ValueError
            # Получаем сохраненные ранее часы
            hour = step_info["hour"]
            # Получаем или создаем запись пользователя в user_states
            user_data = user_states.setdefault(user_id, {"light": False, "watering": False, "actions": {}})
            # Получаем или создаем словарь действий пользователя
            actions = user_data.setdefault("actions", {})
            # Генерируем новый ID для действия (максимальный существующий + 1)
            next_id = str(max([int(k) for k in actions.keys()] + [0]) + 1)
            # Создаем новое действие полива с указанными параметрами
            actions[next_id] = {
                "type": "watering",  # Тип действия - полив
                "boolean": "on",  # Состояние - включено
                "hour": hour,  # Час срабатывания
                "minute": minute  # Минута срабатывания
            }
            # Сохраняем изменения в файл
            save_states()
            # Отправляем пользователю подтверждение с ID действия
            bot.send_message(message.chat.id, f"Сохранено как действие #{next_id}.")
            # Удаляем пользователя из списка находящихся в процессе ввода
            user_input_steps.pop(user_id)
        except ValueError:
            # В случае ошибки просим ввести корректное значение
            bot.send_message(message.chat.id, "Пожалуйста, введите корректную минуту (от 0 до 59).")
    elif step_info["step"] == 3:
        try:
            # Пытаемся преобразовать текст сообщения в число (час)
            hour = int(message.text)
            # Проверяем, что час в допустимом диапазоне (0-23)
            if not (0 <= hour <= 23):
                raise ValueError
            # Сохраняем введенный час и переходим к следующему шагу
            step_info["hour"] = hour
            step_info["step"] = 4
            # Запрашиваем у пользователя ввод минут
            bot.send_message(message.chat.id, "Теперь введите минуту (целое число):")
        except ValueError:
            # В случае ошибки просим ввести корректное значение
            bot.send_message(message.chat.id, "Пожалуйста, введите корректный час (от 0 до 23).")
    elif step_info["step"] == 4:
        try:
            # Пытаемся преобразовать текст сообщения в число (минуты)
            minute = int(message.text)
            # Проверяем, что минуты в допустимом диапазоне (0-59)
            if not (0 <= minute <= 59):
                raise ValueError
            # Получаем сохраненные ранее часы
            hour = step_info["hour"]
            # Получаем или создаем запись пользователя в user_states
            user_data = user_states.setdefault(user_id, {"light": False, "watering": False, "actions": {}})
            # Получаем или создаем словарь действий пользователя
            actions = user_data.setdefault("actions", {})
            # Генерируем новый ID для действия (максимальный существующий + 1)
            next_id = str(max([int(k) for k in actions.keys()] + [0]) + 1)
            # Создаем новое действие полива с указанными параметрами
            actions[next_id] = {
                "type": "light",  # Тип действия - полив
                "boolean": "on",  # Состояние - включено
                "hour": hour,  # Час срабатывания
                "minute": minute  # Минута срабатывания
            }
            # Сохраняем изменения в файл
            save_states()
            # Отправляем пользователю подтверждение с ID действия
            bot.send_message(message.chat.id, f"Сохранено как действие #{next_id}.")
            # Удаляем пользователя из списка находящихся в процессе ввода
            user_input_steps.pop(user_id)
        except ValueError:
            # В случае ошибки просим ввести корректное значение
            bot.send_message(message.chat.id, "Пожалуйста, введите корректную минуту (от 0 до 59).")
    elif step_info["step"] == 5:  # добавляем часы в файл
        try:
            # Пытаемся преобразовать текст сообщения в число (час)
            hour = int(message.text)
            # Проверяем, что час в допустимом диапазоне (0-23)
            if not (0 <= hour <= 23):
                raise ValueError
            # Сохраняем введенный час и переходим к следующему шагу
            step_info["hour"] = hour
            step_info["step"] = 6
            # Запрашиваем у пользователя ввод минут
            bot.send_message(message.chat.id, "Теперь введите минуту (целое число):")
        except ValueError:
            # В случае ошибки просим ввести корректное значение
            bot.send_message(message.chat.id, "Пожалуйста, введите корректный час (от 0 до 23).")
    elif step_info["step"] == 6:
        try:
            # Пытаемся преобразовать текст сообщения в число (минуты)
            minute = int(message.text)
            # Проверяем, что минуты в допустимом диапазоне (0-59)
            if not (0 <= minute <= 59):
                raise ValueError
            # Получаем сохраненные ранее часы
            hour = step_info["hour"]
            # Получаем или создаем запись пользователя в user_states
            user_data = user_states.setdefault(user_id, {"light": False, "watering": False, "actions": {}})
            # Получаем или создаем словарь действий пользователя
            actions = user_data.setdefault("actions", {})
            # Генерируем новый ID для действия (максимальный существующий + 1)
            next_id = str(max([int(k) for k in actions.keys()] + [0]) + 1)
            # Создаем новое действие полива с указанными параметрами
            actions[next_id] = {
                "type": "light",  # Тип действия - полив
                "boolean": "off",  # Состояние - включено
                "hour": hour,  # Час срабатывания
                "minute": minute  # Минута срабатывания
            }
            # Сохраняем изменения в файл
            save_states()
            # Отправляем пользователю подтверждение с ID действия
            bot.send_message(message.chat.id, f"Сохранено как действие #{next_id}.")
            # Удаляем пользователя из списка находящихся в процессе ввода
            user_input_steps.pop(user_id)
        except ValueError:
            # В случае ошибки просим ввести корректное значение
            bot.send_message(message.chat.id, "Пожалуйста, введите корректную минуту (от 0 до 59).")
    elif step_info["step"] == 7:  # запрос индекса для удаления
        try:
            action_id = message.text
            # Проверяем, существует ли такое действие у пользователя
            if user_id in user_states and action_id in user_states[user_id].get("actions", {}):
                # Удаляем действие
                del user_states[user_id]["actions"][action_id]
                save_states()  # сохраняем изменения в файл
                bot.send_message(message.chat.id, f"Действие #{action_id} успешно удалено.")
                user_delete_steps.pop(user_id)  # удаляем пользователя из процесса удаления
            else:
                bot.send_message(message.chat.id, "Действие с таким ID не найдено. Пожалуйста, введите корректный ID:")
        except Exception as e:
            bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}. Пожалуйста, попробуйте еще раз.")
    elif step_info["step"] == 8:  # добавляем минуты в файл
        try:
            # Пытаемся преобразовать текст сообщения в число (минуты)
            trigger = int(message.text)
            # Проверяем, что минуты в допустимом диапазоне (0-59)
            if not (0 <= trigger <= 100):
                raise ValueError
            # Получаем сохраненные ранее часы
            #hour = step_info["hour"]
            # Получаем или создаем запись пользователя в user_states
            user_data = user_states.setdefault(user_id, {"light": False, "watering": False, "actions": {}, "notifications": {}})
            # Получаем или создаем словарь действий пользователя
            notifications = user_data.setdefault("notifications", {})
            # Генерируем новый ID для действия (максимальный существующий + 1)
            next_id = str(max([int(k) for k in notifications.keys()] + [0]) + 1)
            # Создаем новое действие полива с указанными параметрами
            notifications[next_id] = {
                "type": "humidity",  # Тип действия - полив
                "trigger": trigger,  # Состояние - включено
            }
            # Сохраняем изменения в файл
            save_states()
            # Отправляем пользователю подтверждение с ID действия
            bot.send_message(message.chat.id, f"Сохранено как действие #{next_id}.")
            # Удаляем пользователя из списка находящихся в процессе ввода
            user_input_steps.pop(user_id)
        except ValueError:
            # В случае ошибки просим ввести корректное значение
            bot.send_message(message.chat.id, "Пожалуйста, введите целое число от 0 до 100.")
    elif step_info["step"] == 9:  # добавляем минуты в файл
        try:
            # Пытаемся преобразовать текст сообщения в число (минуты)
            trigger = int(message.text)
            # Проверяем, что минуты в допустимом диапазоне (0-59)
            if not (0 <= trigger <= 100):
                raise ValueError
            # Получаем сохраненные ранее часы
            #hour = step_info["hour"]
            # Получаем или создаем запись пользователя в user_states
            user_data = user_states.setdefault(user_id, {"light": False, "watering": False, "actions": {}, "notifications": {}})
            # Получаем или создаем словарь действий пользователя
            notifications = user_data.setdefault("notifications", {})
            # Генерируем новый ID для действия (максимальный существующий + 1)
            next_id = str(max([int(k) for k in notifications.keys()] + [0]) + 1)
            # Создаем новое действие полива с указанными параметрами
            notifications[next_id] = {
                "type": "temperature",  # Тип действия - полив
                "trigger": trigger,  # Состояние - включено
            }
            # Сохраняем изменения в файл
            save_states()
            # Отправляем пользователю подтверждение с ID действия
            bot.send_message(message.chat.id, f"Сохранено как действие #{next_id}.")
            # Удаляем пользователя из списка находящихся в процессе ввода
            user_input_steps.pop(user_id)
        except ValueError:
            # В случае ошибки просим ввести корректное значение
            bot.send_message(message.chat.id, "Пожалуйста, введите целое число от 0 до 100.")
    elif step_info["step"] == 10:  # добавляем минуты в файл
        try:
            # Пытаемся преобразовать текст сообщения в число (минуты)
            trigger = int(message.text)
            # Проверяем, что минуты в допустимом диапазоне (0-59)
            if not (0 <= trigger <= 100):
                raise ValueError
            # Получаем сохраненные ранее часы
            #hour = step_info["hour"]
            # Получаем или создаем запись пользователя в user_states
            user_data = user_states.setdefault(user_id, {"light": False, "watering": False, "actions": {}, "notifications": {}})
            # Получаем или создаем словарь действий пользователя
            notifications = user_data.setdefault("notifications", {})
            # Генерируем новый ID для действия (максимальный существующий + 1)
            next_id = str(max([int(k) for k in notifications.keys()] + [0]) + 1)
            # Создаем новое действие полива с указанными параметрами
            notifications[next_id] = {
                "type": "illumination",  # Тип действия - полив
                "trigger": trigger,  # Состояние - включено
            }
            # Сохраняем изменения в файл
            save_states()
            # Отправляем пользователю подтверждение с ID действия
            bot.send_message(message.chat.id, f"Сохранено как действие #{next_id}.")
            # Удаляем пользователя из списка находящихся в процессе ввода
            user_input_steps.pop(user_id)
        except ValueError:
            # В случае ошибки просим ввести корректное значение
            bot.send_message(message.chat.id, "Пожалуйста, введите целое число от 0 до 100.")
    elif step_info["step"] == 11:  # добавляем минуты в файл
        try:
            # Пытаемся преобразовать текст сообщения в число (минуты)
            trigger = int(message.text)
            # Проверяем, что минуты в допустимом диапазоне (0-59)
            if not (0 <= trigger <= 100):
                raise ValueError
            # Получаем сохраненные ранее часы
            #hour = step_info["hour"]
            # Получаем или создаем запись пользователя в user_states
            user_data = user_states.setdefault(user_id, {"light": False, "watering": False, "actions": {}, "notifications": {}})
            # Получаем или создаем словарь действий пользователя
            notifications = user_data.setdefault("notifications", {})
            # Генерируем новый ID для действия (максимальный существующий + 1)
            next_id = str(max([int(k) for k in notifications.keys()] + [0]) + 1)
            # Создаем новое действие полива с указанными параметрами
            notifications[next_id] = {
                "type": "water_level",  # Тип действия - полив
                "trigger": trigger,  # Состояние - включено
            }
            # Сохраняем изменения в файл
            save_states()
            # Отправляем пользователю подтверждение с ID действия
            bot.send_message(message.chat.id, f"Сохранено как действие #{next_id}.")
            # Удаляем пользователя из списка находящихся в процессе ввода
            user_input_steps.pop(user_id)
        except ValueError:
            # В случае ошибки просим ввести корректное значение
            bot.send_message(message.chat.id, "Пожалуйста, введите целое число от 0 до 100.")
    elif step_info["step"] == 30:  # запрос индекса для удаления
        try:
            action_id = message.text
            # Проверяем, существует ли такое действие у пользователя
            if user_id in user_states and action_id in user_states[user_id].get("notifications", {}):
                # Удаляем действие
                del user_states[user_id]["notifications"][action_id]
                save_states()  # сохраняем изменения в файл
                bot.send_message(message.chat.id, f"Действие #{action_id} успешно удалено.")
                user_delete_steps.pop(user_id)  # удаляем пользователя из процесса удаления
            else:
                bot.send_message(message.chat.id, "Триггер с таким ID не найдено. Пожалуйста, введите корректный ID:")
        except Exception as e:
            bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}. Пожалуйста, попробуйте еще раз.")

def send_notifications(message):
    user_id = str(message.chat.id)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("добавить триггер уведомлений", callback_data="custom_1"))
    markup.add(types.InlineKeyboardButton("удалить триггер", callback_data="custom_2"))

    user_data = user_states.get(user_id, {})
    notifications = user_data.get("notifications", {})
    notifications_text = "*Уведомления:*\n\n"
    for note_id, note in notifications.items():
        type_emoji = {
            "humidity": "💧 Влажность",
            "temperature": "🌡 Температура",
            "illumination": "🔆 Освещённость",
            "water_level": "🚰 Уровень воды"
        }
        note_type = type_emoji.get(note["type"], note["type"])
        trigger = note["trigger"]
        notifications_text += f"• #{note_id} — {note_type}, триггер: {trigger}\n\n"

    bot.send_message(message.chat.id, notifications_text, parse_mode='Markdown', reply_markup=markup)

def add_notifications_buttons(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("влажность", callback_data="custom_11"))
    markup.add(types.InlineKeyboardButton("температура", callback_data="custom_12"))
    markup.add(types.InlineKeyboardButton("освещенность", callback_data="custom_13"))
    markup.add(types.InlineKeyboardButton("уровень воды", callback_data="custom_14"))

    bot.send_message(message.chat.id, "выберите параметр для триггера:", parse_mode='Markdown', reply_markup=markup)

def send_settings(message):
    user_id = str(message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💧 Добавить включение полива", callback_data="custom_button_1"))
    markup.add(types.InlineKeyboardButton("💡 Добавить включение освещения", callback_data="custom_button_2"))
    markup.add(types.InlineKeyboardButton("🔌 Добавить выключение освещения", callback_data="custom_button_3"))
    markup.add(types.InlineKeyboardButton("🚫 Удалить действие", callback_data="custom_button_4"))

    # Формируем текст со списком действий
    user_data = user_states.get(user_id, {})
    actions = user_data.get("actions", {})
    if actions:
        actions_text = "*Ваши сохранённые действия:*\n\n"
        for action_id, action in actions.items():
            action_type = "💧 Полив" if action["type"] == "watering" else "💡 Свет"
            state_text = "вкл" if action["boolean"] == "on" else "выкл"
            actions_text += f"• #{action_id} — {action_type}, {state_text} в {action['hour']:02d}:{action['minute']:02d}\n\n"
    else:
        actions_text = "_У вас пока нет сохранённых действий._"

    bot.send_message(message.chat.id, actions_text, parse_mode='Markdown')
    bot.send_message(message.chat.id, "настройки системы", parse_mode='Markdown', reply_markup=markup)

def send_controls(message):
    user_id = str(message.chat.id)
    state = user_states.get(user_id, {"light": False, "watering": False})

    sensor_data = (
        f"*Текущие показания датчиков:*\n\n"
        f"🌡️ Температура: *{temperature}°C*\n\n"
        f"💧 Влажность: *{humidity}%*\n\n"
        f"💡 Освещение: *{illumination} лк*\n\n"
        f"🚰 Уровень воды: *{water_level}%*"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💡 Включить свет" if not state["light"] else "🔌 Выключить свет",
                                          callback_data="light_off" if state["light"] else "light_on"))
    markup.add(types.InlineKeyboardButton("💧 Включить полив" if not state["watering"] else "🚫 Выключить полив",
                                          callback_data="watering_off" if state["watering"] else "watering_on"))

    bot.send_message(message.chat.id, sensor_data, parse_mode='Markdown', reply_markup=markup)

def update_controls_inline_keyboard(call):
    user_id = str(call.message.chat.id)
    state = user_states.get(user_id, {"light": False, "watering": False})

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💡 Включить свет" if not state["light"] else "🔌 Выключить свет",
                                          callback_data="light_off" if state["light"] else "light_on"))
    markup.add(types.InlineKeyboardButton("💧 Включить полив" if not state["watering"] else "🚫 Выключить полив",
                                          callback_data="watering_off" if state["watering"] else "watering_on"))

    bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=markup)

bot.polling(none_stop=True)
