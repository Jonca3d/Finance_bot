import psycopg2
import db.config as db

conn = psycopg2.connect(dbname=db.DATABASE,
                        user=db.USERNAME,
                        password=db.PASSWORD,
                        host=db.HOST)


class is_check:

    @staticmethod
    def user(user_id: int):
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

    @staticmethod
    def account(user_id: int, name: str, account_balance: int, type_account: int, description='') -> None:
        """
        :param user_id: ID пользователя в Телеграм
        :param name: Название счета
        :param account_balance: Остаток на счете
        :param type_account: Тип счета (дебетовый или кредитный)
        :param description: Описание счета
        :return:
        """
        cursor = conn.cursor()
        cursor.execute('INSERT INTO accounts (name, user_id, description, account_balance, type) '
                       'VALUES(%s, %s, %s, %s, %s)', (name, user_id, description, account_balance, type_account))
        conn.commit()


class get_data:

    @staticmethod
    def account_type(type_name):
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM account_types WHERE name = %s', (type_name,))
        return cursor.fetchone()


class fetch_data:

    @staticmethod
    def accounts(user_id):
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE user_id = %s', (user_id,))
        return cursor.fetchall()