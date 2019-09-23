from telebot import types
from models import get_categories


def get_category_markups():
    category_markup = types.ReplyKeyboardMarkup(row_width=1)
    all_categories = get_categories()

    for one_category in all_categories:
        button = types.KeyboardButton(one_category.name)
        category_markup.add(button)

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
