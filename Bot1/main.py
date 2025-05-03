'''

import telebot
from telebot import types

bot = telebot.TeleBot('7634133767:AAF_vQNs8f-eu3Ec6aYVlG7ndkXKyluYoI4')

watering = False  # полив: False = выключен
light = False  # свет: False = выключен

temperature = 30
humidity = 80
illumination = 50
water_level = 60


@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}!')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Настройки системы', callback_data='settings'))
    markup.add(types.InlineKeyboardButton('Показания датчиков', callback_data='sensors'))
    markup.add(types.InlineKeyboardButton('Настройки уведомлений', callback_data='notifications'))
    bot.send_message(message.chat.id, 'Выберите пункт меню:', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global watering, light  # Объявляем глобальные переменные для изменения их значений

    if callback.data == 'settings':
        bot.send_message(callback.message.chat.id, '<em>настройки</em>', parse_mode='html')

    elif callback.data == 'sensors':
        sensor_data = (
            f"*Текущие показания датчиков:*\n\n"
            f"🌡️ Температура: *{temperature}°C*\n\n"
            f"💧 Влажность: *{humidity}%*\n\n"
            f"💡 Освещение: *{illumination} лк*\n\n"
            f"🚰 Уровень воды: *{water_level}%*\n\n"
            f"                      "
        )
        # создаём кнопку "изменить"
        sensor_markup = types.InlineKeyboardMarkup()

        btn1 = types.InlineKeyboardButton("💦 включить полив прямо сейчас", callback_data='watering_on')
        btn2 = types.InlineKeyboardButton("💡️ включить свет прямо сейчас", callback_data='light_on')
        btn3 = types.InlineKeyboardButton("💦 выключить полив прямо сейчас", callback_data='watering_off')
        btn4 = types.InlineKeyboardButton("💡️ выключить свет прямо сейчас", callback_data='light_off')

        sensor_markup.add(btn3 if watering else btn1)  # проверка флагов включенности полива и света
        sensor_markup.add(
            btn4 if light else btn2)  # если свет включен, то показывается кнопка выключить. аналогично с водой

        bot.send_message(callback.message.chat.id, sensor_data, parse_mode='Markdown', reply_markup=sensor_markup)

    elif callback.data == 'notifications':
        bot.send_message(callback.message.chat.id, '<em>уведомления</em>', parse_mode='html')

    elif callback.data == 'edit':
        bot.send_message(callback.message.chat.id, '🔧 Режим изменения параметров (здесь будет логика редактирования)',
                         parse_mode='Markdown')

    # Обработчики для кнопок управления
    elif callback.data == 'watering_on':
        watering = True
        bot.answer_callback_query(callback.id, "Полив включен! 💦")
        update_sensors_message(callback.message)

    elif callback.data == 'watering_off':
        watering = False
        bot.answer_callback_query(callback.id, "Полив выключен! 🚱")
        update_sensors_message(callback.message)

    elif callback.data == 'light_on':
        light = True
        bot.answer_callback_query(callback.id, "Свет включен! 💡")
        update_sensors_message(callback.message)

    elif callback.data == 'light_off':
        light = False
        bot.answer_callback_query(callback.id, "Свет выключен! 🌑")
        update_sensors_message(callback.message)


def update_sensors_message(message):
    """Функция для обновления сообщения с показаниями датчиков"""
    sensor_data = (
        f"*Текущие показания датчиков:*\n\n"
        f"🌡️ Температура: *{temperature}°C*\n\n"
        f"💧 Влажность: *{humidity}%*\n\n"
        f"💡 Освещение: *{illumination} лк*\n\n"
        f"🚰 Уровень воды: *{water_level}%*\n\n"
        f"                      "
    )

    sensor_markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("💦 включить полив прямо сейчас", callback_data='watering_on')
    btn2 = types.InlineKeyboardButton("💡️ включить свет прямо сейчас", callback_data='light_on')
    btn3 = types.InlineKeyboardButton("💦 выключить полив прямо сейчас", callback_data='watering_off')
    btn4 = types.InlineKeyboardButton("💡️ выключить свет прямо сейчас", callback_data='light_off')

    sensor_markup.add(btn3 if watering else btn1)
    sensor_markup.add(btn4 if light else btn2)

    bot.send_message(chat_id=message.chat.id,
                          text=sensor_data,
                          parse_mode='Markdown',
                          reply_markup=sensor_markup)


bot.polling(none_stop=True)

'''

