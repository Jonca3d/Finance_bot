from aiogram.dispatcher.filters import Command
from aiogram.types import Message
from loader import dp


@dp.message_handler(Command('test'))
async def show_test(msg: Message):
    await msg.answer(text='Теысовое сообщение')


@dp.message_handler(Command('start'))
async def process_start(msg: Message):
    await msg.answer(text='Добро пожаловать в Finance Bot')
