from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

main_menu = ReplyKeyboardMarkup(
    keyboard=[
      [KeyboardButton(text="Случайный рецепт")],
      [KeyboardButton(text="Найти рецепт")],
      [KeyboardButton(text="Оформить подписку")]
    ],
    resize_keyboard=True
)


def get_subscription_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Купить подписку", callback_data="buy_subscription")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_recipes_keyboard(recipes):
  keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=recipe.title, callback_data=f"recipe_{recipe.id}")]
    for recipe in recipes
  ])
  return keyboard

