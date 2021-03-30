from config import TOKEN,ADMIN_ID

from aiogram import Bot,Dispatcher,executor,types
from aiogram.utils.callback_data import CallbackData
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.filters import BoundFilter, Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State,StatesGroup

from category import get_subjects, get_courses, get_books, get_subjects_all
import db_settings
import typing
import logging
import sqlite3



con = sqlite3.connect('db.sqlite')
cur = con.cursor()


API_TOKEN = TOKEN

#Настройка логгирования
logging.basicConfig(level=logging.INFO)
#Инициализация Бота и Диспетчера
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


courses = (
        ('1 курс',1),
        ('2 курс', 2),
        ('3 курс', 3),
        ('4 курс', 4),
        ('5 курс', 5),
        ('6 курс', 6),
    )


# Callback data for lists
courses_cd = CallbackData('course','id','action','name')
subjects_cd = CallbackData('subject','id','action','name')
book_cd = CallbackData('book','action','name')

# Callback data for choices
subject_choice_action = CallbackData('subject_choice','action')
book_choice_action = CallbackData('book_choice','action')

#Callback data for Subject name
subject_name = CallbackData('subject_name','name')



#Создаем кастомный фильтр, который проверяет являетесь ли вы админом или нет
class AdminAccess(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin):
        self.is_admin = is_admin
        super().__init__()

    async def check(self, message):
        if message.from_user.id in self.is_admin:
            return message.from_user.id
        else:
            await message.answer('Access Denied')
            raise CancelHandler()

dp.filters_factory.bind(AdminAccess)


#Создаем класс формы
class NameForm(StatesGroup):
    book_name = State()
    subject_name = State()




"""Основные команды работы с ботом для пользователя!!!!"""

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(
        'Привет, добро пожаловать в наш скромный бот.\n'
        '/help - Помощь в случае ошибок, и т.д.\n'
        '/show - Показать разделы библиотеки')

# Выводит курсы
@dp.message_handler(commands=['show'])
async def show_courses(message: types.Message):
    action = "to_subject"
    markup_courses = get_courses(courses,courses_cd,action)
    await message.answer('Выберите курс: ',reply_markup=markup_courses)

# НАПИСАТЬ ФУНКЦИЮ ПОМОЩИ !!!!!!!!!!!!!!!!!!!!!!!

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
    await message.answer("Введи название предмета:")
    await NameForm.subject_name.set()

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


#
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

    async with state.proxy() as data:
        subject_name = data['subject_name']
        await query.message.answer(f'Вы хотите {context} - {subject_name} !',reply_markup=markup_courses)


#кнопка сокрытия курсов
@dp.callback_query_handler(subject_choice_action.filter(action='hide_choices'))
@dp.callback_query_handler(courses_cd.filter(action='hide_courses'))
async def query_hide_the_courses(query):
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
                result = f'{subject_name} добавлен в {sbj_crs_id} курс'
            else:
                result = f'Предмет с таким названием уже существует в {sbj_crs_id} курсе'

        if action == 'del_subject':
            if db_settings.is_subject_exist(subject_name,sbj_crs_id) == True:
                db_settings.del_subject(subject_name, sbj_crs_id)
                result = f'{subject_name} удален из {sbj_crs_id} курс'
            else:
                result = f'Предмет {subject_name} не существует в {sbj_crs_id}'


    await state.finish()
    await query.message.edit_text(result)




"""Форма ввода названия книги и действия удаления/добавления книги!!!!"""

@dp.message_handler(commands=['change_book'], is_admin=ADMIN_ID)
async def document_name(message: types.Message, state: FSMContext):
    await message.answer('Введите название файла:')
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
            result = f"Книга с таким названием уже существует в {subject_name}\n"
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
        url = f'https://api.telegram.org/file/bot{TOKEN}/{fi}'
        #db_settings.load_book(url, name)

        db_settings.add_book(book_name, document_id,subject_name)


        await message.answer(f"Файл {book_name} успешно сохранен в {subject_name} \n также доступен по ссылке: {url}")

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
            result = f"Файл {name} удален из {subject_name}"
        else:
            result = f"Книги с названием {name} не существует в {subject_name}"

    await query.message.answer(result)
    await state.finish()



@dp.callback_query_handler(book_choice_action.filter(action='hide_subjects'))
@dp.callback_query_handler(book_choice_action.filter(action='hide_choices'))
async def query_hide(query):
    await query.message.edit_text('Варианты скрыты')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)




