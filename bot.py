from aiogram import Bot,Dispatcher,executor,types
from aiogram.utils.callback_data import CallbackData
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.filters import BoundFilter, Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State,StatesGroup
from aiogram.types import InputFile

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from models import Course,Item,Book
from category import get_items, get_courses, get_books

import requests
import typing
import logging
import os
import time


#Bot configs
API_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = [os.environ.get('ADMIN_ID')]
DATABASE_URL = f"{os.environ.get('DATABASE_URL')}"

engine = create_engine(DATABASE_URL)
session = Session(bind=engine)

#Настройка логгирования
logging.basicConfig(level=logging.INFO)

#Инициализация Бота и Диспетчера
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())




# Callback data for lists
courses_cd = CallbackData('course','id','action','name')
item_cd = CallbackData('item','id','action','name')
book_cd = CallbackData('book','action','name')
cancel_action = CallbackData('cancel','action')
# Callback data for choices
course_choice_action = CallbackData('course_choice','action')
item_choice_action = CallbackData('item_choice','action')
book_choice_action = CallbackData('book_choice','action')

#Создаем кастомный фильтр, который проверяет являетесь ли вы админом или нет
class AdminAccess(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin):
        self.is_admin = is_admin
        super().__init__()

    async def check(self, message):
        if str(message.from_user.id) in str(self.is_admin):
            return message.from_user.id
        else:
            await message.answer('Access Denied')
            raise CancelHandler()

dp.filters_factory.bind(AdminAccess)


#Создаем класс формы
class CourseForm(StatesGroup):
    course_name = State()

class ItemForm(StatesGroup):
    item_name = State()

class BookForm(StatesGroup):
    book_url = State()
    book_name = State()







"""Основные команды работы с ботом для пользователя!!!!"""

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message:types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.answer('Заполнение формы отменено.')

@dp.callback_query_handler(cancel_action.filter(action='cancel'))
async def cancel_handler(query: types.CallbackQuery):
    await query.message.edit_text('Заполнение формы отменено.')


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(
        'Привет, добро пожаловать в наш скромный бот.\n\n'
        '/help - Помощь в случае ошибок, и т.д.\n\n'
        '/show - Показать разделы библиотеки')

# Выводит курсы
@dp.message_handler(commands=['show'])
async def show_courses(message: types.Message):
    action = "to_item"
    courses = session.query(Course.id, Course.name).all()
    if courses == []:
        await message.answer('Курсов еще не существует\n\nСоздать: /change_course')

    else:
        markup_courses = get_courses(courses,courses_cd,action)
        await message.answer('Выберите курс: ',reply_markup=markup_courses)

@dp.callback_query_handler(item_cd.filter(action=["back_to_courses"]))
async def show_courses(query: types.CallbackQuery):
    action = "to_item"
    courses = session.query(Course.id, Course.name).all()
    markup_courses = get_courses(courses, courses_cd, action)
    await query.message.edit_text('Выберите курс: ', reply_markup=markup_courses)

@dp.message_handler(commands=['help'])
async def help_command(message:types.Message):
    await message.answer("Появились проблемы или у вас дома завелся призрак?\n\n"
                         "Пишите ему: @somename")

@dp.callback_query_handler(courses_cd.filter(action='hide_courses'))
async def query_hide_the_courses(query):
    await query.message.edit_text('Курсы скрыты\nОткрыть снова /show')

"""---------------COURSE HANDLERS-----------------"""

@dp.message_handler(commands=['change_course'], is_admin=ADMIN_ID)
async def choice_to_change_course(message:types.Message):
    choices = (
        ('Добавить курс','add'),
        ('Удалить курс','del')
    )
    markup_choices = types.InlineKeyboardMarkup()
    for choice, action in choices:
        markup_choices.add(types.InlineKeyboardButton(choice, callback_data=course_choice_action.new(action=action)))

    markup_choices.add(types.InlineKeyboardButton('Отменить', callback_data=cancel_action.new(action='cancel')))

    await message.answer('Выберите действие:', reply_markup=markup_choices)

@dp.callback_query_handler(course_choice_action.filter(action=['add','del']))
async def change_course(query: types.CallbackQuery, callback_data: typing.Dict[str,str], state: FSMContext):
    answer = callback_data['action']
    if answer == 'add':
        await query.message.edit_text("Введите название курса:\nОтменить:/cancel")
        await CourseForm.course_name.set()
    else:
        courses = session.query(Course.id, Course.name).all()
        action = 'del_course'
        markup_courses = get_courses(courses, courses_cd, action)
        await query.message.edit_text('Выберите курс для удаления', reply_markup=markup_courses)


