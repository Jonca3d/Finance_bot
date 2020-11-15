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
from handlers.service import database
from db import sql
from loader import dp


class Transaction_states(StatesGroup):
    transaction_amount = State()
    transfer_amount = State()


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
    await state.update_data(transaction_type=transaction_type)
    inline_transaction_type_btn = InlineKeyboardMarkup()
    for transaction_category in sql.fetch.transaction_categories_by_type(f'{transaction_type}'):
        inline_transaction_type_btn.add(InlineKeyboardButton(text=f'{transaction_category[1]}',
                                                             callback_data=f'trans_category'
                                                                           f':{transaction_category[0]}'
                                                                           f':{transaction_category[1]}'
                                                                           f''))
    inline_transaction_type_btn.add(InlineKeyboardButton(text='Отмена', callback_data='cancel_menu'))
    await call.message.answer(text='Выберите категорию', reply_markup=inline_transaction_type_btn)
    

@dp.callback_query_handler(text_contains='trans_category:')
async def process_transaction_category(call: CallbackQuery, state: FSMContext):
    transaction_category = call.data.split(':')[1]
    await state.update_data(transaction_category=transaction_category)
    await state.update_data(transaction_category_name=call.data.split(':')[2])
    await call.message.edit_reply_markup(reply_markup=None)
    inline_account_list_btn = InlineKeyboardMarkup()
    for transaction_account in sql.fetch.accounts_by_status(call.from_user.id, True):
        inline_account_list_btn.add(InlineKeyboardButton(text=f'{transaction_account[1]}',
                                                         callback_data=f'trans_account'
                                                                       f':{transaction_account[0]}'
                                                                       # f':{transaction_account[1]}'
                                                                       f''))
    await call.message.answer(text='Выберите счет', reply_markup=inline_account_list_btn)


@dp.callback_query_handler(text_contains='trans_account:')
async def process_transaction_amount(call: CallbackQuery, state: FSMContext):
    transaction_account = call.data.split(':')[1]
    await state.update_data(transaction_account=transaction_account)
    # await state.update_data(transaction_account_name=call.data.split(':')[2])
    await state.update_data(transaction_account_name=sql.get.account_name(transaction_account))

    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text='Введите сумму')
    await Transaction_states.transaction_amount.set()


@dp.message_handler(state=Transaction_states.transaction_amount, content_types=types.ContentType.TEXT)
async def process_transaction_final(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(amount=msg.text)

        transaction_data = await state.get_data()
        amount = transaction_data['amount']
        if transaction_data['transaction_type'] == 'spending_of_money':
            amount = int(amount) * -1
        # sql.insert.transaction(msg.from_user.id,
        #                        transaction_data['transaction_category'],
        #                        amount,
        #                        int(time.time()))
        await msg.answer(text='Запись добавлена\n'
                              f'Счет: {transaction_data["transaction_account_name"]}\n'
                              f'{transaction_data["transaction_category_name"]}: '
                              f'{transaction_data["amount"]}')
        database.add_data.transaction(msg.from_user.id,
                                      transaction_data['transaction_account'],
                                      transaction_data['transaction_category'],
                                      amount,
                                      int(time.time()))
        await state.finish()
    else:
        await msg.answer(text='Некорректнный ввод')
        return
# TODO завершить диалог для совершения Транзакции


@dp.callback_query_handler(text_contains='transfer_between_accounts')
async def transfer_between_accounts(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    accounts_list = sql.fetch.accounts_by_status(call.from_user.id, True)

    inline_accounts_list_btn = InlineKeyboardMarkup()
    for account in accounts_list:
        inline_accounts_list_btn.add(InlineKeyboardButton(text=f'{account[1]}',
                                                          callback_data=f'transfer_from:{account[0]}'))
    await call.message.answer(text='Выберите счет с которого хотите перенести средства',
                              reply_markup=inline_accounts_list_btn)


@dp.callback_query_handler(text_contains='transfer_from:')
async def transfer_from(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    from_account = call.data.split(':')[1]
    await state.update_data(from_account=from_account)
    accounts_list = database.get_data.accounts_list(call.from_user.id, exclude_accounts=[int(from_account)])

    inline_accounts_list_btn = InlineKeyboardMarkup()
    for account in accounts_list:
        inline_accounts_list_btn.add(InlineKeyboardButton(text=f'{account[1]}',
                                                          callback_data=f'transfer_in:{account[0]}:'))

    await call.message.answer(text='Выбкрите куда вы хотите перевести стредства',
                              reply_markup=inline_accounts_list_btn)


@dp.callback_query_handler(text_contains='transfer_in:')
async def transfer_in(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    to_account = call.data.split(':')[1]
    await state.update_data(to_account=to_account)
    await Transaction_states.transfer_amount.set()
    await call.message.answer(text='Введите сумму перевода')


@dp.message_handler(state=Transaction_states.transfer_amount, content_types=types.ContentType.TEXT)
async def transfer_amount(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        transfer_data = await state.get_data()
        database.transfer.money_transfer(msg.from_user.id,
                                         transfer_data['to_account'],
                                         transfer_data['from_account'],
                                         int(msg.text),
                                         int(time.time()))
        await state.finish()
        await msg.answer('Перевод успешно завершен')
    else:
        await msg.answer('Введите корректную сумму')
        return

