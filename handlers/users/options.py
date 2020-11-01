from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, Message, \
    ReplyKeyboardRemove
from db import sql
from loader import dp


class State_add_account(StatesGroup):
    are_you_wont_to_subscribe = State()
    what_is_account_title = State()
    what_is_account_type = State()
    what_is_the_balance_on_the_account = State()
    do_you_want_add_description = State()
    description = State()


@dp.callback_query_handler(text_contains='show_accounts_list')
async def process_show_accounts_list(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    inline_accounts_list = InlineKeyboardMarkup()

    inline_accounts_list.add(InlineKeyboardButton(text='Добавить новый счет', callback_data='add_new_account'))

    await call.message.answer(text='Список счетов', reply_markup=inline_accounts_list)


@dp.callback_query_handler(text_contains='add_new_account')
async def process_add_new_account(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Да')
    keyboard.add('Нет')
    await call.message.answer(text='Вы хотите добавить новый счёт?', reply_markup=keyboard)
    await State_add_account.are_you_wont_to_subscribe.set()


@dp.message_handler(state=State_add_account.are_you_wont_to_subscribe, content_types=types.ContentType.TEXT)
async def process_are_you_wont_to_subscribe(msg: Message, state: FSMContext):
    if msg.text.lower() == 'да':
        await state.update_data(user=msg.from_user.id)
        await msg.answer('Введите название счета', reply_markup=ReplyKeyboardRemove())
        await State_add_account.what_is_account_title.set()
    elif msg.text.lower() == 'нет':
        await state.finish()
        await msg.answer('Отмена', reply_markup=ReplyKeyboardRemove())
    else:
        await msg.answer('Нажмите на кнопку ниже')
        return


@dp.message_handler(state=State_add_account.what_is_account_title, content_types=types.ContentType.TEXT)
async def process_what_is_account_title(msg: Message, state: FSMContext):
    await state.update_data(title=msg.text)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Дебетовый')
    keyboard.add('Кредитный')

    await msg.answer('Выберите тип счета', reply_markup=keyboard)
    await State_add_account.what_is_account_type.set()


@dp.message_handler(state=State_add_account.what_is_account_type, content_types=types.ContentType.TEXT)
async def process_what_is_account_type(msg: Message, state: FSMContext):
    if msg.text.lower() == 'дебетовый':
        await state.update_data(account_type='debit')
        await msg.answer('Остаток на счете', reply_markup=ReplyKeyboardRemove())
        await State_add_account.what_is_the_balance_on_the_account.set()
    elif msg.text.lower() == 'кредитный':
        await state.update_data(account_type='credit')
        await msg.answer('Остаток на счете', reply_markup=ReplyKeyboardRemove())
        await State_add_account.what_is_the_balance_on_the_account.set()
    else:
        await msg.answer('Нажмите на кнопку ниже')
        return


@dp.message_handler(state=State_add_account.what_is_the_balance_on_the_account, content_types=types.ContentType.TEXT)
async def process_what_is_the_balance_on_the_account(msg: Message, state: FSMContext):
    # TODO добавить валидацию
    #  входные данные "денежная сумма"
    await state.update_data(account_balance=msg.text)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Да')
    keyboard.add('Нет')

    await msg.answer('Добавить описание счета?', reply_markup=keyboard)
    await State_add_account.do_you_want_add_description.set()


@dp.message_handler(state=State_add_account.do_you_want_add_description, content_types=types.ContentType.TEXT)
async def process_do_you_want_add_description(msg: Message, state: FSMContext):

    if msg.text.lower() == 'да':
        await msg.answer('Введите описание счета', reply_markup=ReplyKeyboardRemove())
        await State_add_account.description.set()
    elif msg.text.lower() == 'нет':
        account_data = await state.get_data()
        sql.insert.account(account_data['user'],
                           account_data['title'],
                           account_data['account_balance'],
                           account_data['account_type'])
        await msg.answer('Новый счет успешно добавлен', reply_markup=ReplyKeyboardRemove())
    else:
        await msg.answer('Нажмите на кнопку ниже')
        return


@dp.message_handler(state=State_add_account.description, content_types=types.ContentType.TEXT)
async def process_add_description_for_new_account(msg: Message, state: FSMContext):
    await state.update_data(description=msg.text)

    account_data = await state.get_data()
    sql.insert.account(account_data['user'],
                       account_data['title'],
                       account_data['account_balance'],
                       account_data['account_type'],
                       account_data['description'])
    await msg.answer('Новый счет успешно добавлен')
