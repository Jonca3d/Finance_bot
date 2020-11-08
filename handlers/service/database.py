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
