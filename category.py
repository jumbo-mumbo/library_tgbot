from aiogram import types

#Получаем список кнопок из кортежа "курсы"
def get_courses(category,category_cd,action):
    markup = types.InlineKeyboardMarkup()
    for crs, crs_id in category:
        markup.add(types.InlineKeyboardButton(
            crs,
            callback_data = category_cd.new(action=action,id=crs_id,name=f'{crs}а'))
        )

    markup.add(types.InlineKeyboardButton('-Hide-', callback_data=category_cd.new(id='-', action='hide_courses', name='-')))

    return markup

def get_subjects_all(category,category_cd,action):
    markup_subjects = types.InlineKeyboardMarkup()
    for sbj, id in category:
            markup_subjects.add(types.InlineKeyboardButton(sbj,callback_data=category_cd.new(action=action,id=id,name=f'{sbj}')))

    return markup_subjects

#Получаем список из кортежа "предметы" + добовляем действие возврата
def get_subjects(category,category_cd,id,action=None):
    markup = types.InlineKeyboardMarkup()
    new_action = "to_books" if action == None else action
    for sbj_id, sbj, crs_sbj_id in category:
        if crs_sbj_id == id:
            markup.add(types.InlineKeyboardButton(
                sbj,
                callback_data=category_cd.new(action=new_action,id=sbj_id,name=f'{sbj}'))
            )



    return markup

def get_books(books,sbj,book_cd):
    markup = types.InlineKeyboardMarkup()
    for id, book, book_id, book_sbj_name in books:
        if sbj == book_sbj_name:
            markup.add(types.InlineKeyboardButton(
                book,
                callback_data=book_cd.new(action='to_files', name=f'{book}'))
            )

    markup.add(types.InlineKeyboardButton('<< Back',
                                          callback_data=book_cd.new(action='back_to_courses', name='-')))

    return markup