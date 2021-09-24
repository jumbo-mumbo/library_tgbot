<<<<<<< HEAD
#from config import TOKEN,ADMIN_ID

=======
>>>>>>> e0c052e31b889a8b8100c96f764a416e5af2ea37
from aiogram import Bot,Dispatcher,executor,types
from aiogram.utils.callback_data import CallbackData
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.filters import BoundFilter, Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State,StatesGroup
<<<<<<< HEAD

from category import get_subjects, get_courses, get_books

import typing
import logging
import sqlite3
import db_settings
import os

con = sqlite3.connect('db.sqlite')
cur = con.cursor()


API_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = [os.environ.get('ADMIN_ID')]


#Настройка логгирования
logging.basicConfig(level=logging.INFO)
=======
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

>>>>>>> e0c052e31b889a8b8100c96f764a416e5af2ea37
#Инициализация Бота и Диспетчера
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


<<<<<<< HEAD
courses = (
        ('1 курс',1),
        ('2 курс', 2),
        ('3 курс', 3),
        ('4 курс', 4),
        ('5 курс', 5),
        ('6 курс', 6),
    )
=======
>>>>>>> e0c052e31b889a8b8100c96f764a416e5af2ea37


# Callback data for lists
courses_cd = CallbackData('course','id','action','name')
<<<<<<< HEAD
subjects_cd = CallbackData('subject','id','action','name')
book_cd = CallbackData('book','action','name')
cancel_action = CallbackData('cancel','action')
# Callback data for choices
subject_choice_action = CallbackData('subject_choice','action')
book_choice_action = CallbackData('book_choice','action')

#Callback data for Subject name
subject_name = CallbackData('subject_name','name')



=======
item_cd = CallbackData('item','id','action','name')
book_cd = CallbackData('book','action','name')
cancel_action = CallbackData('cancel','action')
# Callback data for choices
course_choice_action = CallbackData('course_choice','action')
item_choice_action = CallbackData('item_choice','action')
book_choice_action = CallbackData('book_choice','action')

>>>>>>> e0c052e31b889a8b8100c96f764a416e5af2ea37
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
<<<<<<< HEAD
class NameForm(StatesGroup):
    book_name = State()
    subject_name = State()




"""Основные команды работы с ботом для пользователя!!!!"""


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(
        'Привет, добро пожаловать в наш скромный бот.\n\n'
        '/help - Помощь в случае ошибок, и т.д.\n\n'
        '/show - Показать разделы библиотеки')

# Выводит курсы
@dp.message_handler(commands=['show'])
async def show_courses(message: types.Message):
    action = "to_subject"
    markup_courses = get_courses(courses,courses_cd,action)
    await message.answer('Выберите курс: ',reply_markup=markup_courses)


@dp.message_handler(commands=['help'])
async def help_command(message:types.Message):
    await message.answer("Появились проблемы или у вас дома завелся призрак?\n\n"
                         "Пишите ему: @somename")

#Функуция которая выводит кнопки для выбора предмета
@dp.callback_query_handler(courses_cd.filter(action='to_subject'))
async def show_subjects(query: types.CallbackQuery, callback_data: typing.Dict[str,str]):
    cur.execute("SELECT * FROM subjects")
    subjects = cur.fetchall()
    crs_id = callback_data['id']
    crs_name = callback_data['name']
    markup_subjects = get_subjects(subjects,subjects_cd,crs_id)
    markup_subjects.add(types.InlineKeyboardButton('<< Back',
                                          callback_data=subjects_cd.new(id='-', action='back_to_courses', name='-')))

    await query.message.edit_text(f'Выберите предмет из {crs_name}: ',reply_markup=markup_subjects)

@dp.callback_query_handler(subjects_cd.filter(action='to_books'))
async def select_book(query: types.CallbackQuery, callback_data: typing.Dict[str,str]):
    cur.execute("SELECT * FROM books")
    books = cur.fetchall()
    sbj_name = callback_data['name']

    markup_books = get_books(books, sbj_name, book_cd)

    await query.message.edit_text(f'Выберите книгу из {sbj_name}:', reply_markup=markup_books)

