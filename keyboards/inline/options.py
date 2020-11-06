from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Основное меню
inline_options = InlineKeyboardMarkup()

inline_show_accounts = InlineKeyboardButton('Просмотреть список счетов', callback_data='show_accounts_list')
inline_cancel = InlineKeyboardButton('Отмена', callback_data='cancel_menu')


inline_options.add(inline_show_accounts)
inline_options.add(inline_cancel)

