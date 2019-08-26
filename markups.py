from telebot import types


def get_category_markups():
    category_markup = types.ReplyKeyboardMarkup(row_width=1)

    clothes = types.KeyboardButton('Одежда')
    underwear = types.KeyboardButton('Бельё')
    stationery = types.KeyboardButton('Канцтовары')
    consumer_electronic = types.KeyboardButton('Бытовая электроника')
    smartphones = types.KeyboardButton('Смартфоны')
    accessories = types.KeyboardButton('Аксессуары')
    watches = types.KeyboardButton('Часы')
    jewelry = types.KeyboardButton('Ювелирные изделия')
    toys = types.KeyboardButton('Игрушки')
    car_accessories = types.KeyboardButton('Автомобильные аксессуары')
    in_car_electronics = types.KeyboardButton('Автомобильная электроника')
    perfumes = types.KeyboardButton('Парфюмерия и косметика')
    crockery = types.KeyboardButton('Посуда')
    supplies = types.KeyboardButton('Строительные материалы')
    furniture = types.KeyboardButton('Мебель')

    category_markup.add(clothes, underwear, stationery, consumer_electronic, smartphones, accessories, watches,
                        jewelry, toys, car_accessories, in_car_electronics, perfumes, crockery, supplies, furniture)

    return category_markup


def get_yes_no_markups():
    yes_no_markup = types.ReplyKeyboardMarkup(row_width=1)

    yes = types.KeyboardButton('Да')
    no = types.KeyboardButton('Нет')

    yes_no_markup.add(yes, no)
    return yes_no_markup


def continue_markups():
    continue_ = types.ReplyKeyboardMarkup(row_width=1)

    continue_b = types.KeyboardButton('Продолжить')

    continue_.add(continue_b)
    return continue_
