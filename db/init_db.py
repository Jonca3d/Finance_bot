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

    cursor.execute('CREATE TABLE account_types('
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
                   'FOREIGN KEY("user_id") REFERENCES "users"("telegram_id"), '
                   'FOREIGN KEY("type") REFERENCES "account_types"("id")'
                   ');')
    conn.commit()


