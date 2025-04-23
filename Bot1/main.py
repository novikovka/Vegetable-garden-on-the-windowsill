import telebot
from telebot import types

bot = telebot.TeleBot('7789381064:AAFFdBdqwiNBJrq16UExKKLiprnDpCpRACo')
#markup = types.InlineKeyboardMarkup()

@bot.message_handler(commands=['start', 'Hello!', 'main', 'go'])
def main(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}')

@bot.message_handler(commands=['help'])
def main(message):
    #markup = types.InlineKeyboardMarkup()
    #markup.add(types.InlineKeyboardButton('Вывести информацию'))
    bot.send_message(message.chat.id, '<b>Help</b> <em><u>information</u></em>', parse_mode='html')

@bot.message_handler(commands=['show'])
def show(message):
    markup = types.InlineKeyboardMarkup()  # создаём новую клавиатуру каждый раз
    markup.add(types.InlineKeyboardButton('Вывести информацию', callback_data='information'))
    bot.send_message(message.chat.id, 'Нажми на кнопку ниже:', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'information':
        bot.send_message(callback.message.chat.id, '<b>Help</b> <em><u>information</u></em>', parse_mode='html')


@bot.message_handler()
def info(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}')
    elif message.text.lower() == 'id':
        bot.reply_to(message, f'ID: {message.from_user.id}')

'''
@bot.message_handler(commands=['show'])
def show(message):
    #bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}')
    markup.add(types.InlineKeyboardButton('Вывести информацию', callback_data='information'))
'''




bot.polling(none_stop=True) #чтобы бот работал всегда