from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import (CallbackQuery,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           ReplyKeyboardMarkup,
                           Message,
                           ReplyKeyboardRemove)
from db import sql
from loader import dp


class State_add_account(StatesGroup):
    are_you_wont_to_subscribe = State()
    what_is_account_title = State()
    what_is_account_type = State()
    what_is_the_balance_on_the_account = State()
    do_you_want_add_description = State()
    description = State()


class State_edit_account(StatesGroup):
    edit_name = State()
    edit_description = State()
    delete_entry = State()
    to_which_account_to_transfer_the_balance_of_money = State()


@dp.callback_query_handler(text_contains='show_accounts_list')
async def process_show_accounts_list(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    inline_accounts_list = InlineKeyboardMarkup()

    for account in sql.fetch.accounts(call.from_user.id):
        inline_accounts_list.add(InlineKeyboardButton(text=f'{account[1]}',
                                                      callback_data=f'accounts_list:{account[0]}'))

    inline_accounts_list.add(InlineKeyboardButton(text='Добавить новый счет', callback_data='add_new_account'))
    inline_accounts_list.insert(InlineKeyboardButton(text='Отмена', callback_data='cancel_menu'))

    await call.message.answer(text='Список счетов', reply_markup=inline_accounts_list)


# ##########################################################
# Добавление нового счета
# ##########################################################
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
        await state.update_data(user_id=msg.from_user.id)
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
        await state.update_data(account_type=sql.get.account_type('debit')[0])
        await msg.answer('Остаток на счете', reply_markup=ReplyKeyboardRemove())
        await State_add_account.what_is_the_balance_on_the_account.set()
    elif msg.text.lower() == 'кредитный':
        await state.update_data(account_type=sql.get.account_type('credit')[0])
        await msg.answer('Размер задолжности', reply_markup=ReplyKeyboardRemove())
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
        sql.insert.account(account_data['user_id'],
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
    sql.insert.account(account_data['user_id'],
                       account_data['title'],
                       account_data['account_balance'],
                       account_data['account_type'],
                       account_data['description'])
    await msg.answer('Новый счет успешно добавлен')
    await state.finish()


# #########################################################
# Редактирование информации о счете
# #########################################################
@dp.callback_query_handler(text_contains='accounts_list:')
async def process_edit_account(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    account_id = call.data.split(':')[1]

    inline_account_options_btn = InlineKeyboardMarkup()
    inline_account_options_btn.add(InlineKeyboardButton(text='Изменить название',
                                                        callback_data=f'edit_account_name:{account_id}'))
    inline_account_options_btn.add(InlineKeyboardButton(text='Изменить описание',
                                                        callback_data=f'edit_account_description:{account_id}'))
    inline_account_options_btn.add(InlineKeyboardButton(text='Удалить',
                                                        callback_data=f'remove_account:{account_id}'))
    inline_account_options_btn.add(InlineKeyboardButton(text='Отмена',
                                                        callback_data='cancel_menu'))

    account = sql.get.account(account_id)
    await call.message.answer(text=f'Название: {account[1]}\n'
                                   f'Бананс: {account[4]}\n'
                                   f'Описание: {account[3]}',
                              reply_markup=inline_account_options_btn)


# Редактирование названия счета
@dp.callback_query_handler(text_contains='edit_account_name:')
async def process_edit_account_name(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text='Введите новое название для счёта')
    await state.update_data(account_id=call.data.split(':')[1])
    await State_edit_account.edit_name.set()


@dp.message_handler(state=State_edit_account.edit_name, content_types=types.ContentType.TEXT)
async def process_set_new_name_of_account(msg: Message, state: FSMContext):
    await state.update_data(new_name=msg.text)
    new_data = await state.get_data()
    sql.update.account_name(new_data['account_id'], new_data['new_name'])
    await state.finish()
    await msg.answer(text='Название успешно изменено')


# Редактирование описаня счета
@dp.callback_query_handler(text_contains='edit_account_description:')
async def process_edit_account_description(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text='Введите новое описание для счёта')
    await state.update_data(account_id=call.data.split(':')[1])
    await State_edit_account.edit_description.set()


@dp.message_handler(state=State_edit_account.edit_description, content_types=types.ContentType.TEXT)
async def process_set_new_name_of_account(msg: Message, state: FSMContext):
    await state.update_data(new_description=msg.text)
    new_data = await state.get_data()
    sql.update.account_description(new_data['account_id'], new_data['new_description'])
    await state.finish()
    await msg.answer(text='Описание успешно изменено')


# Удаление счета
@dp.callback_query_handler(text_contains='remove_account:')
async def process_remove_account(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    # account_id = call.data.split(':')[1]
    account = sql.get.account(call.data.split(':')[1])
    # print(account)
    await state.update_data(account_id=account[0])
    await state.update_data(account_balance=account[4])
    await state.update_data(account_type=account[5])

    # TODO Вынести клавиатуру с ДА НЕТ в файл с клавиатурами
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Да')
    keyboard.add('Нет')

    await call.message.answer(text='Вы действительно хотите удалить этот счёт?', reply_markup=keyboard)

    await State_edit_account.delete_entry.set()


@dp.message_handler(state=State_edit_account.delete_entry, content_types=types.ContentType.TEXT)
async def process_do_you_want_to_delete_the_account(msg: Message, state: FSMContext):
    data = await state.get_data()
    if msg.text.lower() == 'да':
        if int(data['account_balance']) == 0:
            sql.update.account_status(data['account_id'], False)
            await msg.answer('Счет успешно удален', reply_markup=ReplyKeyboardRemove())
            await state.finish()
        else:
            inline_accounts_btn = InlineKeyboardMarkup()
            print("type: " + str(data['account_type']))
            for account in sql.fetch.accounts_by_type(msg.from_user.id, data['account_type']):
                if account[0] != data['account_id']:
                    inline_accounts_btn.add(InlineKeyboardButton(text=f'{account[1]}',
                                                                 callback_data=f'to_which_account_to_transfer:{account[0]}'))
            inline_accounts_btn.add(InlineKeyboardButton(text='Просто удалить всю сумму',
                                                         callback_data=f'to_which_account_to_transfer:0'))
            inline_accounts_btn.add(InlineKeyboardButton(text='Отмена', callback_data='cancel_menu'))
            # TODO вставить осознанный текст в ответ
            await msg.answer(text='qwe', reply_markup=ReplyKeyboardRemove())
            await msg.answer(text='На какой счет вы хотите перенести остаток?',
                             reply_markup=inline_accounts_btn)
            await state.finish()
    elif msg.text.lower() == 'нет':
        await msg.answer(text='Отмена', reply_markup=ReplyKeyboardRemove())
        await state.finish()
    else:
        await msg.answer(text='Нажмите да или нет')
        return
