from aiogram.fsm.state import StatesGroup, State


# Изменить токены
class send_to_tokens(StatesGroup):
    text = State()
    state = State()