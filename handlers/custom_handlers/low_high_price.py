from loader import bot
from states.low_high_price_states import UserChoiceState
from rapid_api import \
    city_founding, create_hotel_message
from keyboards.inline.city_photo_markup \
    import city_markup, photo_markup, nums_keyboard
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date
from loguru import logger


@bot.message_handler(commands=['low_price', 'high_price', 'bestdeal'])
@logger.catch
def start(message):
    bot.set_state(
        message.from_user.id, UserChoiceState.command, message.chat.id
    )
    with bot.retrieve_data(message.from_user.id, message.chat.id) as bot_data:
        bot_data['command'] = message.text[1:]
    bot.set_state(
        message.from_user.id, UserChoiceState.chosen_city, message.chat.id
    )
    bot.send_message(message.chat.id, '🌎В какой город планируем ехать?')
    bot.register_next_step_handler(message, get_city)


@bot.message_handler(state=UserChoiceState.chosen_city)
@logger.catch
def get_city(message):
    cities_list = city_founding(message.text)
    bot.delete_message(message.chat.id, message.message_id - 1)

    if cities_list is not None:
        bot.send_message(
            message.from_user.id,
            '✍Уточните, пожалуйста какую часть города вы имеете ввиду:',
            reply_markup=city_markup(cities_list))
        bot.set_state(
            message.from_user.id, UserChoiceState.city_neighborhood_id, message.chat.id
        )
        with bot.retrieve_data(message.from_user.id, message.chat.id) as bot_data:
            bot_data['city'] = message.text
    else:
        bot.send_message(
            message.from_user.id,
            'Извините(( Не могу найти такой город!🥺'
            'Пожалуйста проверьте правильность написания города.'
        )


@bot.message_handler(state=UserChoiceState.city_neighborhood_id)
@bot.callback_query_handler(func=lambda call: call.data.isdigit())
@logger.catch
def hotels(call):
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as bot_data:
        bot_data['city_neighborhood_id'] = call.data

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    bot.delete_message(call.message.chat.id, call.message.message_id)

    calendar, step = DetailedTelegramCalendar(calendar_id='in',
                                              min_date=date.today(),
                                              max_date=date(2024, 3, 31)).build()

    ru_steps = {'y': 'год', 'm': 'месяц', 'd': 'день'}
    bot.send_message(
        call.message.chat.id, f'📆Выберите дату заезда: '
                              f'\n{ru_steps[step]}', reply_markup=calendar
    )


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id='in'))
@logger.catch
def call_back_check_in(call):
    result, key, step = DetailedTelegramCalendar(
        calendar_id='in',
        locale='ru',
        min_date=date.today(),
        max_date=date(2024, 3, 31)
    ).process(call.data)

    ru_steps = {'y': 'год', 'm': 'месяц', 'd': 'день'}

    if not result and key:

        bot.edit_message_text(f"Выберите: {ru_steps[step]}",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"📆Дата заезда: {result}",
                              call.message.chat.id,
                              call.message.message_id)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as bot_data:
            bot_data['check_in'] = result

        calendar, step = DetailedTelegramCalendar(
            calendar_id='out',
            min_date=date.today(),
            max_date=date(2024, 3, 31)
        ).build()

        bot.send_message(
            call.message.chat.id,
            f'📆Выберите дату выезда: \n{ru_steps[step]}', reply_markup=calendar
        )


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id='out'))
@logger.catch
def call_back_check_out(call):
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        result, key, step = DetailedTelegramCalendar(
            calendar_id='out',
            locale='ru',
            min_date=data['check_in'],
            max_date=date(2024, 3, 31)).process(call_data=call.data)
    if not result and key:
        ru_steps = {'y': 'год', 'm': 'месяц', 'd': 'день'}
        bot.edit_message_text(f"Выберите {ru_steps[step]}",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"📆Дата выезда: {result}",
                              call.message.chat.id,
                              call.message.message_id)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as bot_data:
            bot_data['check_out'] = result

            if data['command'] == 'bestdeal':
                bot.send_message(
                    call.message.chat.id,
                    '↙Укажите минимальную стоимость отеля за ночь:'
                )
                bot.set_state(
                    call.from_user.id, UserChoiceState.min_price, call.message.chat.id
                )
            else:
                bot.send_message(
                    call.message.chat.id,
                    '😁Сколько отелей показать?(Не больше 10)',
                    reply_markup=nums_keyboard('hotels')
                )
                bot.set_state(
                    call.from_user.id,
                    UserChoiceState.hotel_quantity,
                    call.message.chat.id
                )


@bot.message_handler(state=UserChoiceState.hotel_quantity)
@bot.callback_query_handler(func=lambda call: call.data.endswith('h'))
@logger.catch
def get_hotel_quantity(call):
    bot.set_state(
        call.from_user.id,
        UserChoiceState.apply_photo,
        call.message.chat.id
    )
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as bot_data:
        bot_data['hotel_quantity'] = int(call.data.replace('h', '')) + 1

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    bot.delete_message(call.message.chat.id, call.message.message_id)

    bot.send_message(
        call.message.chat.id,
        text="📷Показать фотографии отелей?",
        reply_markup=photo_markup()
    )


@bot.message_handler(state=UserChoiceState.apply_photo)
@bot.callback_query_handler(
    func=lambda call: call.data.startswith('н') or call.data.startswith('д')
)
@logger.catch
def ask_about_photo(call):
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as bot_data:
        if call.data == 'нет':
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
            days = (bot_data['check_out'] - bot_data['check_in']).days
            create_hotel_message(bot_data=bot_data,
                                 days_count=days,
                                 user_id=call.from_user.id)

            bot.delete_state(call.from_user.id)
            bot.reset_data(call.from_user.id)

        elif call.data == 'да':
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(
                call.message.chat.id,
                '🖼Сколько фотографий показать?(Не больше 10)',
                reply_markup=nums_keyboard('photos'))
            bot.set_state(
                call.from_user.id,
                UserChoiceState.photo_quantity,
                call.message.chat.id
            )


@bot.message_handler(state=UserChoiceState.photo_quantity)
@bot.callback_query_handler(func=lambda call: call.data.endswith('p'))
@logger.catch
def get_photo_quantity(call):
    bot.set_state(
        call.from_user.id, UserChoiceState.apply_photo, call.message.chat.id
    )
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as bot_data:
        bot_data['photo_quantity'] = int(call.data.replace('p', ''))

        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        days = (bot_data['check_out'] - bot_data['check_in']).days
        create_hotel_message(bot_data=bot_data,
                             days_count=days,
                             user_id=call.from_user.id,
                             photo_quantity=bot_data['photo_quantity'])
    bot.delete_state(call.from_user.id)
    bot.reset_data(call.from_user.id)