import telebot
from telebot import types
import json
import os

bot = telebot.TeleBot('7634133767:AAF_vQNs8f-eu3Ec6aYVlG7ndkXKyluYoI4')  # токен бота

temperature = 30
humidity = 80
illumination = 50
water_level = 60

STATE_FILE = "state.json"

# Загружаем состояния из файла или создаём пустой словарь
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        user_states = json.load(f)
else:
    user_states = {}

def save_states():
    with open(STATE_FILE, "w") as f:
        json.dump(user_states, f)

@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.chat.id)

    # Инициализируем состояние для нового пользователя
    if user_id not in user_states:
        user_states[user_id] = {"light": False, "watering": False}
        save_states()

    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}!')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Настройки системы', callback_data='settings'))
    markup.add(types.InlineKeyboardButton('Показания датчиков', callback_data='sensors'))
    markup.add(types.InlineKeyboardButton('Настройки уведомлений', callback_data='notifications'))
    bot.send_message(message.chat.id, 'Выберите пункт меню:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = str(call.message.chat.id)

    if call.data == 'settings':
        #bot.send_message(call.message.chat.id, '<em>настройки</em>', parse_mode='html')
        send_settings(call.message)
    elif call.data == 'sensors':
        #bot.send_message(call.message.chat.id, '<em>датчики</em>', parse_mode='html')
        send_controls(call.message)
    elif call.data == 'notifications':
        bot.send_message(call.message.chat.id, '<em>уведомления</em>', parse_mode='html')

    if user_id not in user_states:
        user_states[user_id] = {"light": False, "watering": False}

    if call.data == 'light_on':
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
        update_controls_inline_keyboard(call)  # Только для полива
    elif call.data == 'watering_off':
        user_states[user_id]["watering"] = False
        bot.answer_callback_query(call.id, "Полив выключен 🚱")
        update_controls_inline_keyboard(call)  # Только для полива

    save_states()

def send_settings(message):
    bot.send_message(message.chat.id, '<em>датчики</em>', parse_mode='html')

def send_controls(message):
    user_id = str(message.chat.id)
    state = user_states.get(user_id, {"light": False, "watering": False})

    sensor_data = (
        f"*Текущие показания датчиков:*\n\n"
        f"🌡️ Температура: *{temperature}°C*\n\n"
        f"💧 Влажность: *{humidity}%*\n\n"
        f"💡 Освещение: *{illumination} лк*\n\n"
        f"🚰 Уровень воды: *{water_level}%*\n\n"
        f"                      "
    )

    markup = types.InlineKeyboardMarkup()

    # Кнопки света
    if state["light"]:
        markup.add(types.InlineKeyboardButton("🔌 Выключить свет", callback_data="light_off"))
    else:
        markup.add(types.InlineKeyboardButton("💡 Включить свет", callback_data="light_on"))

    # Кнопки полива
    if state["watering"]:
        markup.add(types.InlineKeyboardButton("🚫 Выключить полив", callback_data="watering_off"))
    else:
        markup.add(types.InlineKeyboardButton("💧 Включить полив", callback_data="watering_on"))

    bot.send_message(message.chat.id, sensor_data, parse_mode='Markdown', reply_markup=markup)

def update_controls_inline_keyboard(call):
    user_id = str(call.message.chat.id)
    state = user_states.get(user_id, {"light": False, "watering": False})

    markup = types.InlineKeyboardMarkup()

    # Кнопки света
    if state["light"]:
        markup.add(types.InlineKeyboardButton("🔌 Выключить свет", callback_data="light_off"))
    else:
        markup.add(types.InlineKeyboardButton("💡 Включить свет", callback_data="light_on"))

    # Кнопки полива
    if state["watering"]:
        markup.add(types.InlineKeyboardButton("🚫 Выключить полив", callback_data="watering_off"))
    else:
        markup.add(types.InlineKeyboardButton("💧 Включить полив", callback_data="watering_on"))

    bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=markup)

bot.polling(none_stop=True)
