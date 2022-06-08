from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS
from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    bot.delete_state(message.from_user.id)
    bot.reset_data(message.from_user.id)
    bot.reply_to(message, f"Привет, {message.from_user.full_name}!\n"
                          f"С помощью меня ты сможешь найти ЛЮБОЙ отель в ЛЮБОМ городе!\nПриступим?")
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, '\n'.join(text))
