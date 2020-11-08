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

    @staticmethod
    def transaction_categories():
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM transaction_categories')
        return cursor.fetchone()

    @staticmethod
    def account(user_id):
        cursor = conn.cursor()
        cursor.execute('SELECT EXISTS(SELECT * FROM accounts WHERE (user_id = %s AND status = %s))',
                       (user_id, True))
        return cursor.fetchone()


class insert:

    @staticmethod
    def user(user_id, first_name, last_name, time_stamp):
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (telegram_id, first_name, last_name, current_balance) '
                       'VALUES(%s, %s, %s, %s)', (user_id, first_name, last_name, 0))
        conn.commit()

        cursor.execute('INSERT INTO balance_history (user_id, balance, timestamp) '
                       'VALUES(%s, 0, %s)', (user_id, time_stamp))
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
        cursor.execute('INSERT INTO accounts (name, user_id, description, account_balance, type, status) '
                       'VALUES(%s, %s, %s, %s, %s, True)',
                       (name, user_id, description, account_balance, type_account))
        conn.commit()

    @staticmethod
    def transaction(user_id, transaction_category, amount, time_stamp):
        """
        Метод добавляет в БД запись о Транзакции
        :param user_id: ID пользователя
        :param transaction_category: Категория транзакции
        :param amount: Сумма транзакции
        :param time_stamp: Временная метка
        :return:
        """
        cursor = conn.cursor()
        cursor.execute('INSERT INTO transactions (user_id, transaction_category, amount, timestamp) '
                       'VALUES(%s, %s, %s, %s)', (user_id, transaction_category, amount, time_stamp))
        conn.commit()

    @staticmethod
    def balance_history_record(user_id, balance, time_stamp):
        cursor = conn.cursor()
        cursor.execute('INSERT INTO balance_history (user_id, balance, timestamp) '
                       'VALUES(%s, %s, %s)', (user_id, balance, time_stamp))
        conn.commit()


class update:

    @staticmethod
    def account_name(account_id, new_name):
        cursor = conn.cursor()
        cursor.execute('UPDATE accounts SET name = %s WHERE id = %s', (new_name, account_id))
        conn.commit()

    @staticmethod
    def account_description(account_id, new_description):
        cursor = conn.cursor()
        cursor.execute('UPDATE accounts SET description = %s WHERE id = %s', (new_description, account_id))
        conn.commit()

    @staticmethod
    def account_status(account_id, status: bool):
        """
        Изменяет статус счета.
        Передача в status False равносильна удалению счета.
        Счет становится недоступным для редактирования,
        проведения транзакций и пропадает из меню счетов.
        :param account_id: Идентификатор счета
        :param status: Принимает True или False. False для удаления чсета из меню счетов
        :return:
        """
        cursor = conn.cursor()
        cursor.execute('UPDATE accounts SET status = %s WHERE id = %s', (status, account_id))
        conn.commit()

    @staticmethod
    def account_balance(account_id, amount):
        cursor = conn.cursor()
        new_balance = int(get.account_balance(account_id)[0]) + int(amount)
        cursor.execute('UPDATE accounts SET account_balance = %s WHERE id = %s',
                       (new_balance, account_id))
        conn.commit()

    @staticmethod
    def overall_balance(user_id, amount):
        cursor = conn.cursor()
        new_balance = int(get.overall_balance(user_id)[0]) + int(amount)
        cursor.execute('UPDATE users SET current_balance = %s WHERE telegram_id = %s',
                       (new_balance, user_id))
        conn.commit()


class delete:

    @staticmethod
    def account(account_id):
        cursor = conn.cursor()
        cursor.execute('DELETE FROM accounts WHERE id = %s', (account_id,))
        conn.commit()


class get:
    """
    Класс содежит методы, которые возвращают единычныое значение из БД
    """
    @staticmethod
    def account_type(type_name):
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM account_types WHERE name = %s', (type_name,))
        return cursor.fetchone()

    @staticmethod
    def account(account_id):
        # TODO Осавить во входных данных только account_id
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (account_id,))
        return cursor.fetchone()

    @staticmethod
    def account_balance(account_id):
        cursor = conn.cursor()
        cursor.execute('SELECT account_balance FROM accounts WHERE id = %s', (account_id,))
        return cursor.fetchone()

    @staticmethod
    def overall_balance(user_id):
        cursor = conn.cursor()
        cursor.execute('SELECT current_balance FROM users WHERE telegram_id = %s', (user_id,))
        return cursor.fetchone()


class fetch:
    """
    Класс содержит методы, которые возвращают список значений из БД
    """
    @staticmethod
    def accounts(user_id):
        """
        Возвращает список всех счетов пользователя
        :param user_id:
        :return:
        """
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE user_id = %s', (user_id,))
        return cursor.fetchall()

    @staticmethod
    def accounts_by_type(user_id, account_type):
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE (user_id = %s AND type = %s)', (user_id, account_type))
        return cursor.fetchall()

    @staticmethod
    def accounts_by_status(user_id, status: bool):
        """
        Запросить список счетов пользователя с определенным статусом:
        Активный(True) или Не активный(False)
        :param user_id: Идентификатор пользователя
        :param status: True-это активные счета пользователя, False-не активные
        :return:
        """
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE (user_id = %s AND status = %s)', (user_id, status))
        return cursor.fetchall()

    @staticmethod
    def transaction_categories_by_type(type_name: str):
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transaction_categories WHERE transaction_type = '
                       '(SELECT id FROM transaction_types WHERE name = %s)', (type_name,))
        return cursor.fetchall()
