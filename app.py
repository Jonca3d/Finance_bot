import asyncio


if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    loop = asyncio.get_event_loop()
    executor.start_polling(dp, loop=loop)
