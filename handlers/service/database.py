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
    def account(user_id, balance, time_stamp):
        sql.update.overall_balance(user_id, balance)
        new_balance = sql.get.overall_balance(user_id)[0]
        sql.insert.balance_history_record(user_id, new_balance, time_stamp)


class transfer:

    @staticmethod
    def money_transfer(user_id, to_account_id, from_account_id, amount, time_stamp):
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
