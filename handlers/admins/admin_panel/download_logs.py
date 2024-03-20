import os

from aiogram import Router, Bot, F, types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import FSInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filters import PrivateChatFilter, AdminFilter

router = Router(name='download_logs')


class Server_log(CallbackData, prefix='srv_log'):
    data: str
    clear_server_logs: str


class Pagination_logs(CallbackData, prefix="pag_logs"):
    action: str
    page: int


def get_server_logs() -> list:
    """
    Получение всех лог-файлов.
    Returns:
        list: Список имен файлов в директории
    """
    logs_dir = 'logs/server'
    return os.listdir(logs_dir)


async def paginator_download_logs(page: int = 0) -> InlineKeyboardMarkup:
    """
    Generates a paginated inline keyboard markup for displaying and navigating through server logs.

    Args:
        page (int, optional): The page number. Defaults to 0.

    Returns:
        InlineKeyboardMarkup: The paginated inline keyboard markup.
    """
    logs_server = get_server_logs()
    builder = InlineKeyboardBuilder()
    limit = 5
    start_offset = (page - 1) * limit
    total_pages = -(-len(logs_server) // limit)
    end_offset = start_offset + limit
    for logs in logs_server[start_offset:end_offset]:
        builder.row(
            InlineKeyboardButton(text=f'👤 {logs} ',
                                 callback_data=Server_log(data=logs, clear_server_logs=logs).pack())
        )
    buttons_row = []
    if page > 1:
        buttons_row.append(
            InlineKeyboardButton(text="⬅️", callback_data=Pagination_logs(action="prev", page=page - 1).pack()))
    buttons_row.append(InlineKeyboardButton(text=f'{page} / {total_pages}', callback_data='total_page'))
    if end_offset < len(logs_server):
        buttons_row.append(
            InlineKeyboardButton(text="➡️", callback_data=Pagination_logs(action="next", page=page + 1).pack()))
    else:
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=Pagination_logs(action="next",
                                                                                         page=1).pack()))
    builder.row(*buttons_row)
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='logs'))
    return builder.as_markup()


@router.callback_query(F.data.startswith("download_server_logs"), PrivateChatFilter(), AdminFilter())
async def download_logs(call: CallbackQuery) -> None:
    """
    Handles the callback query to display the server logs and options for downloading the logs.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
    """
    await call.answer(cache_time=1)
    # Отображаем клавиатуру с пользователями и кнопками для перелистывания
    await call.message.edit_text('Выберите лог для того чтобы скачать: ', reply_markup=await paginator_download_logs(page=1))


@router.callback_query(Pagination_logs.filter(), PrivateChatFilter())
async def pagination_handler(call: CallbackQuery, callback_data: Pagination_logs) -> None:
    """
    Handles the pagination of server logs when "next" or "prev" buttons are clicked.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
        callback_data (Pagination_logs): The parsed callback data representing the pagination action.
    """
    page = callback_data.page
    # После того как была нажата кнопка "next" или "prev", обновляем клавиатуру
    await call.message.edit_reply_markup(reply_markup=await Pagination_logs(page=page))


@router.callback_query(Server_log.filter(F.data), PrivateChatFilter())
async def get_unban(call: CallbackQuery, callback_data: Server_log, bot: Bot) -> None:
    """
    Sends the server log file as a document upon callback query action.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
        callback_data (Server_log): The parsed callback data representing the server log to download.
        bot (Bot): The Bot object used for sending the document.
    """
    await call.answer()
    logs_file = FSInputFile(f'logs/server/{callback_data.data}')
    await bot.send_document(call.message.chat.id, logs_file)


# Скачивание лога админом
@router.callback_query(F.data.startswith("download_logs"), PrivateChatFilter(), AdminFilter())
async def download_logs(call: CallbackQuery, bot: Bot) -> None:
    """
    Handles the callback query to send the chat log file as a document to the admin.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
        bot (Bot): The Bot object used for sending the document.
    """
    await call.answer(cache_time=1)
    logs_file = FSInputFile('chat_logs.txt')
    await bot.send_document(call.message.chat.id, logs_file)



