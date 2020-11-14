from db import sql


class add_data:

    @staticmethod
    def transaction(user_id, account_id, transaction_category, amount, time_stamp):
        sql.insert.transaction(user_id, transaction_category, amount, time_stamp)
        sql.update.account_balance(account_id, amount)
        sql.update.overall_balance(user_id, amount)
        new_balance = sql.get.overall_balance(user_id)[0]
        sql.insert.balance_history_record(user_id, new_balance, time_stamp)

    @staticmethod
    def account(user_id, acc_data, time_stamp):
        """
        Добавляет новый счет
        :param user_id:
        :param acc_data: account data
        :param time_stamp:
        :return:
        """
        balance = int(acc_data['account_balance'])
        if acc_data['account_type'] == 2:
            balance = int(balance)*-1

        description = ''
        if 'description' in acc_data:
            description = acc_data['description']

        sql.insert.account(acc_data['user_id'],
                           acc_data['title'],
                           balance,
                           acc_data['account_type'],
                           description)
        sql.update.overall_balance(user_id, balance)
        new_balance = sql.get.overall_balance(user_id)[0]
        sql.insert.balance_history_record(user_id, new_balance, time_stamp)


class transfer:

    @staticmethod
    def money_transfer(user_id, to_account_id, from_account_id, amount, time_stamp):
        # TODO Исправить параметр transaction)category in insert.transaction
        sql.insert.transaction(user_id, 3, amount, time_stamp)
        sql.update.account_balance(to_account_id, amount)
        sql.update.account_balance(from_account_id, int(amount) * -1)

    @staticmethod
    def all_money_and_remove_account(user_id, to_account_id, from_account_id, time_stamp):
        from_account_balance = sql.get.account_balance(from_account_id)[0]
        sql.insert.transaction(user_id, 3, from_account_balance, time_stamp)
        sql.update.account_balance(to_account_id, from_account_balance)
        sql.update.account_balance(from_account_id, int(from_account_balance)*-1)
        sql.update.account_status(from_account_id, False)


class delete:

    @staticmethod
    def account(user_id, account_id, time_stamp):
        account_balance = sql.get.account_balance(account_id)[0]
        sql.update.account_balance(account_id, int(account_balance)*-1)
        sql.update.overall_balance(user_id, int(account_balance)*-1)
        new_balance = sql.get.overall_balance(user_id)
        sql.insert.balance_history_record(user_id, new_balance, time_stamp)
        sql.update.account_status(account_id, False)


class get_info:

    @staticmethod
    def all_accounts_balance(user_id: int):
        overall_balance = sql.get.overall_balance(user_id)[0]
        info_message = f'Общий баланс: {overall_balance}\n============================'

        for account in sql.fetch.accounts_by_status(user_id, True):
            info_message += f'\n{account[1]}: {account[4]}'

        return info_message


class get_data:

    @staticmethod
    def accounts_list(user_id, only_active=True, exclude_accounts=[]):
        """
        Возвращает список счетов пользователя
        :param user_id:
        :param only_active: Если True, то возвращает только активные счета
        :param exclude_accounts: Принимает список с ID счетов для исключения их из результирующего списка
        :return:
        """
        accounts_list: list
        if only_active:
            accounts_list = sql.fetch.accounts_by_status(user_id, True)
        else:
            accounts_list = sql.fetch.accounts(user_id)
        # TODO Придумать более изящный способ убрать из выборки ненужные счета
        if len(exclude_accounts) == 0:
            return accounts_list
        else:
            acc_list = []
            for account in accounts_list:
                if account[0] in exclude_accounts:
                    continue
                else:
                    acc_list.append(account)
            return acc_list


class service:

    @staticmethod
    def add_user_if_doesnt_exists(user_data, time_stamp):
        if not sql.is_check.user(user_data.id)[0]:
            sql.insert.user(user_data.id, user_data.first_name, user_data.last_name, time_stamp)
