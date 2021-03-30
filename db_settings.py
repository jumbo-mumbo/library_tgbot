import sqlite3
import requests

conn = sqlite3.connect('db.sqlite')
cursor = conn.cursor()


def add_subject(name,id):
    cursor.execute(f"insert into subjects(name,subjects_id) values ('{name}','{id}')")
    conn.commit()

def is_subject_exist(subject_name, subject_id):
    cursor.execute("select name,subjects_id from subjects")
    ftch = cursor.fetchall()
    result = False
    for name, id in ftch:
        if name == subject_name and int(id) == subject_id:
            result = True
            break

    return result

def is_book_exist(book_name, subj_name):
    cursor.execute("select name, subject_name from books")
    ftch = cursor.fetchall()
    result = False
    for name, subject_name in ftch:
        if name == book_name and subject_name == subj_name:
            result = True
            break

    return result

def del_duplicates(list):
    new_list = []
    new_list.append(list[0])
    for i in list:
        is_unique = True
        for j in new_list:
            if i[0] == j[0]:
                is_unique = False

        if is_unique:
            new_list.append(i)
    return new_list



def del_subject(name,id):
    cursor.execute(f"delete from subjects where name='{name}' and subjects_id='{id}'")
    conn.commit()

    cursor.execute(f"delete from books where subject_name='{name}'")
    conn.commit()


def add_book(name,id,subject_name):
    cursor.execute(f"insert into books(name,book_id,subject_name) values ('{name}','{id}','{subject_name}')")
    conn.commit()

def del_book(name,subject_name):
    cursor.execute(f"delete from books where name='{name}' and subject_name='{subject_name}'")
    conn.commit()





def select_book(name):
    cursor.execute(f"SELECT book_id FROM books WHERE name = '{name}'")
    ftch = cursor.fetchall()
    x = 0
    for i in ftch:
        x = i[0]
    return x

def get_book_name(name):
    cursor.execute(f"SELECT name FROM books WHERE name='{name}'")
    ftch = cursor.fetchall()
    x = 0
    for i in ftch:
        x = i[0]

    return x


def load_book(url,name):
    r = requests.get(url=url, stream=True)
    rk = r.raw.read()
    with open(f'documents/{name}', 'wb') as fd:
        fd.write(rk)
        fd.close()

def only_int(mass):
    x = 0
    for i in mass:
        for j in i:
            if j.isdecimal():
                x += int(j)
    return x




conn.commit()