@dp.message_handler(state=CourseForm.course_name)
async def add_choice_action_course(message: types.Message,state: FSMContext):

    async with state.proxy() as data:
        data['course_name'] = message.text
        all_courses = session.query(Course.name).filter(Course.name == '{}'.format(data['course_name'])).all()
        if all_courses != []:
            await message.answer('Курс с названием {} уже существует'.format(data['course_name']))
            await state.finish()
        else:
            course_name = Course(name=data['course_name'])
            session.add(course_name)
            session.commit()
            await message.answer('Вы добавили {} в курсы'.format(course_name.name))
            await state.finish()

@dp.callback_query_handler(courses_cd.filter(action=['del_course']))
async def del_choice_action_course(query: types.CallbackQuery, callback_data: typing.Dict[str,str]):
    course_name = callback_data['name']
    delete_course_query = session.query(Course).filter(Course.name == '{}'.format(course_name)).delete(synchronize_session=False)
    session.commit()
    await query.message.edit_text('Вы удалили {} из курсов'.format(course_name))


"""---------------ITEM HANDLERS-----------------"""

@dp.message_handler(commands=['change_item'], is_admin=ADMIN_ID)
async def choice_item_action(message: types.Message,state: FSMContext):
    choices = (
               ('Добавить предмет','add_item'),
               ('Удалить предмет','del_item')
               )


    markup_items = types.InlineKeyboardMarkup()
    for choice,action in choices:
        markup_items.add(types.InlineKeyboardButton(choice,callback_data=item_choice_action.new(action=action)))

    markup_items.add(
        types.InlineKeyboardButton('Отменить', callback_data=cancel_action.new(action='cancel')))

    await message.answer('Выберите действие',reply_markup=markup_items)



@dp.callback_query_handler(item_choice_action.filter(action=['add_item','del_item']))
async def change_item(query: types.CallbackQuery, callback_data: typing.Dict[str,str], state: FSMContext):
    response = callback_data['action']
    courses = session.query(Course.id, Course.name).all()

    markup_courses = get_courses(courses, courses_cd, action=response)
    await query.message.edit_text("Выберите курс ",reply_markup=markup_courses)



@dp.callback_query_handler(courses_cd.filter(action=['add_item']))
async def add_item(query: types.CallbackQuery, callback_data: typing.Dict[str,str]):
    global course_item_id
    global course_item_name
    course_item_name = callback_data['name']
    course_item_id = callback_data['id']
    await query.message.edit_text("Введите название предмета:\nОтменить:/cancel")
    await ItemForm.item_name.set()


@dp.message_handler(state=ItemForm.item_name)
async def add_item_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['item_name'] = message.text
        similiar_items = session.query(Item.name, Course.name).join(Course).filter(Item.name == data['item_name']).all()
        if similiar_items == []:
            item_name = Item(name=data['item_name'], course_id=course_item_id)
            session.add(item_name)
            session.commit()

            await state.finish()
            await message.answer("Предмет {} добавлен в {}".format(data['item_name'],course_item_name))

        else:
            await state.finish()
            await message.answer("Предмет с названием {} уже существует в {}".format(similiar_items[0][0],similiar_items[0][1]))


@dp.callback_query_handler(courses_cd.filter(action=['to_del_item']))
async def chose_deleted_item(query: types.CallbackQuery, callback_data: typing.Dict[str,str]):
        deleted_item = session.query(Item.id, Item.name).filter(Item.course_id == callback_data['id'])
        markup_items = get_items(deleted_item,item_cd,action="del_item")
        await query.message.edit_text("Удалите предмет", reply_markup=markup_items)

@dp.callback_query_handler(item_cd.filter(action=['del_item']))
async def delete_item(query: types.CallbackQuery, callback_data: typing.Dict[str,str]):
    delete_item = session.query(Item).filter(Item.name == '{}'.format(callback_data['name'])).delete(synchronize_session=False)
    session.commit()
    await query.message.edit_text("Предмет {} удален ".format(callback_data['name']))


@dp.callback_query_handler(courses_cd.filter(action='to_item'))
async def show_items(query: types.CallbackQuery, callback_data: typing.Dict[str,str]):
    action = "to_books"
    course_id = callback_data["id"]
    items = session.query(Item.id, Item.name).filter(Item.course_id == course_id).all()
    items_markup = get_items(items,item_cd,action)

    await query.message.edit_text("Выберите предмет", reply_markup=items_markup)

"""-----------BOOKS HANDLERS---------------"""

@dp.callback_query_handler(book_cd.filter(action=['back_to_item']))
async def back_to_item(query: types.CallbackQuery, callback_data: typing.Dict[str,str]):
    action = "to_books"
    course_id = session.query(Item.course_id).filter(Item.id == callback_data['name']).all()[0][0]
    items = session.query(Item.id, Item.name).filter(Item.course_id == course_id).all()
    items_markup = get_items(items, item_cd, action)

    await query.message.edit_text("Выберите предмет", reply_markup=items_markup)

