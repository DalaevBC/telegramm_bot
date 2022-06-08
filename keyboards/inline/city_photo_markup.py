from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def city_markup(cities) -> InlineKeyboardMarkup:
    """
    Функция для создания кнопок
    :param cities: Список частей города(Функция "city_founding"
    уже возвращает список словарей с нужным именем и id)
    :return: Кнопки для выбора части города
    """
    destinations = InlineKeyboardMarkup()
    for city in cities:
        destinations.add(InlineKeyboardButton(
            text=city['city_name'],
            callback_data=f'{city["destination_id"]}'))
    return destinations


def photo_markup() -> InlineKeyboardMarkup:
    """
    Функция возвращает кнопки Да и Нет
    :return: Кнопки 'Да' 'Нет'
    """
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Да', callback_data='да'))
    markup.add(InlineKeyboardButton(text='Нет', callback_data='нет'))
    return markup


def nums_keyboard(status) -> InlineKeyboardMarkup:
    """
    Функция создает кнопки для вывода отелей и фото
    :param status: str
    :return: InlineKeyboardMarkup
    """
    markup = InlineKeyboardMarkup()
    if status == 'hotels':
        for num in range(1, 11):
            if num == 1:
                markup.add(
                    InlineKeyboardButton(
                        text=str(num) + ' Отель', callback_data=str(num) + 'h'
                    )
                )
            elif 1 < num < 6:
                markup.add(
                    InlineKeyboardButton(
                        text=str(num) + ' Отеля', callback_data=str(num) + 'h'
                    )
                )
            elif 5 < num < 11:
                markup.add(
                    InlineKeyboardButton(
                        text=str(num) + ' Отелей', callback_data=str(num) + 'h'
                    )
                )
    elif status == 'photos':
        for num in range(1, 11):
            if num == 1:
                markup.add(
                    InlineKeyboardButton(
                        text=str(num) + ' Фотография', callback_data=str(num) + 'p'
                    )
                )
            elif 1 < num < 6:
                markup.add(
                    InlineKeyboardButton(
                        text=str(num) + ' Фотографии', callback_data=str(num) + 'p'
                    )
                )
            elif 5 < num < 11:
                markup.add(
                    InlineKeyboardButton(
                        text=str(num) + ' Фотографий', callback_data=str(num) + 'p'
                    )
                )
    return markup