@dp.callback_query_handler(book_cd.filter(action='to_files'))
async def get_file(query: types.CallbackQuery,callback_data: typing.Dict[str,str]):
    name = callback_data['name']
    file_id = db_settings.select_book(name)
    await query.message.answer_document(file_id)

    # await bot.send_chat_action(user_id, types.ChatActions.UPLOAD_DOCUMENT)
    # await bot.send_document(user_id, gf_id,caption='Этот файл специально для тебя!')

#Кнопка возвращения к выбору курсов (в выборе предмета)
@dp.callback_query_handler(subjects_cd.filter(action='back_to_courses'))
async def query_back_to_courses(query):
    action = "to_subject"
    markup_courses = get_courses(courses,courses_cd,action)
    await query.message.edit_text('Выберите курс: ', reply_markup=markup_courses)

#Кнопка возвращения к выбору курсов (в выборе предмета)
@dp.callback_query_handler(book_cd.filter(action='back_to_courses'))
async def query_back_to_courses(query):
    action = "to_subject"
    markup_courses = get_courses(courses,courses_cd,action)
    await query.message.edit_text('Выберите курс: ', reply_markup=markup_courses)



"""Форма ввода названия предмета и действия удаления/добавления предмета!!!!"""

@dp.message_handler(commands=['change_item'],is_admin=ADMIN_ID)
async def input_subject_name(message: types.Message):
    await message.answer("Введи название предмета:\nОтменить:/cancel")
    await NameForm.subject_name.set()
=======
class CourseForm(StatesGroup):
    course_name = State()

class ItemForm(StatesGroup):
    item_name = State()

class BookForm(StatesGroup):
    book_url = State()
    book_name = State()







"""Основные команды работы с ботом для пользователя!!!!"""
>>>>>>> e0c052e31b889a8b8100c96f764a416e5af2ea37

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