@dp.callback_query_handler(item_cd.filter(action='to_books'))
async def select_book(query: types.CallbackQuery, callback_data: typing.Dict[str,str]):
    item_id = callback_data['id']
    item_name = callback_data['name']
    books = session.query(Book.id,Book.name,Book.url,Book.item_id).filter(Book.item_id == item_id).all()

    markup_books = get_books(books, item_id, book_cd)

    await query.message.edit_text(f'Выберите книгу из {item_name}:', reply_markup=markup_books)

#@dp.callback_query_handler(book_cd.filter(action=['to_file']))
#async def get_book(query: types.CallbackQuery, callback_data: typing.Dict[str,str]):



#Форма ввода названия книги и действия удаления/добавления книги!!!!

@dp.message_handler(commands=['change_book'], is_admin=ADMIN_ID)
async def change_book_action(message: types.Message):
    choices = (
        ('Добавить книгу', 'add_book'),
        ('Удалить книгу', 'del_book')
    )

    markup_items = types.InlineKeyboardMarkup()
    for choice, action in choices:
        markup_items.add(types.InlineKeyboardButton(choice, callback_data=book_choice_action.new(action=action)))

    markup_items.add(
        types.InlineKeyboardButton('Отменить', callback_data=cancel_action.new(action='cancel')))

    await message.answer('Выберите действие', reply_markup=markup_items)


@dp.callback_query_handler(book_choice_action.filter(action=['add_book','del_book']))
async def change_book_to_courses(query: types.CallbackQuery, callback_data: typing.Dict[str,str]):
    response = callback_data['action']
    courses = session.query(Course.id, Course.name).all()
    markup = get_courses(courses,courses_cd,action=response)

    await query.message.edit_text("Выберите курс", reply_markup=markup)

@dp.callback_query_handler(courses_cd.filter(action=['add_book','del_book']))
async def change_book_to_items(query: types.CallbackQuery, callback_data: typing.Dict[str,str]):
    response = callback_data['action']
    course_id = callback_data['id']
    items = session.query(Item.id, Item.name).filter(Item.course_id == course_id).all()
    markup = get_items(items,item_cd,action=response)

    await query.message.edit_text("Выберите предмет", reply_markup=markup)

@dp.callback_query_handler(item_cd.filter(action=['del_book']))
async def del_book_from_chosen_item(query: types.CallbackQuery, callback_data: typing.Dict[str,str]):
    response = callback_data['action']
    item_id = callback_data['id']
    book_list = session.query(Book.id, Book.name, Book.url, Book.item_id).filter(Book.item_id == item_id).all()
    markup = get_books(book_list,item_id, book_cd, action=response )
    await query.message.edit_text("Удалите книгу", reply_markup=markup)

@dp.callback_query_handler(book_cd.filter(action=['del_book']))
async def delete_book(query: types.CallbackQuery, callback_data: typing.Dict[str,str]):
    book_name = callback_data['name']
    book = session.query(Book).filter(Book.name == book_name).delete(synchronize_session=False)
    session.commit()
    await query.message.edit_text(f"Книга {callback_data['name']} удалена")



@dp.callback_query_handler(item_cd.filter(action=['add_book']))
async def add_book_to_item(query: types.CallbackQuery, callback_data: typing.Dict[str,str]):
    global item_book_id
    global item_book_name
    item_book_name = callback_data['name']
    item_book_id = callback_data['id']
    await query.message.edit_text("Прикрепите нужный файл:\nОтменить:/cancel")
    await BookForm.book_url.set()


@dp.message_handler(content_types=['document'], state=BookForm.book_url)
async def add_file_url(message: types.Message, state: FSMContext):
    document_id = message.document.file_id
    file_info = await bot.get_file(document_id)
    fi = file_info.file_path
    url = f'https://api.telegram.org/file/bot{API_TOKEN}/{fi}'
    async with state.proxy() as data:
        data['book_url'] = url
        await message.answer("Наименуйте файл")

    await BookForm.book_name.set()

@dp.message_handler(state=BookForm.book_name)
async def add_item_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['book_name'] = message.text
        similiar_books = session.query(Book.name, Item.name).join(Item).filter(Book.name == data['book_name']).all()
        if similiar_books == []:
            book = Book(name=data['book_name'], url=data['book_url'], item_id=item_book_id)
            session.add(book)
            session.commit()

            await state.finish()
            await message.answer("Книга {} добавлена в {}".format(data['book_name'],item_book_name))

        else:
            await state.finish()
            await message.answer("Книга с названием {} уже существует в {}".format(similiar_books[0][0],similiar_books[0][1]))


"""-----------SENDING A FILE----------------"""
@dp.callback_query_handler(book_cd.filter(action=["to_files"]))
async def send_file(query: types.CallbackQuery, callback_data: typing.Dict[str,str]):
    book_name = callback_data['name']
    book_url = session.query(Book.url).filter(Book.name == book_name).all()[0][0]
    await query.message.edit_text("Достаем книжку с полки...")
    await bot.send_document(query.message.chat.id, InputFile.from_url(book_url, f"{book_name}.pdf"))
    await query.message.edit_text("Приятного чтения. \n/show")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)




