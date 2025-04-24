from aiogram.fsm.state import State, StatesGroup

class SearchRecipe(StatesGroup):
    waiting_for_recipe_name = State()