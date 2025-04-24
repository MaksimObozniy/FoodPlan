from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

main_menu = ReplyKeyboardMarkup(
    keyboard=[
      [KeyboardButton(text="Случайный рецепт")],
      [KeyboardButton(text="Найти рецепт")],
    ],
    resize_keyboard=True
)

def get_recipes_keyboard(recipes):
  keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=recipe.title, callback_data=f"recipe_{recipe.id}")]
    for recipe in recipes
  ])
  return keyboard

