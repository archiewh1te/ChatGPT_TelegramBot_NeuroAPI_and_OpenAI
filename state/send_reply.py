from aiogram.fsm.state import StatesGroup, State


# Ответить на обращение
class send_to_reply(StatesGroup):
    text = State()
    state = State()