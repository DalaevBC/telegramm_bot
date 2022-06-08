from loader import bot
from states.low_high_price_states import UserChoiceState
from loguru import logger
from keyboards.inline.city_photo_markup import nums_keyboard


@bot.message_handler(state=UserChoiceState.min_price)
@logger.catch
def get_min_price(message):
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as bot_data:
            bot_data['min_price'] = message.text
            bot.delete_message(message.chat.id, message.message_id - 1)
        bot.send_message(
            message.chat.id,
            '↗️Отлично! Теперь введите максимальную стоимость отеля за ночь:')
        bot.set_state(
            message.from_user.id, UserChoiceState.max_price, message.chat.id
        )
    else:
        bot.send_message(message.chat.id, 'Мне нужны сухие цифры)))))')


@bot.message_handler(state=UserChoiceState.max_price)
@logger.catch
def get_max_price(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as bot_data:
        if message.text.isdigit() and \
                int(bot_data['min_price']) < int(message.text):
            bot_data['max_price'] = message.text
            bot.delete_message(message.chat.id, message.message_id - 1)

            bot.send_message(
                message.chat.id,
                '↙️Укажите минимальное расстояние до центра города '
                'в километрах(например 0.7 или 1)'
            )
            bot.set_state(
                message.from_user.id, UserChoiceState.center_min, message.chat.id
                 )
        else:
            bot.send_message(message.chat.id, 'Мне нужны сухие цифры)))))')


@bot.message_handler(state=UserChoiceState.center_min)
@logger.catch
def get_min_distance(message):
    if message.text.find('.' or ',') or message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as bot_data:
            bot_data['center_min'] = message.text
            bot.delete_message(message.chat.id, message.message_id - 1)

        bot.send_message(
            message.chat.id,
            '↗️Укажите максимальное расстояние до центра города '
            'в километрах(например 2.5 или 5)')
        bot.set_state(
            message.from_user.id, UserChoiceState.center_max, message.chat.id
        )


@bot.message_handler(state=UserChoiceState.center_max)
@logger.catch
def get_max_distance(message):
    if message.text.find('.' or ',') or message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as bot_data:
            bot_data['center_max'] = message.text
            if float(bot_data['center_min']) < float(bot_data['center_max']):
                bot.delete_message(message.chat.id, message.message_id - 1)
                bot.send_message(
                    message.chat.id,
                    '🏠Сколько отелей показать?(Не больше 10)',
                    reply_markup=nums_keyboard('hotels')
                )
                bot.set_state(
                    message.from_user.id,
                    UserChoiceState.hotel_quantity,
                    message.chat.id
                )
    else:
        bot.send_message(
            message.chat.id, 'Пожалуйста укажите расстояние цифрами.\n'
                             'Если число дробное его необходимо разделить точкой.')
