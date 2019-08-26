import json
import telebot
import datetime
from markups import get_category_markups, get_yes_no_markups, continue_markups
from questionary import QUESTIONS, INIT_QUESTION, change_current_question, check_end, check_conditions


telebot.apihelper.proxy = {'https': 'https://89.238.190.164:3128'}

FILE_WITH_TOKEN = 'token.json'


def load_token(file):
    with open(file, 'r') as fh:
        entry = json.load(fh)
        return entry['token']


token = load_token(FILE_WITH_TOKEN)
bot = telebot.TeleBot(token)

next_question = INIT_QUESTION
category = None
sale_date = None


@bot.message_handler(content_types=['text'])
def initial_block(message):
    if message.text == '/help':
        bot.send_message(message.from_user.id, 'Для регистрации товара введите /reg')
    elif message.text == '/reg':
        bot.register_next_step_handler(message, get_fio)
        bot.send_message(message.from_user.id, 'Для регистрации продукта заполните необходимые поля:\nВведите ваше ФИО:')
        # bot.register_next_step_handler(message, get_category)
    else:
        bot.send_message(message.from_user.id, 'Для регистрации товара введите /reg\nВведите /help')


@bot.message_handler(content_types=['text'])
def get_fio(message):
    FIO = message.text
    bot.register_next_step_handler(message, get_address)
    bot.send_message(message.from_user.id, f'Ваше ФИО: {FIO}\nВведите адрес регистрации:')


@bot.message_handler(content_types=['text'])
def get_address(message):
    address = message.text
    bot.register_next_step_handler(message, get_sale_date)
    bot.send_message(message.from_user.id, f'Ваш адрес: {address}\nВведите дату покупки(в формате дд.мм.гггг):')


def validate_date(date_text):
    try:
        datetime.datetime.strptime(date_text, '%d.%m.%Y')
        return True
    except ValueError:
        return False


@bot.message_handler(content_types=['text'])
def get_sale_date(message):
    global sale_date
    sale_date = message.text
    if validate_date(sale_date):
        bot.register_next_step_handler(message, get_order_id)
        bot.send_message(message.from_user.id, f'Дата покупки: {sale_date}\nВведите номер заказа:')
    else:
        bot.register_next_step_handler(message, get_sale_date)
        bot.send_message(message.from_user.id, f'Вы ввели: {sale_date}\nДата не соответствует формату дд.мм.гггг\n'
        f'Введите дату ещё раз:\n')


@bot.message_handler(content_types=['text'])
def get_order_id(message):
    order_id = message.text
    bot.register_next_step_handler(message, get_photo)
    bot.send_message(message.from_user.id, f'Номер заказа: {order_id}\nЗагрузите фото товара:')


@bot.message_handler(content_types=['photo'])
def get_photo(message):
    try:
        photo_id = message.photo[-1].file_id
        photo = bot.get_file(photo_id)
        file_link = f'https://api.telegram.org/file/bot{token}/{photo.file_path}'
        bot.send_message(message.from_user.id, file_link)
        bot.send_message(message.from_user.id, f'Вы загрузили фотографию!\nВыберите категорию товара:', reply_markup=get_category_markups())
        bot.register_next_step_handler(message, get_category)
    except TypeError:
        bot.register_next_step_handler(message, get_photo)
        bot.send_message(message.from_user.id, f'Фотография не была загружена\nПопробуйте ещё раз.'
        f'Введите дату ещё раз:\n')


@bot.message_handler(content_types=['text'])
def get_category(message):
    global category
    category = message.text
    bot.send_message(message.from_user.id, f'Выбрана категория товара: {category}')
    bot.register_next_step_handler(message, get_questions)
    bot.send_message(message.from_user.id, QUESTIONS[next_question], reply_markup=get_yes_no_markups())


@bot.message_handler(content_types=['text'])
def get_questions(message):
    global next_question
    try:
        next_question = change_current_question(message.text, next_question)
        next_question = check_conditions(next_question, category, sale_date)
        bot.send_message(message.from_user.id, QUESTIONS[next_question], reply_markup=get_yes_no_markups())

        next_question = check_end(next_question)
        bot.register_next_step_handler(message, get_questions)
    except Exception:
        print('Опрос закончен')
        next_question = 1
        bot.send_message(message.from_user.id, 'Спасибо!', reply_markup=continue_markups())
        bot.register_next_step_handler(message, initial_block)


bot.polling(none_stop=True, interval=0)
