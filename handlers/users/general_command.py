import time

from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.options import inline_options
from db import sql
from loader import dp


@dp.message_handler(Command('test'))
async def show_test(msg: Message):
    await msg.answer(text='Тестовое сообщение')


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
        sql.insert.user(msg.from_user.id, msg.from_user.first_name, msg.from_user.last_name, int(time.time()))


@dp.message_handler(Command('help'))
async def show_help_message(msg: Message):
    await msg.answer(text='Введите /transaction для добавления новой транзакции\n'
                          'Введите /options для открытия опций\n'
                          'Введите /info для просмотра информации по счетам и общему балансу\n'
                          '/help для вызова этой справки')


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
        sql.insert.user(msg.from_user.id, msg.from_user.first_name, msg.from_user.last_name, int(time.time()))

    await msg.answer(text='General options',
                     reply_markup=inline_options,
                     parse_mode='HTML')


@dp.message_handler(Command('transaction'))
async def transaction(msg: Message):
    """
    При вызове этого хэгдлера предлагается выбрать тип транзакции:
    Приход-поступление средств
    Расход-какие либо траты
    Перевод между счетами-когда мы хотим перевести деньги с одного счета на другой
    :param msg:
    :return:
    """
    if not sql.is_check.user(msg.from_user.id)[0]:
        sql.insert.user(msg.from_user.id, msg.from_user.first_name, msg.from_user.last_name, int(time.time()))

    if sql.is_check.account(msg.from_user.id)[0]:
        inline_transaction_btn = InlineKeyboardMarkup()
        inline_transaction_btn.add(InlineKeyboardButton(text='Приход', callback_data='transaction:arrival_of_money'))
        inline_transaction_btn.add(InlineKeyboardButton(text='Расход', callback_data='transaction:spending_of_money'))
        inline_transaction_btn.add(InlineKeyboardButton(text='Перевод между счетами',
                                                        callback_data='transaction:transfer_between_accounts'))
        inline_transaction_btn.add(InlineKeyboardButton(text='Отмена', callback_data='cancel_menu'))
        await msg.answer(text='Выберите тип транзакции', reply_markup=inline_transaction_btn)
    else:
        await msg.answer(text='У вас пока нет ни одного счета. Введите /options и добавте хотябы один счет')


@dp.message_handler(Command('info'))
async def show_info_about_accounts(msg: Message):
    pass


@dp.callback_query_handler(text_contains='cancel_menu')
async def process_cancel_menu(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
