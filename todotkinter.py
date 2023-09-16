import sqlite3
from tkinter import Label, Listbox, Tk, Variable, font, ttk

"""Шаблоны запросов к бд."""


QUERY = "INSERT INTO Todo (todo, ind) VALUES (?, ?)"
UPDATE_QUERY = 'UPDATE Todo SET ind = ? WHERE pk = ?'
UPDATE_TODO = 'UPDATE Todo SET todo = ? WHERE ind = ?'
ADD = 'INSERT INTO Todo (todo, ind) VALUES (?, ?)'
DELETE = 'DELETE FROM Todo WHERE ind = ?'


"""Подключаемся если есть, в противном случае создаем новую."""


connect = sqlite3.connect('todo.db')
cursor = connect.cursor()
cursor.execute(
    'CREATE TABLE IF NOT EXISTS Todo(pk integer NOT NULL'
    ' PRIMARY KEY AUTOINCREMENT, todo TEXT, ind INTEGER)'
)


"""Сохраняет данные, закрывает соединение и завершает работу"""


def save(func, *args, **kwargs):

    def wrap(*args, **kwargs):
        try:
            func()
        except Exception:
            print('Ошибка программы')
            connect.commit()
            connect.close()
            root.destroy()

    return wrap


"""Блок функций."""

"""Работают параллельно с бд и с текущими данными, в этой сессии."""


@save
def add_update(*a):
    """Обновляет или добавляет значение."""
    rm()
    end = curr_listbox.size()
    inp.focus()
    new_language = inp.get()
    selection = curr_listbox.curselection()
    if new_language.strip(' ') and not selection:
        cursor.execute(ADD, (new_language, end))
        connect.commit()
        curr_listbox.insert('end', new_language)
    elif new_language.strip(' ') and len(selection) == 1:
        cursor.execute(UPDATE_TODO, (new_language, selection[0]))
        connect.commit()
        curr_listbox.delete(selection[0])
        curr_listbox.insert(selection[0], new_language)
    elif len(selection) > 1:
        clear()
    connect.commit()
    inp.delete(first=0, last='end')
    inp.focus()


@save
def delete():
    """Удаляет значение по индексу, может удалять сразу несколько позиций."""
    selection = curr_listbox.curselection()
    if selection:
        cursor.execute(DELETE, (selection[0],))
        update_ind()
        connect.commit()
        curr_listbox.delete(selection[0])
    else:
        return
    [delete() for _ in selection]


@save
def update_ind():
    """
    После каждого удаления, проходит циклом по всем данным и
    меняет их индексы в порядке возрастания.
    Не самый оптимальный способ для работы с большими данными,
    но для нас самое то.
    """
    cursor.execute('SELECT pk FROM Todo ORDER BY pk ASC')
    we = [i[0] for i in cursor.fetchall()]
    for i, j in enumerate(we):
        cursor.execute(UPDATE_QUERY, (i, int(j)))
        connect.commit()


"""Добавление и удаление плейсхолдера."""


def rm(*a):
    if inp.get() == placeholder:
        inp.delete(0, 'end')
        inp.config(foreground='black')


def add(*a):
    if inp.get() == '':
        inp.insert(0, placeholder)
        inp.config(foreground='gray')


def clear(*a):
    curr_listbox.select_clear(0, 'end')


"""Получение данных с которыми будем работать в этой сессии."""


cursor.execute('SELECT todo FROM Todo ORDER BY ind ASC')
curr = [i[0] for i in cursor.fetchall()]


"""Формирование основного контента."""


root = Tk()
root.minsize(200, 400)
root.config(background='#a4aded')
root.title("Todo App")
root.geometry("700x500")


font1 = font.Font(family="Arial", size=24, weight="bold", slant="roman",
                  underline=True)
label = Label(text="Daily Tasks", font=font1, background='#a4aded')

placeholder = 'Add todo'

frame = ttk.Frame(borderwidth=1, relief='solid', padding=10, width=70)

inp = ttk.Entry(frame, width=60)
inp.bind("<ButtonPress-1>", clear)
inp.bind("<Return>", add_update)
inp.bind('<FocusIn>', rm)
inp.bind('<FocusOut>', add)

curr_var = Variable(frame, value=curr)

curr_listbox = Listbox(frame, listvariable=curr_var, width=60,
                       selectmode='multiple')

scrollbar = ttk.Scrollbar(frame, orient="vertical", command=curr_listbox.yview)
curr_listbox["yscrollcommand"] = scrollbar.set

style = ttk.Style()
style.configure("My.TButton", font="Tahoma 11", padding=3,
                anchor='s', background="#6406D6", cursor='raised')

add_btn = ttk.Button(text='add / update', command=add_update, width=58,
                     style="My.TButton", cursor='plus')
del_btn = ttk.Button(text='delete', command=delete, width=58,
                     style="My.TButton")

label.pack(ipady=20)
scrollbar.pack(side='right', fill='y', ipadx=0)
inp.pack(anchor='center', padx=3, ipadx=3)
frame.pack(anchor='center')
curr_listbox.pack(anchor='center', pady=7, padx=3, ipadx=3)
add_btn.pack(anchor='s', pady=5)
del_btn.pack(anchor='s', pady=5)


if __name__ == '__main__':
    add()
    root.mainloop()
