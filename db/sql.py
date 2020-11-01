import psycopg2
import db.config as db

conn = psycopg2.connect(dbname=db.DATABASE,
                        user=db.USERNAME,
                        password=db.PASSWORD,
                        host=db.HOST)


class is_check:

    @staticmethod
    def user(user_id):
        cursor = conn.cursor()
        cursor.execute('SELECT EXISTS(SELECT * FROM users WHERE telegram_id = %s);', (user_id,))
        return cursor.fetchone()


class insert:

    @staticmethod
    def user(user_id, first_name, last_name):
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (telegram_id, first_name, last_name) '
                       'VALUES(%s, %s, %s)', (user_id, first_name, last_name))
        conn.commit()