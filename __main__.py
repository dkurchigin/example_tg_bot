import json
import telebot
import datetime
from markups import get_category_markups, get_yes_no_markups, continue_markups
from models import get_categories, add_new_reg_ticket, update_reg_ticket, get_next_question, get_question


telebot.apihelper.proxy = {'https': 'socks5://127.0.0.1:9150'}

FILE_WITH_TOKEN = 'token.json'
INIT_QUESTION = 1


def load_token(file):
    with open(file, 'r') as fh:
        entry = json.load(fh)
        return entry['token']


token = load_token(FILE_WITH_TOKEN)
bot = telebot.TeleBot(token)
next_question = INIT_QUESTION


class Ticket:
    def __init__(self):
        self.id = None
        self.fio = None
        self.address = None
        self.sale_date = None
        self.order_id = None
        self.photo_file = None
        self.category = None
        self.next_question = INIT_QUESTION


@bot.message_handler(content_types=['text'])
def initial_block(message):
    if message.text == '/help':
        bot.send_message(message.from_user.id, 'Для регистрации товара введите /reg')
    elif message.text == '/reg':
        new_ticket = Ticket()
        new_ticket.id = add_new_reg_ticket(message.from_user.id)

        bot.register_next_step_handler(message, get_fio, new_ticket)
        bot.send_message(message.from_user.id, 'Для регистрации продукта заполните необходимые поля:\nВведите ваше ФИО:')
    else:
        bot.send_message(message.from_user.id, 'Для регистрации товара введите /reg\nВведите /help')


@bot.message_handler(content_types=['text'])
def get_fio(message, new_ticket):
    new_ticket.fio = message.text
    update_reg_ticket(new_ticket)

    bot.register_next_step_handler(message, get_address, new_ticket)
    bot.send_message(message.from_user.id, f'Ваше ФИО: {new_ticket.fio}\nВведите адрес регистрации:')


@bot.message_handler(content_types=['text'])
def get_address(message, new_ticket):
    new_ticket.address = message.text
    update_reg_ticket(new_ticket)

    bot.register_next_step_handler(message, get_sale_date, new_ticket)
    bot.send_message(message.from_user.id, f'Ваш адрес: {new_ticket.address}\nВведите дату покупки(в формате дд.мм.гггг):')


def validate_date(date_text):
    try:
        valid_date = datetime.datetime.strptime(date_text, '%d.%m.%Y')
        return valid_date
    except ValueError:
        return False


@bot.message_handler(content_types=['text'])
def get_sale_date(message, new_ticket):
    sale_date = message.text

    valid_date = validate_date(sale_date)

    if valid_date:
        new_ticket.sale_date = valid_date
        update_reg_ticket(new_ticket)

        bot.register_next_step_handler(message, get_order_id, new_ticket)
        bot.send_message(message.from_user.id, f'Дата покупки: {sale_date}\nВведите номер заказа:')
    else:
        bot.register_next_step_handler(message, new_ticket)
        bot.send_message(message.from_user.id, f'Вы ввели: {sale_date}\nДата не соответствует формату дд.мм.гггг\n'
        f'Введите дату ещё раз:\n')


@bot.message_handler(content_types=['text'])
def get_order_id(message, new_ticket):
    new_ticket.order_id = message.text
    update_reg_ticket(new_ticket)

    bot.register_next_step_handler(message, get_photo, new_ticket)
    bot.send_message(message.from_user.id, f'Номер заказа: {new_ticket.order_id}\nЗагрузите фото товара:')


@bot.message_handler(content_types=['photo'])
def get_photo(message, new_ticket):
    try:
        photo_id = message.photo[-1].file_id

        photo = bot.get_file(photo_id)
        downloaded_photo = bot.download_file(photo.file_path)

        src = 'img/' + photo_id

        with open(src, 'wb') as new_file:
            new_file.write(downloaded_photo)

        new_ticket.photo_file = src
        update_reg_ticket(new_ticket)

        bot.send_message(message.from_user.id, f'Вы загрузили фотографию!\nВыберите категорию товара:', reply_markup=get_category_markups())
        bot.register_next_step_handler(message, get_category, new_ticket)
    except TypeError:
        bot.register_next_step_handler(message, get_photo, new_ticket)
        bot.send_message(message.from_user.id, f'Фотография не была загружена\nПопробуйте ещё раз.\n')


@bot.message_handler(content_types=['text'])
def get_category(message, new_ticket):
    new_ticket.category = message.text
    update_reg_ticket(new_ticket)

    bot.send_message(message.from_user.id, f'Выбрана категория товара: {new_ticket.category}')

    first_question = get_question(1)
    bot.register_next_step_handler(message, get_questions, new_ticket, question=first_question)
    bot.send_message(message.from_user.id, first_question.text, reply_markup=get_yes_no_markups())


@bot.message_handler(content_types=['text'])
def get_questions(message, new_ticket, question):
    try:
        question = get_next_question(question, new_ticket, message.text)
        question = get_question(question.id)

        bot.send_message(message.from_user.id, question.text, reply_markup=get_yes_no_markups())

        if question.final_status:
            raise Exception('Have No Next Question')

        bot.register_next_step_handler(message, get_questions, new_ticket, question=question)
    except Exception as s:
        print(f'Have Exception: {s}')
        print('Опрос закончен')
        bot.send_message(message.from_user.id, 'Спасибо!', reply_markup=continue_markups())
        bot.register_next_step_handler(message, initial_block)


bot.polling(none_stop=True)
