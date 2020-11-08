import time

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import (CallbackQuery,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           ReplyKeyboardMarkup,
                           Message,
                           ReplyKeyboardRemove)
from db import sql
from loader import dp


class Transaction_states(StatesGroup):
    transaction_amount = State()


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
    inline_transaction_btn = InlineKeyboardMarkup()
    inline_transaction_btn.add(InlineKeyboardButton(text='Приход', callback_data='transaction:arrival_of_money'))
    inline_transaction_btn.add(InlineKeyboardButton(text='Расход', callback_data='transaction:spending_of_money'))
    inline_transaction_btn.add(InlineKeyboardButton(text='Перевод между счетами',
                                                    callback_data='transaction:transfer_between_accounts'))
    await msg.answer(text='Выберите тип транзакции', reply_markup=inline_transaction_btn)


# TODO написать хэндлер для операции перемещения средств между счетами

@dp.callback_query_handler(text_contains='transaction:')
async def process_transaction(call: CallbackQuery, state: FSMContext):
    """
    В этом хэндлере, в зависимости от того какой тип транцакции мы выбрали,
    выходит список категорий для расхода или поступления денег
    :param call:
    :param state:
    :return:
    """
    await call.message.edit_reply_markup(reply_markup=None)
    transaction_type = call.data.split(':')[1]
    inline_transaction_category_btn = InlineKeyboardMarkup()
    for transaction_category in sql.fetch.transaction_categories_by_type(f'{transaction_type}'):
        inline_transaction_category_btn.add(InlineKeyboardButton(text=f'{transaction_category[1]}',
                                                                 callback_data=f'trans_category'
                                                                               f':{transaction_category[0]}'
                                                                               f':{transaction_category[1]}'
                                                                               f''))
        print(transaction_category)
    inline_transaction_category_btn.add(InlineKeyboardButton(text='Отмена', callback_data='cancel_menu'))
    await call.message.answer(text='Выберите категорию', reply_markup=inline_transaction_category_btn)


@dp.callback_query_handler(text_contains='trans_category:')
async def process_transaction_amount(call: CallbackQuery, state: FSMContext):
    transaction_category = call.data.split(':')[1]
    await state.update_data(transaction_category=transaction_category)
    await state.update_data(transaction_category_name=call.data.split(':')[2])
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text='Введите сумму')
    await Transaction_states.transaction_amount.set()


@dp.message_handler(state=Transaction_states.transaction_amount, content_types=types.ContentType.TEXT)
async def process_transaction_final(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(amount=msg.text)

    transaction_data = await state.get_data()
    print(transaction_data)
    sql.insert.transaction(msg.from_user.id,
                           transaction_data['transaction_category'],
                           transaction_data['amount'],
                           int(time.time()))
    await msg.answer(text='Запись добавлена\n'
                          f'{transaction_data["transaction_category_name"]}: '
                          f'{transaction_data["amount"]}')
    await state.finish()
# TODO завершить диалог для совершения Транзакции
