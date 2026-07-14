from aiogram.fsm.state import State, StatesGroup


class AsciiGeneration(StatesGroup):
    choosing_mode = State()
    choosing_width = State()
