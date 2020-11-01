from aiogram.dispatcher.filters import Command
from aiogram.types import Message

from keyboards.inline.options import inline_options
from db import sql
from loader import dp


@dp.message_handler(Command('test'))
async def show_test(msg: Message):
    await msg.answer(text='Теысовое сообщение')


@dp.message_handler(Command('start'))
async def process_start(msg: Message):
    await msg.answer(text='Добро пожаловать в Finance Bot')
    user_exists = sql.is_check.user(msg.from_user.id)[0]
    if user_exists:
        await msg.answer(text=f'С возвращением {msg.from_user.first_name}.\n'
                              f'Для вызова справки введите /help')
    else:
        await msg.answer(text=f'{msg.from_user.first_name}, приятно познакомиться. \n'
                              f'Для вызова справки введите /help')
        sql.insert.user(msg.from_user.id, msg.from_user.first_name, msg.from_user.last_name)


@dp.message_handler(Command('help'))
async def show_help_message(msg: Message):
    # TODO Придумать текст сообщения
    #  вынести сообщение в отдельный файл
    await msg.answer(text='help')


@dp.message_handler(Command('options'))
async def show_options(msg: Message):
    """
    Открыть опции бота.
    Если пользователя не существует в БД, то сначала добавляется пользователь, а потом открывается список опций
    :param msg:
    :return:
    """

    # Проверка существует ли пользователь в БД
    if not sql.is_check.user(msg.from_user.id)[0]:
        sql.insert.user(msg.from_user.id, msg.from_user.first_name, msg.from_user.last_name)

    await msg.answer(text='General options',
                     reply_markup=inline_options,
                     parse_mode='HTML')
