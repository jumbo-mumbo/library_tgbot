from aiogram import types

#Получаем список кнопок из кортежа "курсы"
def get_courses(category,category_cd,action):
    markup = types.InlineKeyboardMarkup()
    for crs_id, crs in category:
        markup.add(types.InlineKeyboardButton(
            crs,
            callback_data = category_cd.new(
                action=action,
                id=crs_id,
                name=f'{crs}')
        )
        )

    markup.add(types.InlineKeyboardButton('-Hide-', callback_data=category_cd.new(id='-', action='hide_courses', name='-')))

    return markup



#Получаем список из кортежа "предметы" + добовляем действие возврата
def get_items(category,category_cd,action=None):
    markup = types.InlineKeyboardMarkup()
    new_action = "to_books" if action == None else action
    for id, item in category:
            markup.add(types.InlineKeyboardButton(
                item,
                callback_data=category_cd.new(action=new_action,id=id,name=f'{item}'))
            )

    markup.add(types.InlineKeyboardButton("<< Back", callback_data=category_cd.new(id='-', action="back_to_courses",name='-')))

    return markup

def get_books(books,current_item_id,book_cd,action=None):
    markup = types.InlineKeyboardMarkup()
    new_action = "to_files" if action == None else action
    for id, book, book_url, item_id in books:
        markup.add(types.InlineKeyboardButton(
            book,
            callback_data=book_cd.new(action=new_action, name=f'{book}'))
            )

    markup.add(types.InlineKeyboardButton('<< Back',callback_data=book_cd.new(action='back_to_item', name=f'{current_item_id}')))

    return markup