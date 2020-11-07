import psycopg2

import db.config as db

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
                   'timezone INTEGER'
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

    cursor.execute('CREATE TABLE IF NOT EXISTS payment_schedule('
                   'id SERIAL PRIMARY KEY,'
                   'account_id INTEGER NOT NULL, '
                   'payment_date DATE NOT NULL, '
                   'amount INTEGER NOT NULL'
                   ');')
    conn.commit()


def init_db_basic_data():
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

