from asyncio import sleep

from aiogram import Router, F, Bot
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import load_config
from database.function.admin_commands import select_alladmins
from filters import PrivateChatFilter
from state.send_reply import send_to_reply
from state.send_support import send_to_support

config = load_config('.env')

DEV_ID = config.tg_bot.dev_id

router = Router(name='support')


class Replys(CallbackData, prefix='replys'):
    user_id: int


# РОУТЕР КНОПКИ НАПИСАТЬ В SUPPORT
@router.callback_query(F.data.startswith("support"), PrivateChatFilter())
async def get_support(call: CallbackQuery, state: FSMContext) -> None:
    """
    Handles the 'support' callback query, prompts the user to enter the text to send to support.

    :param call: The CallbackQuery object representing the callback.
    :type call: aiogram.types.CallbackQuery
    :param state: The FSMContext object to manage bot states.
    :type state: aiogram.fsm.context.FSMContext
    """
    await call.answer(cache_time=2)
    global support_start
    markup_4 = InlineKeyboardMarkup(row_width=1,
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(text='❌ Отменить', callback_data='quit_support')
                                        ]
                                    ])
    support_start = await call.message.answer(f'Введите текст для отправки в <b>support</b>:',
                                              reply_markup=markup_4)
    await state.set_state(send_to_support.text)


@router.message(send_to_support.text)
async def support_text(message: Message, session: AsyncSession, bot: Bot, state: FSMContext) -> None:
    """
    Handles the user's text message to support, sends it to all admins and informs the user.

    :param message: The Message object representing the user's message.
    :type message: aiogram.types.Message
    :param session: The AsyncSession object for asynchronous database operations.
    :type session: sqlalchemy.ext.asyncio.AsyncSession
    :param bot: The Bot object for sending messages.
    :type bot: aiogram.Bot
    :param state: The FSMContext object to manage bot states.
    :type state: aiogram.fsm.context.FSMContext
    """
    await support_start.delete()
    answer = message.text
    await state.update_data(text=answer)
    admins = await select_alladmins(session=session)
    data = await state.get_data()
    text = data.get('text')
    await state.clear()

    kb_reply = InlineKeyboardBuilder()
    kb_reply.row(InlineKeyboardButton(text='💬 Ответить', callback_data=Replys(user_id=message.from_user.id).pack(),
                                      width=1))

    for admin in admins:
        try:
            await bot.send_message(chat_id=admin.user_id,
                                   text=f"💬 <b>Поступило новое обращение!</b>\n\n"
                                        f"👤 <b>От пользователя:</b> @<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>\n"
                                        f"🖥 ID: <code>{message.from_user.id}</code> \n\n"
                                        f"<b>{text}</b>", reply_markup=kb_reply.as_markup())
            await sleep(0.33)
        except Exception as e:
            cid = message.from_user.id
            await message.answer(f"Упс! <b>Ошибка!</b> Не переживайте, ошибка уже <b>отправлена</b> разработчику.")
            await bot.send_message(DEV_ID,
                                   f"Случилась <b>ошибка</b> в чате <b>{cid}</b>\nСтатус ошибки: <code>{e}</code>")
    await message.answer('✅📨 Спасибо! Ваше обращение в техническую поддержку было отослано, с вами свяжутся.')


# РОУТЕР ОТВЕТА ОТ ТП
@router.callback_query(Replys.filter(), PrivateChatFilter())
async def reply(call: CallbackQuery, callback_data: Replys, state: FSMContext) -> None:
    """
    Handles the 'reply' callback query, prompts the user to enter the reply text to a user.

    :param call: The CallbackQuery object representing the callback.
    :type call: aiogram.types.CallbackQuery
    :param callback_data: The Replys CallbackData object representing the callback data.
    :type callback_data: Replys
    :param state: The FSMContext object to manage bot states.
    :type state: aiogram.fsm.context.FSMContext
    """
    await call.answer(cache_time=2)
    global reply_start
    markup_4 = InlineKeyboardMarkup(row_width=1,
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(text='❌ Отменить', callback_data='quit_support')
                                        ]
                                    ])
    reply_start = await call.message.answer(f'Введите текст для ответа пользователю:',
                                            reply_markup=markup_4)
    await state.update_data(user_id=callback_data.user_id)
    await state.set_state(send_to_reply.text)


@router.message(send_to_reply.text)
async def support_text(message: Message, bot: Bot, state: FSMContext) -> None:
    """
    Handles the user's reply text message, sends it to the specific user and informs the user.

    :param message: The Message object representing the user's message.
    :type message: aiogram.types.Message
    :param bot: The Bot object for sending messages.
    :type bot: aiogram.Bot
    :param state: The FSMContext object to manage bot states.
    :type state: aiogram.fsm.context.FSMContext
    """
    await reply_start.delete()
    answer = message.text
    await state.update_data(text=answer)
    data = await state.get_data()
    text = data.get('text')
    user_id = data.get('user_id')
    await state.clear()
    try:
        await bot.send_message(chat_id=user_id,
                               text=f"💬 <b>Ответ от Технической поддержки: </b>\n\n"
                                    f"<b>{text}</b>")
        await sleep(0.33)
    except Exception as e:
        cid = message.from_user.id
        await message.answer(f"Упс! <b>Ошибка!</b> Не переживайте, ошибка уже <b>отправлена</b> разработчику.")
        await bot.send_message(DEV_ID,
                               f"Случилась <b>ошибка</b> в чате <b>{cid}</b>\nСтатус ошибки: <code>{e}</code>")
    await message.answer('✅📨 Спасибо! Ваш ответ отправлен.')


@router.callback_query(F.data.startswith('quit_support'))
async def quit(call: CallbackQuery, state: FSMContext) -> None:
    """
    Handles the 'quit' callback query, cancels the message sending process and informs the user.

    :param call: The CallbackQuery object representing the callback.
    :type call: aiogram.types.CallbackQuery
    :param state: The FSMContext object to manage bot states.
    :type state: aiogram.fsm.context.FSMContext
    """
    await state.clear()
    await call.message.delete()
    await call.message.answer('❌ Отправка отменена')
