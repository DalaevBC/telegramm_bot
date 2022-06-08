import peewee

db = peewee.SqliteDatabase('database/database.db')  # Создали объект базы данных


class BaseModel(peewee.Model):

    class Meta:
        database = db


class HistoryUsers(BaseModel):
    # В классе описываем таблицу в базе данных
    id_user = peewee.IntegerField()
    chosen_city = peewee.CharField()
    date = peewee.DateField()
    command_choice = peewee.CharField()
    result_command = peewee.CharField()
