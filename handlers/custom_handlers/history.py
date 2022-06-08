from loader import bot
import re
from database.models import HistoryUsers


def data_base_request(user_id: int) -> list:
    """
    Запрос к базе данных
    :param user_id: Айди юзера для поиска
    :return: Список результатов по айди
    """
    return HistoryUsers.select().where(HistoryUsers.id_user == user_id)


@bot.message_handler(commands=['history'])
def history_message(message):
    for row in data_base_request(message.from_user.id):
        text = row.result_command
        hotels_result = re.sub(r'_', '\n', text)
        bot.send_message(
            message.chat.id,
            '🌇Город: {city}\n✍Команда: {com}\n📆Дата:'
            ' {date}\n🔍Результат:\n{res}'.format(
                city=row.chosen_city, com=row.command_choice, date=row.date, res=hotels_result
            ), disable_web_page_preview=True
        )
