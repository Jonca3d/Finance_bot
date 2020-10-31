import asyncio


if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp
    from db.init_db import init_db_tables, init_db_basic_data
    init_db_tables()
    init_db_basic_data()
    loop = asyncio.get_event_loop()
    executor.start_polling(dp, loop=loop)
