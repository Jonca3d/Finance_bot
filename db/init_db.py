import psycopg2
from psycopg2.extras import execute_values

import db.config as db
from db import sql

conn = psycopg2.connect(dbname=db.DATABASE,
                        user=db.USERNAME,
                        password=db.PASSWORD,
                        host=db.HOST)


def init_db_tables():
    cursor = conn.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS users('
                   'telegram_id INTEGER PRIMARY KEY, '
                   'first_name VARCHAR(40), '
                   'last_name VARCHAR(40), '
                   'timezone INTEGER,'
                   'current_balance INTEGER NOT NULL'
                   ');')
    conn.commit()

    cursor.execute('CREATE TABLE IF NOT EXISTS account_types('
                   'id SERIAL PRIMARY KEY, '
                   'name VARCHAR(40) NOT NULL'
                   ');')

    cursor.execute('CREATE TABLE IF NOT EXISTS accounts('
                   'id SERIAL PRIMARY KEY, '
                   'name VARCHAR(100) NOT NULL, '
                   'user_id INTEGER NOT NULL, '
                   'description VARCHAR(250), '
                   'account_balance INTEGER NOT NULL, '
                   'type INTEGER NOT NULL, '
                   'status BOOLEAN NOT NULL, '
                   'FOREIGN KEY("user_id") REFERENCES "users"("telegram_id"), '
                   'FOREIGN KEY("type") REFERENCES "account_types"("id")'
                   ');')
    conn.commit()

    cursor.execute('CREATE TABLE IF NOT EXISTS transaction_types('
                   'id SERIAL PRIMARY KEY,'
                   'name VARCHAR(40) NOT NULL'
                   ');')
    conn.commit()

    cursor.execute('CREATE TABLE IF NOT EXISTS transaction_categories('
                   'id SERIAL PRIMARY KEY, '
                   'name VARCHAR(40) NOT NULL, '
                   'description TEXT, '
                   'transaction_type INTEGER NOT NULL, '
                   'FOREIGN KEY("transaction_type") REFERENCES "transaction_types"("id")'
                   ');')
    conn.commit()

    cursor.execute('CREATE TABLE IF NOT EXISTS transactions('
                   'id SERIAL PRIMARY KEY, '
                   'user_id INTEGER NOT NULL, '
                   'transaction_category INTEGER NOT NULL, '
                   'amount INTEGER NOT NULL, '
                   'timestamp INTEGER NOT NULL, '
                   'FOREIGN KEY("user_id") REFERENCES "users"("telegram_id"), '
                   'FOREIGN KEY("transaction_category") '
                   'REFERENCES "transaction_categories"("id")'
                   ');')
    conn.commit()

    # В эту таблицу сохраняется значение текущего баланса пользователя после совершения каждой транзакции
    cursor.execute('CREATE TABLE IF NOT EXISTS balance_history('
                   'id SERIAL PRIMARY KEY, '
                   'user_id INTEGER NOT NULL, '
                   'balance INTEGER NOT NULL, '
                   'timestamp INTEGER NOT NULL, '
                   'FOREIGN KEY("user_id") REFERENCES "users"("telegram_id")'
                   ');')
    conn.commit()

    # График платежей
    # TODO Добавить возможность расписывать график платежей. Например за кредит
    cursor.execute('CREATE TABLE IF NOT EXISTS payment_schedule('
                   'id SERIAL PRIMARY KEY,'
                   'account_id INTEGER NOT NULL, '
                   'payment_date DATE NOT NULL, '
                   'amount INTEGER NOT NULL'
                   ');')
    conn.commit()


def init_db_basic_data():
    # TODO Провести рефакторинг (объединить запросы по добавлению записей в одну таблицу)
    cursor = conn.cursor()

    cursor.execute('SELECT EXISTS(SELECT*FROM account_types WHERE name = %s)', ('debit',))
    check_data = cursor.fetchone()
    if not check_data[0]:
        cursor.execute('INSERT INTO account_types(name) '
                       'VALUES(%s);', ('debit',))
        conn.commit()

    cursor.execute('SELECT EXISTS(SELECT*FROM account_types WHERE name = %s)', ('credit',))
    check_data = cursor.fetchone()
    if not check_data[0]:
        cursor.execute('INSERT INTO account_types(name) '
                       'VALUES(%s);', ("credit",))
        conn.commit()

    cursor.execute('SELECT EXISTS(SELECT*FROM transaction_types WHERE name = %s)', ("arrival_of_money",))
    check_data = cursor.fetchone()
    if not check_data[0]:
        cursor.execute('INSERT INTO transaction_types(name) '
                       'VALUES(%s);', ("arrival_of_money", ))
        conn.commit()

    cursor.execute('SELECT EXISTS(SELECT*FROM transaction_types WHERE name = %s)', ("spending_of_money",))
    check_data = cursor.fetchone()
    if not check_data[0]:
        cursor.execute('INSERT INTO transaction_types(name) '
                       'VALUES(%s);', ("spending_of_money",))
        conn.commit()

    cursor.execute('SELECT EXISTS(SELECT*FROM transaction_types WHERE name = %s)', ("transfer_between_accounts",))
    check_data = cursor.fetchone()
    if not check_data[0]:
        cursor.execute('INSERT INTO transaction_types(name) '
                       'VALUES(%s);', ("transfer_between_accounts",))
        conn.commit()

    cursor.execute('SELECT EXISTS(SELECT*FROM transaction_types WHERE name = %s)', ("arrears",))
    check_data = cursor.fetchone()
    if not check_data[0]:
        cursor.execute('INSERT INTO transaction_types(name) '
                       'VALUES(%s);', ("arrears",))
        conn.commit()

    if sql.is_check.transaction_categories()[0] == 0:
        data = [("Продукты", "Покупка продуктов питания", "2"),
                ("Жильё", "Оплата жилья. Аренда. Комунальные услуги", "2"),
                ("Одежда", "Покупка одежды, обуви и т.д.", "2"),
                ("Хобби", "Приобретение предметов для занятий своим хобби", "2"),
                ("Кафе/Рестораны", "Посещение кафе или ресторана", "2"),
                ("Транспорт", "Расходы на проезд или на личный транспорт", "2"),
                ("Телефон", "Оплата услуг телефонии", "2"),
                ("Интернет", "Оплата услуг интернет", "2"),
                ("Быт", "Расходы на приобретени бытовой химии или других предметов для поддержания чистоты в доме", "2"),
                ("Лекарства", "Расходы на лекарства при болезни", "2"),
                ("Здоровье", "Приобретение БАДов или витаминов или средств по уходу за собой", "2"),
                ("Подарки", "Расходы на подарки для друзей, коллег и близких", "2"),
                ("Развлечения", "Посещение клубов, кино, игровые автоматы", "2"),
                ("Кредит", "Выплаты по кредиту", "2"),
                ("Отдых", "Расходы на отпуск. Например приобретение тура или покупка билета", "2"),
                ("Образование", "Приобретение курсов, посещение тренингов, репетитор", "2"),
                ("Книги", "Покупка книг", "2"),
                ("Зарплата", "Зарплата", "1"),
                ("Аванс", "Аванс", "1"),
                ("Подарок", "Подарок", "1")]
        print('I am here')
        execute_values(cursor, 'INSERT INTO transaction_categories(name, description, transaction_type) '
                               'VALUES %s', data)
        conn.commit()

