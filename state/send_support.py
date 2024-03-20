from aiogram.fsm.state import StatesGroup, State


# Написать в ТП
class send_to_support(StatesGroup):
    text = State()
    state = State()
