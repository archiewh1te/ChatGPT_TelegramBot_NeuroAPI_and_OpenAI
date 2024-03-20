from asyncio import sleep

from aiogram import F, Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import load_config
from database.function.user_commands import select_allusers
from filters import PrivateChatFilter, AdminFilter
from state.send_all_notice import send_notice_allusers

config = load_config('.env')

DEV_ID = config.tg_bot.dev_id

router = Router(name='notice_to_all_users')


# ---------------------------------БЛОК ОТПРАВКИ УВЕДОМЛЕНИЯ ВСЕМ ПОЛЬЗОВАТЕЛЯМ-----------------------------------------
@router.callback_query(F.data.startswith("notice_all_users"), PrivateChatFilter(), AdminFilter())
async def start_send_notice(call: CallbackQuery, state: FSMContext) -> None:
    """
    Handles the start of sending a notice to all users.

    :param call: The CallbackQuery object representing the callback.
    :type call: aiogram.types.CallbackQuery
    :param state: The FSMContext object to manage bot states.
    :type state: aiogram.fsm.context.FSMContext
    """
    global document_message
    await call.message.delete()
    await call.answer(cache_time=1)
    markup_4 = InlineKeyboardMarkup(row_width=1,
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(text='❌ Отменить', callback_data='quit_notice')
                                        ]
                                    ])
    document_message = await call.message.answer(f'Введите текст для отправки всем пользователям:',
                                                 reply_markup=markup_4)
    await state.set_state(send_notice_allusers.text)


@router.message(send_notice_allusers.text)
async def notice_text(message: Message, state: FSMContext) -> None:
    """
    Handles the notice message from the user and prompts for photo addition.

    :param message: The Message object representing the user's message.
    :type message: aiogram.types.Message
    :param state: The FSMContext object to manage bot states.
    :type state: aiogram.fsm.context.FSMContext
    """
    await document_message.delete()
    await message.delete()
    answer = message.text

    markup_1 = InlineKeyboardMarkup(row_width=3,
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(text='📷 Добавить фотографию',
                                                                 callback_data='add_photo'),
                                        ],
                                        [
                                            InlineKeyboardButton(text='✅ Отправить', callback_data='next'),
                                            InlineKeyboardButton(text='❌ Отменить', callback_data='quit_notice')
                                        ]
                                    ])
    await state.update_data(text=answer)
    await message.answer(text=answer, reply_markup=markup_1)
    await state.set_state(send_notice_allusers.state)


@router.callback_query(F.data.startswith("next"), PrivateChatFilter(), send_notice_allusers.state)
async def start_notice(call: CallbackQuery, session: AsyncSession, bot: Bot, state: FSMContext) -> None:
    """
    Starts sending the notice message to all users.

    :param call: The CallbackQuery object representing the callback.
    :type call: aiogram.types.CallbackQuery
    :param session: The AsyncSession object for asynchronous database operations.
    :type session: sqlalchemy.ext.asyncio.AsyncSession
    :param bot: The Bot object for sending messages.
    :type bot: aiogram.Bot
    :param state: The FSMContext object to manage bot states.
    :type state: aiogram.fsm.context.FSMContext
    """
    await call.message.delete()
    await call.answer(cache_time=1)
    users = await select_allusers(session=session)
    data = await state.get_data()
    text = data.get('text')
    await state.clear()
    for user in users:
        try:
            await bot.send_message(chat_id=user.user_id, text=f"<b>{text}</b>")
            await sleep(0.33)
        except Exception as e:
            cid = user.user_id
            await bot.send_message(DEV_ID,
                                   f"Случилась <b>ошибка</b> при отправке уведомлений в чате <b>{cid}</b>\nСтатус ошибки: <code>{e}</code>")
    await call.message.answer('✉ Ваше уведомление для всех пользователей было отослано.')


