from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Кнопка главной админской панели
kb_panel = InlineKeyboardBuilder()
kb_panel.row(types.InlineKeyboardButton(text='📢 Нотисы', callback_data='notices'),
             types.InlineKeyboardButton(text='📋 Логи', callback_data='logs'),
             types.InlineKeyboardButton(text='✏️ Редактировать', callback_data='edit'),
             types.InlineKeyboardButton(text='👥 Пользователи', callback_data='users'), width=2)

# Кнопка нотисы
kb_notice = InlineKeyboardBuilder()
kb_notice.row(types.InlineKeyboardButton(text='📢 Отправить нотис всем пользователям', callback_data='notice_all_users'),
              width=1)
kb_notice.row(types.InlineKeyboardButton(text='⬅ Назад ', callback_data='cancel'), width=1)

# Кнопка логи
kb_logs = InlineKeyboardBuilder()
kb_logs.row(
    types.InlineKeyboardButton(text='🔽 Скачать логи чата', callback_data='download_logs'),
    types.InlineKeyboardButton(text='🔽 Скачать системные логи', callback_data='download_server_logs'),
    types.InlineKeyboardButton(text='🗑 Очистить логи чата', callback_data='logs_clear'),
    types.InlineKeyboardButton(text='🗑 Очистить системные логи', callback_data='server_logs_clear'), width=2)
kb_logs.row(types.InlineKeyboardButton(text='⬅ Назад ', callback_data='cancel'), width=1)

# Кнопка редактировать
kb_users_menu = InlineKeyboardBuilder()
kb_users_menu.row(
    types.InlineKeyboardButton(text='⚡️ Добавить токены', callback_data='add_attempts'),
    types.InlineKeyboardButton(text='🚫 Забанить', callback_data='bans'),
    types.InlineKeyboardButton(text='✅ Разбанить', callback_data='unbans'),
    types.InlineKeyboardButton(text='💎 Изменить подписку', callback_data='subscription'),
    types.InlineKeyboardButton(text='🤖 Добавить модель GPT', callback_data='create_model_gpt'),
    types.InlineKeyboardButton(text='🗑🤖 Удалить модель GPT', callback_data='delete_model_gpt'), width=2)
kb_users_menu.row(types.InlineKeyboardButton(text='⬅ Назад ', callback_data='cancel'), width=1)



