from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Кнопки при старте
kb_user_main = InlineKeyboardBuilder()
kb_user_main.row(types.InlineKeyboardButton(text='👤 Профиль', callback_data='userprofile'),
                 types.InlineKeyboardButton(text='🤖 Сменить модель GPT', callback_data='gptmodel'),
                 types.InlineKeyboardButton(text='❔ Помощь', callback_data='userhelp'),
                 types.InlineKeyboardButton(text='❓ FAQ', callback_data='userfaq'),
                 types.InlineKeyboardButton(text='✉️ Написать в support', callback_data='support'),
                 width=1
                 )

# Кнопка назад
kb_back = InlineKeyboardBuilder()
kb_back.row(types.InlineKeyboardButton(text='⬅ Назад ', callback_data='back'), width=1)


