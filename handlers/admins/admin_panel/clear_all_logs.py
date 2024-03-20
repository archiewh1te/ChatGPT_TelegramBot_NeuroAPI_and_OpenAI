from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filters import PrivateChatFilter, AdminFilter
from handlers.admins.admin_panel.download_logs import Pagination_logs, get_server_logs

router = Router(name='clear_logs')


class Server_log_clear(CallbackData, prefix='srv_log'):
    clear_server_logs: str


async def paginator_clear_logs(page: int = 0) -> InlineKeyboardMarkup:
    """
    Generates a paginated inline keyboard markup for displaying server logs.

    Args:
        page (int, optional): The page number. Defaults to 0.

    Returns:
        InlineKeyboardMarkup: The paginated inline keyboard markup.
    """
    log_server = get_server_logs()
    builder = InlineKeyboardBuilder()
    limit = 5
    start_offset = (page - 1) * limit
    total_pages = -(-len(log_server) // limit)
    end_offset = start_offset + limit
    for logs in log_server[start_offset:end_offset]:
        builder.row(
            InlineKeyboardButton(text=f'👤 {logs} ',
                                 callback_data=Server_log_clear(clear_server_logs=logs).pack())
        )
    buttons_row = []
    if page > 1:
        buttons_row.append(
            InlineKeyboardButton(text="⬅️", callback_data=Pagination_logs(action="prev", page=page - 1).pack()))
    buttons_row.append(InlineKeyboardButton(text=f'{page} / {total_pages}', callback_data='total_page'))
    if end_offset < len(log_server):
        buttons_row.append(
            InlineKeyboardButton(text="➡️", callback_data=Pagination_logs(action="next", page=page + 1).pack()))
    else:
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=Pagination_logs(action="next",
                                                                                         page=1).pack()))
    builder.row(*buttons_row)
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='logs'))
    return builder.as_markup()


# Очистка файла лога чата
@router.callback_query(F.data.startswith("logs_clear"), PrivateChatFilter(), AdminFilter())
async def clear_chat_logs(call: CallbackQuery) -> None:
    """
    Handles the callback query to clear the chat logs file.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
    """
    await call.answer(cache_time=1)
    logs_file = open('chat_logs.txt', 'w')
    logs_file.close()
    await call.message.answer(f'✅Файл логов успешно очищен!')


# Очистка файла системного лога
@router.callback_query(F.data.startswith("server_logs_clear"), PrivateChatFilter(), AdminFilter())
async def clear_server_logs(call: CallbackQuery) -> None:
    """
    Handles the callback query to display a list of server logs and pagination buttons for clearing the logs.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
    """
    await call.answer(cache_time=1)
    # Отображаем клавиатуру с пользователями и кнопками для перелистывания
    await call.message.edit_text('Выберите лог для того чтобы очистить: ', reply_markup=await paginator_clear_logs(page=1))


@router.callback_query(Pagination_logs.filter(), PrivateChatFilter())
async def pagination_handler(call: CallbackQuery, callback_data: Pagination_logs) -> None:
    """
    Handles the callback query to update the pagination of the server log list for clearing the logs.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
        callback_data (Pagination_logs): The parsed callback data.
    """
    page = callback_data.page
    # После того как была нажата кнопка "next" или "prev", обновляем клавиатуру
    await call.message.edit_reply_markup(reply_markup=await Pagination_logs(page=page))


@router.callback_query(Server_log_clear.filter(F.clear_server_logs), PrivateChatFilter())
async def get_unban(call: CallbackQuery, callback_data: Server_log_clear) -> None:
    """
    Handles the callback query to clear a specific server log file and display the result.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
        callback_data (Server_log_clear): The parsed callback data representing the server log file to clear.
    """
    await call.answer()
    logs_file = open(f'logs/server/{callback_data.clear_server_logs}', 'w')
    logs_file.close()
    await call.message.answer(f'✅Файл <b>{callback_data.clear_server_logs}</b> системных логов успешно очищен!')
