from aiogram.filters import Command

from filters import PrivateChatFilter, AdminFilter
from keyboards.admins.kb_menu import kb_panel, kb_notice, kb_logs, kb_users_menu

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

router = Router(name='panels')


# ГЛАВНАЯ ПАНЕЛЬ АДМИНА
@router.message(Command('panelodm'), PrivateChatFilter(), AdminFilter())
async def main_panel(message: Message) -> None:
    """
    Displays the main admin panel menu upon receiving the /panelodm command in a private chat.

    Args:
        message (Message): The Message object representing the user's message.
    """
    await message.answer(
        f'✋ Привет @<b><a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a></b>! \n\n'
        f'<b>👮🏼‍♂️Меню Админ Панели</b>\n', reply_markup=kb_panel.as_markup())


@router.callback_query(F.data.startswith("notices"), PrivateChatFilter(), AdminFilter())
async def notices_all(call: CallbackQuery) -> None:
    """
    Handles the callback query to display notices in the admin panel.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
    """
    await call.answer(cache_time=1)
    await call.message.edit_reply_markup(reply_markup=kb_notice.as_markup())


@router.callback_query(F.data.startswith("logs"), PrivateChatFilter(), AdminFilter())
async def logs_all(call: CallbackQuery) -> None:
    """
    Handles the callback query to display logs in the admin panel.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
    """
    await call.answer(cache_time=1)
    await call.message.edit_reply_markup(reply_markup=kb_logs.as_markup())


@router.callback_query(F.data.startswith("cancel"), PrivateChatFilter())
async def get_cancel(call: CallbackQuery) -> None:
    """
    Handles the callback query to cancel the current action and display the main admin panel menu.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
    """
    await call.answer(cache_time=1)
    await call.message.edit_text('<b>👮🏼‍♂️Меню Админ Панели</b>', reply_markup=kb_panel.as_markup())


@router.callback_query(F.data.startswith("edit"), PrivateChatFilter(), AdminFilter())
async def get_user(call: CallbackQuery) -> None:
    """
    Handles the callback query to get user data in the admin panel.

    Args:
        call (CallbackQuery): The CallbackQuery object representing the callback.
    """
    await call.answer(cache_time=1)
    await call.message.edit_reply_markup(reply_markup=kb_users_menu.as_markup())
