from aiogram.fsm.state import StatesGroup, State


# Антифлуд при запросе к чатгпт
class AntiFlood_gpt(StatesGroup):
    generating_message = State()
