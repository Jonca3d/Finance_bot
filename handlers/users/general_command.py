import time

from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from handlers.service import database
from keyboards.inline.options import inline_options
from db import sql
from loader import dp


@dp.message_handler(Command('test'))
async def show_test(msg: Message):
    await msg.answer(text='Тестовое сообщение')
    test = database.get_data.accounts_list(msg.from_user.id, only_active=False, exclude_accounts=[2,1])
    mess = ''
    for i in test:
        mess += str(i) + '\n'
    await msg.answer(mess)


@dp.message_handler(Command('start'))
async def process_start(msg: Message):
    await msg.answer(text=f'Добро пожаловать в Finance Bot {msg.from_user.first_name}.'
                          f'\nДля вызова справки введите /help')
    database.service.add_user_if_doesnt_exists(msg.from_user, int(time.time()))


@dp.message_handler(Command('help'))
async def show_help_message(msg: Message):
    await msg.answer(text='Введите /transaction для добавления новой транзакции\n'
                          'Введите /options для открытия опций\n'
                          'Введите /info для просмотра информации по счетам и общему балансу\n'
                          '/help для вызова этой справки')


@dp.message_handler(Command('options'))
async def show_options(msg: Message):
    database.service.add_user_if_doesnt_exists(msg.from_user, int(time.time()))
    await msg.answer(text='General options', reply_markup=inline_options, parse_mode='HTML')


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
    database.service.add_user_if_doesnt_exists(msg.from_user, int(time.time()))

    if sql.is_check.account(msg.from_user.id)[0]:
        inline_transaction_btn = InlineKeyboardMarkup()
        inline_transaction_btn.add(InlineKeyboardButton(text='Приход', callback_data='transaction:arrival_of_money'))
        inline_transaction_btn.add(InlineKeyboardButton(text='Расход', callback_data='transaction:spending_of_money'))
        inline_transaction_btn.add(InlineKeyboardButton(text='Перевод между счетами',
                                                        callback_data='transfer_between_accounts'))
        inline_transaction_btn.add(InlineKeyboardButton(text='Отмена', callback_data='cancel_menu'))
        await msg.answer(text='Выберите тип транзакции', reply_markup=inline_transaction_btn)
    else:
        await msg.answer(text='У вас пока нет ни одного счета. Введите /options и добавте хотябы один счет')


@dp.message_handler(Command('info'))
async def show_info_about_accounts(msg: Message):
    database.service.add_user_if_doesnt_exists(msg.from_user, int(time.time()))
    await msg.answer(database.get_info.all_accounts_balance(msg.from_user.id))


@dp.callback_query_handler(text_contains='cancel_menu')
async def process_cancel_menu(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