<<<<<<< HEAD
@dp.callback_query_handler(cancel_action.filter(action='cancel'),state='*')
async def cancel_handler(query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await query.message.edit_text('Заполнение формы отменено.')






@dp.message_handler(state=NameForm.subject_name)
async def choice_action(message: types.Message,state: FSMContext):
    choices = (
               ('Добавить предмет','add_sub'),
               ('Удалить предмет','del_sub')
               )


    markup = types.InlineKeyboardMarkup()
    for choice,action in choices:
        markup.add(types.InlineKeyboardButton(choice,callback_data=subject_choice_action.new(action=action)))

    markup.add(
        types.InlineKeyboardButton('-Hide-', callback_data=subject_choice_action.new(action='hide_choices')))

    markup.add(
        types.InlineKeyboardButton('Отменить', callback_data=cancel_action.new(action='cancel')))

    async with state.proxy() as data:
        data['subject_name'] = message.text

    await message.answer('Выберите действие',reply_markup=markup)


#Команда добавления предмета в курс(через кнопки)
#@dp.message_handler(state=Form.subject_name)
@dp.callback_query_handler(subject_choice_action.filter(action=['add_sub','del_sub']),state=NameForm.subject_name)
async def pick_course(query: types.CallbackQuery,state: FSMContext,callback_data: typing.Dict[str,str]):

    sbj_choice_action = callback_data['action']
    action = None
    context = None

    if sbj_choice_action == 'add_sub':
        action = 'add_subject'
        context = 'добавить'

    if sbj_choice_action == 'del_sub':
        action = 'del_subject'
        context = 'удалить'

    markup_courses = get_courses(courses, courses_cd, action)
    markup_courses.add(types.InlineKeyboardButton('Отменить', callback_data=cancel_action.new(action='cancel')))

    async with state.proxy() as data:
        subject_name = data['subject_name']
        await query.message.edit_text(f'Вы хотите {context} - {subject_name} !',reply_markup=markup_courses)


#кнопка сокрытия курсов

@dp.callback_query_handler(courses_cd.filter(action='hide_courses'))
async def query_hide_the_courses(query):
    await query.message.edit_text('Курсы скрыты\nОткрыть снова /show')

@dp.callback_query_handler(subject_choice_action.filter(action='hide_choices'))
async def query_hide_the_courses_form(query):
    await query.message.edit_text('Курсы скрыты')

@dp.callback_query_handler(courses_cd.filter(action=['add_subject','del_subject']),state=NameForm.subject_name)
async def modify_subject(query :types.CallbackQuery, callback_data: typing.Dict[str,str] ,state: FSMContext):
    crs_name = callback_data['name']
    action = callback_data['action']
    sbj_crs_id = db_settings.only_int(crs_name)
    result = None

    async with state.proxy() as data:
        subject_name = data['subject_name']
        if action == 'add_subject':
            if db_settings.is_subject_exist(subject_name, sbj_crs_id) == False:
                db_settings.add_subject(subject_name, sbj_crs_id)
                result = f'{subject_name} добавлен в {sbj_crs_id} курс\n' \
                         f'Показать: /show\n' \
                         f'Повторить: /change_item'
            else:
                result = f'Предмет с таким названием уже существует в {sbj_crs_id} курсе\n' \
                         f'Показать: /show\n' \
                         f'Повторить: /change_item'

        if action == 'del_subject':
            if db_settings.is_subject_exist(subject_name,sbj_crs_id) == True:
                db_settings.del_subject(subject_name, sbj_crs_id)
                result = f'{subject_name} удален из {sbj_crs_id} курс\n' \
                         f'Показать: /show\n' \
                         f'Повторить: /change_item'
            else:
                result = f'Предмет {subject_name} не существует в {sbj_crs_id}\n' \
                         f'Показать: /show\n' \
                         f'Повторить: /change_item'


    await state.finish()
    await query.message.edit_text(result)




"""Форма ввода названия книги и действия удаления/добавления книги!!!!"""

@dp.message_handler(commands=['change_book'], is_admin=ADMIN_ID)
async def document_name(message: types.Message, state: FSMContext):
    await message.answer('Введите название файла:\nОтменить:/cancel')
    await NameForm.book_name.set()

@dp.message_handler(state=NameForm.book_name)
async def choice_book_action(message: types.Message,state: FSMContext):
    choices = (
               ('Добавить книгу','add_book_to_course'),
               ('Удалить книгу','del_book_to_course')
               )


    markup = types.InlineKeyboardMarkup()
    for choice,action in choices:
        markup.add(types.InlineKeyboardButton(choice,callback_data=book_choice_action.new(action=action)))

    markup.add(
        types.InlineKeyboardButton('-Hide-', callback_data=book_choice_action.new(action='hide_choices')))

    markup.add(types.InlineKeyboardButton('Отменить', callback_data=cancel_action.new(action='cancel')))

    async with state.proxy() as data:
        data['book_name'] = message.text


    await message.answer('Выберите действие',reply_markup=markup)

@dp.callback_query_handler(subjects_cd.filter(action=['add_book_to_course','del_book_to_course']),state=NameForm.book_name)
@dp.callback_query_handler(book_choice_action.filter(action=['add_book_to_course','del_book_to_course']),state=NameForm.book_name)
async def show_courses(query: types.CallbackQuery,callback_data: typing.Dict[str,str]):
    action_book_choice = callback_data['action']
    action = None
    if action_book_choice == 'add_book_to_course':
        action = 'add_book_to_subject'

    if action_book_choice == 'del_book_to_course':
        action = 'del_book_to_subject'

    markup_courses = get_courses(courses,courses_cd,action)
    markup_courses.add(types.InlineKeyboardButton('Отменить', callback_data=cancel_action.new(action='cancel')))

    await query.message.edit_text('Выберите курс: ',reply_markup=markup_courses)


@dp.callback_query_handler(courses_cd.filter(action=['add_book_to_subject','del_book_to_subject']),state=NameForm.book_name)
async def pick_subject_for_book(query: types.CallbackQuery,state: FSMContext,callback_data: typing.Dict[str,str]):
    action_book_choice = callback_data['action']
    action = None
    context = None
    back_action = None

    if  action_book_choice == 'add_book_to_subject':
        action = 'add_book'
        back_action = 'add_book_to_course'
        context = 'добавить'

    if  action_book_choice == 'del_book_to_subject':
        action = 'del_book'
        back_action = 'del_book_to_course'
        context = 'удалить'

    cur.execute("SELECT * FROM subjects")
    raw_subjects = cur.fetchall()

    crs_id = callback_data['id']
    crs_name = callback_data['name']

    markup_subjects = get_subjects(raw_subjects, subjects_cd, crs_id,action)
    markup_subjects.add(types.InlineKeyboardButton('<< Back',callback_data=subjects_cd.new(id='-', action=back_action, name='-')))

    await query.message.edit_text(f'Выберите предмет из {crs_name}: ', reply_markup=markup_subjects)

    #clean_subjects = db_settings.del_duplicates(raw_subjects)

    #markup_subjects = get_subjects(courses, courses_cd, action)
    #markup_subjects.add(types.InlineKeyboardButton('-Hide-', callback_data=book_choice_action.new(action='hide_subjects')))


    #async with state.proxy() as data:
        #book_name = data['book_name']
        #await query.message.answer(f'Вы хотите {context} - {book_name} !',reply_markup=markup_subjects)




"""Обработка данных добавление/удаления данных из бд!!!"""

@dp.callback_query_handler(subjects_cd.filter(action='add_book'),state=NameForm.book_name)
async def add_book(query :types.CallbackQuery,callback_data: typing.Dict[str,str],state: FSMContext):
    result = None
    await NameForm.next()
    subject_name = callback_data['name']

    async with state.proxy() as data:
        data['subject_name'] = subject_name
        subject_name = data['subject_name']
        book_name = data['book_name']
        if db_settings.is_book_exist(book_name, subject_name) == False:
            result = f"Добавьте файл в {subject_name}:"

        else:
            result = f"Книга с таким названием уже существует в {subject_name}\n" \
                         f'Показать: /show\n' \
                         f'Повторить: /change_item'

            await state.finish()

    await query.message.answer(result)

@dp.message_handler(content_types=['document'],state=NameForm.subject_name)
async def add_file(message: types.Message, state: FSMContext):
    document_id = message.document.file_id
    result = None
    async with state.proxy() as data:
        book_name = data['book_name']
        subject_name = data['subject_name']

        file_info = await bot.get_file(document_id)
        fi = file_info.file_path
        url = f'https://api.telegram.org/file/bot{API_TOKEN}/{fi}'
        #db_settings.load_book(url, name)

        db_settings.add_book(book_name, document_id,subject_name)


        await message.answer(f"Файл {book_name} успешно сохранен в {subject_name}\n"
                             f"Посмотреть: /show\n"
                             f"Повторить: /change_book \n\n "
                             f"Также доступен по ссылке: {url}")

    await state.finish()


@dp.callback_query_handler(subjects_cd.filter(action='del_book'),state=NameForm.book_name)
async def delete_book(query :types.CallbackQuery,callback_data: typing.Dict[str,str],state: FSMContext):
    await NameForm.subject_name.set()
    subject_name = callback_data['name']
    result = None
    async with state.proxy() as data:
        name = data['book_name']
        if db_settings.is_book_exist(name,subject_name) == True:
            db_settings.del_book(name,subject_name)
            result = f"Файл {name} удален из {subject_name}\n" \
                     f"Посмотреть: /show\n" \
                     f"Повторить: /change_book"
        else:
            result = f"Книги с названием {name} не существует в {subject_name}\n" \
                         f'Показать: /show\n' \
                         f'Повторить: /change_book'

    await query.message.answer(result)
    await state.finish()



@dp.callback_query_handler(book_choice_action.filter(action='hide_subjects'))
@dp.callback_query_handler(book_choice_action.filter(action='hide_choices'))
async def query_hide(query):
    await query.message.edit_text('Варианты скрыты')
=======
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

>>>>>>> e0c052e31b889a8b8100c96f764a416e5af2ea37

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)




