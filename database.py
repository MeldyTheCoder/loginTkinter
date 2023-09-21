import pymysql
from pymysql.cursors import DictCursor


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

        query = 'CREATE TABLE IF NOT EXISTS products (id INT AUTO_INCREMENT, title VARCHAR(50), price INT, quantity INT, PRIMARY KEY (id))'
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

    def get_product(self, **kwargs):
        query = "SELECT * FROM products WHERE "
        args = []
        args_str = []

        if not kwargs:
            return None

        for key, val in kwargs.items():
            args.append(val)
            args_str.append(f'{key} = %s')

        query += ' AND '.join(args_str)
        self.cursor.execute(query, args)
        return self.cursor.fetchone()

    def get_products(self, **kwargs):
        query = "SELECT * FROM products"
        args = []
        args_str = []

        if kwargs:
            query += ' WHERE '
            for key, val in kwargs.items():
                args.append(val)
                args_str.append(f'{key} = %s')

            query += ' AND '.join(args_str)

        self.cursor.execute(query, args)
        return self.cursor.fetchall()

    def add_product(self, **kwargs):
        query = 'INSERT INTO products ({}) VALUES ({})'
        args = []
        args_str = []

        if not kwargs:
            return None

        for key, val in kwargs.items():
            args.append(val)
            args_str.append(key)

        arg_patterns = ["%s" for _ in args]

        query = query.format(
            ', '.join(args_str),
            ', '.join(arg_patterns)
        )

        self.cursor.execute(query, args)
        self.db.commit()
        return self.cursor.lastrowid

    def update_product(self, row_id: int, **kwargs):
        query = 'UPDATE products SET {} WHERE id = %s'
        args = []
        args_str = []

        if not kwargs:
            return

        for key, val in kwargs.items():
            args_str.append(f"{key} = %s")
            args.append(val)

        args.append(row_id)

        self.cursor.execute(query, args)
        self.db.commit()

    def delete_product(self, **kwargs):
        query = "DELETE FROM products WHERE "
        args = []
        args_str = []

        if not kwargs:
            return None

        for key, val in kwargs.items():
            args.append(val)
            args_str.append(f'{key} = %s')

        query += ' AND '.join(args_str)
        self.cursor.execute(query, args)
        self.db.commit()