from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Основное меню
inline_options = InlineKeyboardMarkup()

inline_show_accounts = InlineKeyboardButton('Просмотреть список счетов', callback_data='show_accounts_list')


inline_options.add(inline_show_accounts)

