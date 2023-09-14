import hmac
from hashlib import sha256
import tkinter as tk
import pymysql
from pymysql.cursors import DictCursor
from tkinter import messagebox


class HashTools:
    secret = 'password'
    digest = sha256

    @classmethod
    def make_hash(cls, text: str | bytes):
        secret = cls.secret

        if isinstance(text, str):
            text = text.encode()

        if isinstance(secret, str):
            secret = secret.encode()

        return hmac.new(secret, text, digestmod=cls.secret).hexdigest()

    @classmethod
    def compare_digest(cls, digest: str | bytes, text: str | bytes):
        new_hash = cls.make_hash(text)
        return hmac.compare_digest(digest, new_hash)


class Database:
    connection_data = dict(
        host='localhost',
        user='root',
        port=3306,
        password='',
        database='login'
    )

    db = pymysql.connect(
        cursorclass=DictCursor,
        **connection_data
    )

    cursor = db.cursor()

    def __init__(self):
        self.init_db()

    def init_db(self):
        query = "CREATE TABLE IF NOT EXISTS users (id INT UNSIGNED AUTO_INCREMENT, login VARCHAR(50), password_hash VARCHAR(255), PRIMARY KEY (id))"
        self.cursor.execute(query, ())
        self.db.commit()

    def get_user(self, **kwargs):
        query = 'SELECT * FROM users WHERE '
        args = []
        args_str = []

        for key, val in kwargs.items():
            args.append(val)
            args_str.append(f"{key} = %s")

        query += " AND ".join(args_str)
        self.cursor.execute(query, args)
        return self.cursor.fetchone()

    def add_user(self, **kwargs):
        query = 'INSERT INTO users ({}) VALUES ({})'
        args_str = []
        args = []

        if not kwargs:
            return

        for key, val in kwargs.items():
            args.append(val)
            args_str.append(f'{key}')

        query = query.format(
            ", ".join(args_str),
            ", ".join(['%s' for _ in range(len(args_str))])
        )

        self.cursor.execute(query, args)
        return self.db.commit()


class MainView:
    def __init__(self):
        self.root = tk.Tk()
        self.init_ui()

    def init_ui(self):
        tk.Label(self.root, text='Вы успешно вошли!').pack()

    def mainloop(self):
        return self.root.mainloop()


class LoginView:
    db = Database()

    login_entry: tk.Entry
    password_entry: tk.Entry

    register_btn: tk.Button
    confirm_btn: tk.Button

    def __init__(self):
        self.root = tk.Tk()
        self.init_ui()

    def init_ui(self):
        self.root.title('Авторизация')

        self.login_entry = tk.Entry(self.root)
        self.password_entry = tk.Entry(self.root)

        tk.Label(self.root, text='Логин:').grid(column=0, row=0)
        self.login_entry.grid(column=1, row=0)

        tk.Label(self.root, text='Пароль:').grid(column=0, row=1)
        self.password_entry.grid(column=1, row=1)

        self.confirm_btn = tk.Button(self.root, text='Войти', command=self.button_callback)
        self.confirm_btn.grid(column=0, row=2)

        self.register_btn = tk.Button(self.root, text='Регистрация', command=lambda: RegisterView().mainloop())
        self.register_btn.grid(column=1, row=2)

    def button_callback(self):
        login, password = self.login_entry.get(), self.password_entry.get()

        user = self.db.get_user(login=login)
        if not user:
            return messagebox.showerror(message='Такого пользователя не существует!')

        password_hash = HashTools.make_hash(password)
        if HashTools.compare_digest(password_hash, user['password']):
            return messagebox.showinfo(message='Вы успешно вошли!')

        return messagebox.showerror(message='Неверный логин или пароль!')

    def mainloop(self):
        return self.root.mainloop()


class RegisterView:
    db = Database()

    login_entry: tk.Entry
    password_entry: tk.Entry
    password_confirm_entry: tk.Entry

    confirm_btn: tk.Button
    login_btn: tk.Button

    def __init__(self):
        self.root = tk.Tk()
        self.init_ui()

    def init_ui(self):
        self.root.title('Регистрация')

        self.login_entry = tk.Entry(self.root)
        self.password_entry = tk.Entry(self.root)
        self.password_confirm_entry = tk.Entry(self.root)

        tk.Label(self.root, text='Логин:').grid(column=0, row=0)
        self.login_entry.grid(column=1, row=0)

        tk.Label(self.root, text='Пароль:').grid(column=0, row=1)
        self.password_entry.grid(column=1, row=1)

        tk.Label(self.root, text='Повтор пароля:').grid(column=0, row=2)
        self.password_confirm_entry.grid(column=1, row=2)

        self.confirm_btn = tk.Button(self.root, text='Регистрация', command=self.button_callback)
        self.confirm_btn.grid(column=0, row=3)

    def button_callback(self):
        login, password, password_confirm = self.login_entry.get(), self.password_entry.get(), self.password_confirm_entry.get()

        user = self.db.get_user(login=login)
        if user:
            return messagebox.showerror(message='ТакоЙ пользователь уже существует!')

        if password != password_confirm:
            return messagebox.showerror(message='Пароли не совпадают!')

        password_hash = HashTools.make_hash(password)
        self.db.add_user(login=login, password_hash=password_hash)
        messagebox.showinfo(message='Вы успешно зарегистрировались!')
        return LoginView().mainloop()

    def mainloop(self):
        return self.root.mainloop()


view = LoginView()
view.mainloop()
