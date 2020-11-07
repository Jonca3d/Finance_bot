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
    inline_transaction_btn = InlineKeyboardMarkup()
    inline_transaction_btn.add(InlineKeyboardButton(text='Приход', callback_data='transaction:arrival_of_money'))
    inline_transaction_btn.add(InlineKeyboardButton(text='Расход', callback_data='transaction:spending_of_money'))
    inline_transaction_btn.add(InlineKeyboardButton(text='Перевод между счетами',
                                                    callback_data='transaction:transfer_between_accounts'))
    await msg.answer(text='Выберите тип транзакции', reply_markup=inline_transaction_btn)


@dp.callback_query_handler(text_contains='transaction:')
async def process_transaction(call: CallbackQuery, state: FSMContext):

    await call.message.edit_reply_markup(reply_markup=None)
    transaction_type = call.data.split(':')[1]
    await state.update_data(transaction_type=transaction_type)
    inline_transaction_category_btn = InlineKeyboardMarkup()
    inline_transaction_category_btn.add(InlineKeyboardButton(text='test btn', callback_data='test_btn'))
    for transaction_category in sql.fetch.transaction_categories_by_type(f'{transaction_type}'):
        inline_transaction_category_btn.add(InlineKeyboardButton(text=f'{transaction_category[1]}',
                                                                 callback_data=f'trans_category:{transaction_category[1]}'))
    inline_transaction_category_btn.add(InlineKeyboardButton(text='Отмена', callback_data='cancel_menu'))
    await call.message.answer(text='Выберите категорию', reply_markup=inline_transaction_category_btn)


@dp.callback_query_handler(text_contains='trans_category:')
async def process_transaction_amount(call: CallbackQuery, state: FSMContext):
    transaction_category = call.data.split(':')[1]
    await state.update_data(transaction_category=transaction_category)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text='Введите сумму')
    await Transaction_states.transaction_amount.set()


@dp.message_handler(state=Transaction_states.transaction_amount, content_types=types.ContentType.TEXT)
async def process_transaction_final(msg: Message, state: FSMContext)
    transaction_data = state.get_data()
    transaction_amount: int
    if msg.text.isdigit():
        transaction_amount = int(msg.text)
# TODO завершить диалог для совершения Транзакции