@router.callback_query(F.data.startswith("add_photo"), PrivateChatFilter(), send_notice_allusers.state)
async def add_photo(call: CallbackQuery, state: FSMContext) -> None:
    """
    Prompts the user to send a photo for the notice.

    :param call: The CallbackQuery object representing the callback.
    :type call: aiogram.types.CallbackQuery
    :param state: The FSMContext object to manage bot states.
    :type state: aiogram.fsm.context.FSMContext
    """
    await call.answer(cache_time=1)
    await call.message.answer('Пришлите фото')
    await state.set_state(send_notice_allusers.photo)


@router.message(send_notice_allusers.photo, F.photo)
async def send_photo(message: Message, state: FSMContext) -> None:
    """
    Handles the photo message for the notice.

    :param message: The Message object representing the user's message.
    :type message: aiogram.types.Message
    :param state: The FSMContext object to manage bot states.
    :type state: aiogram.fsm.context.FSMContext
    """
    photo_file_id = message.photo[-1].file_id
    await state.update_data(photo=photo_file_id)
    data = await state.get_data()
    text = data.get('text')
    photo = data.get('photo')
    markup_2 = InlineKeyboardMarkup(row_width=2,
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(text='✅ Отправить', callback_data='next'),
                                            InlineKeyboardButton(text='❌ Отменить', callback_data='quit_notice')
                                        ]
                                    ])
    await message.answer_photo(photo=photo, caption=text, reply_markup=markup_2)


@router.callback_query(F.data.startswith("next"), PrivateChatFilter(), send_notice_allusers.photo)
async def next_notice_photo(call: CallbackQuery, session: AsyncSession, bot: Bot, state: FSMContext) -> None:
    """
    Sends the notice message with a photo to all users.

    :param call: The CallbackQuery object representing the callback.
    :type call: aiogram.types.CallbackQuery
    :param session: The AsyncSession object for asynchronous database operations.
    :type session: sqlalchemy.ext.asyncio.AsyncSession
    :param bot: The Bot object for sending messages.
    :type bot: aiogram.Bot
    :param state: The FSMContext object to manage bot states.
    :type state: aiogram.fsm.context.FSMContext
    """
    users = await select_allusers(session=session)
    data = await state.get_data()
    text = data.get('text')
    photo = data.get('photo')
    await state.clear()
    for user in users:
        try:
            await bot.send_photo(chat_id=user.user_id, photo=photo, caption=f"<b>{text}</b>")
            await sleep(0.33)
        except Exception as e:
            cid = user.user_id
            await bot.send_message(DEV_ID,
                                   f"Случилась <b>ошибка</b> при отправке уведомлений в чате <b>{cid}</b>\nСтатус ошибки: <code>{e}</code>")
    await call.message.answer('✉ Ваше уведомление для всех пользователей было отослано.')


@router.message(send_notice_allusers.photo, F.photo)
async def no_photo(message: Message) -> None:
    """
    Handles the case when the user does not send a photo for the notice.

    :param message: The Message object representing the user's message.
    :type message: aiogram.types.Message
    """
    markup_3 = InlineKeyboardMarkup(row_width=1,
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(text='❌ Отменить', callback_data='quit_notice')
                                        ]
                                    ])
    await message.answer('Пришли мне фото', reply_markup=markup_3)


@router.callback_query(F.data.startswith('quit_notice'))
async def quit_notice(call: CallbackQuery, state: FSMContext) -> None:
    """
    Cancels notice sending process and informs the user.

    :param call: The CallbackQuery object representing the callback.
    :type call: aiogram.types.CallbackQuery
    :param state: The FSMContext object to manage bot states.
    :type state: aiogram.fsm.context.FSMContext
    """
    await state.clear()
    await call.message.delete()
    await call.message.answer('❌ Отправка отменена')
# ----------------------------КОНЕЦ БЛОКА ОТПРАВКИ КОМАНДЫ ДОКУМЕНТА ВСЕМ ПОЛЬЗОВАТЕЛЯМ-------------------------------
