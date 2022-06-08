from telebot.handler_backends import State, StatesGroup


class UserChoiceState(StatesGroup):
    command = State()
    chosen_city = State()
    city_neighborhood_id = State()
    check_in = State()
    check_out = State()
    min_price = State()
    max_price = State()
    center_min = State()
    center_max = State()
    hotel_quantity = State()
    apply_photo = State()
    photo_quantity = State()
