import sqlalchemy
from sqlalchemy import desc, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import sessionmaker
from validators import VALIDATORS

CONNECTION_STRING = 'mysql+mysqlconnector://root:1234567890@localhost:3306/chat_bot'
engine = create_engine(CONNECTION_STRING, echo=False)
Session = sessionmaker(bind=engine)
session = Session()


Base = declarative_base()


class Categories(Base):
        __tablename__ = 'categories'

        id = Column(Integer, primary_key=True)
        name = Column(String)
        pp = Column(TINYINT)
        tst = Column(TINYINT)

        def __init__(self, name, pp, tst):
                self.name = name
                self.pp = pp
                self.tst = tst

        def __repr__(self):
                return f"<Category({self.name}, {self.pp}, {self.tst})>"


class RegTicket(Base):
    __tablename__ = 'reg_ticket'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fio = Column(String)
    address = Column(String)
    sale_date = Column(DateTime)
    order_id = Column(String)
    photo_file = Column(String)
    category_id = Column(Integer, ForeignKey(Categories.id))
    tg_user_id = Column(Integer)

    def __repr__(self):
        return f"<Registrated({self.id}, {self.fio}, {self.category_id})>"


class Questions(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String)
    yes_answer = Column(Integer)
    no_answer = Column(Integer)
    final_status = Column(Integer)
    validator = Column(String)

    def __repr__(self):
        return f"<Question({self.id}, {self.text}, {self.yes_answer}, {self.no_answer})>"


def get_categories(category_name=None):
    if not category_name:
        result_ = session.query(Categories).all()
    else:
        result_ = session.query(Categories).filter_by(name=category_name).first()

    return result_


def add_new_reg_ticket(tg_uid):
    new_record = RegTicket()
    new_record.tg_user_id = tg_uid
    session.add(new_record)
    session.commit()

    reg_id = session.query(RegTicket).filter_by(tg_user_id=tg_uid).order_by(desc(RegTicket.id)).first()

    return reg_id.id


def update_reg_ticket(ticket):
    reg_ticket = session.query(RegTicket).filter_by(id=ticket.id).order_by(desc(RegTicket.id)).first()
    reg_ticket.fio = ticket.fio
    reg_ticket.address = ticket.address
    reg_ticket.sale_date = ticket.sale_date
    reg_ticket.order_id = ticket.order_id
    reg_ticket.photo_file = ticket.photo_file

    if ticket.category:
        category = get_categories(ticket.category)
        reg_ticket.category_id = category.id

    session.commit()


def get_question(current_question):
    question = session.query(Questions).filter_by(id=current_question).first()
    return question


def get_next_question(question, ticket, answer=None):
    if question.final_status:
        return None
    else:
        if answer:
            if answer == 'Да':
                question = get_question(question.yes_answer)
            elif answer == 'Нет':
                question = get_question(question.no_answer)

    if question.validator:
        if VALIDATORS.get(question.validator):
            category_ = get_categories(ticket.category)
            validator_answer = VALIDATORS[question.validator](ticket, category_)

            if validator_answer:
                question = get_question(question.yes_answer)
            else:
                question = get_question(question.no_answer)

            if question.validator:
                question = get_next_question(question, ticket)

    return question
