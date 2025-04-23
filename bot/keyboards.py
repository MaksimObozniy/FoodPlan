from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
      [KeyboardButton(text="Случайный рецепт")],
      [KeyboardButton(text="Найти рецепт")],
    ],
    resize_keyboard=True
)