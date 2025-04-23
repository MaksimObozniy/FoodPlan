from aiogram import Router, types, F
from aiogram.filters import CommandStart
from keyboards import main_menu
from recipes.models import Recipe, BotUser
import random
from aiogram.types import FSInputFile


router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user, created = BotUser.objects.get_or_create(telegram_id=message.from_user.id)
    user.username = message.from_user.username
    user.save()
    
    await message.answer(
        "Привет! Я бот FoodPlan и я помогу тебе найти рецепт по душе. Выбери опцию ниже 👇",
        reply_markup=main_menu
        )


@router.message(F.text == "Случайный рецепт")
async def random_recipe(message: types.Message):
    recipes = Recipe.objects.all()
    if not recipes:
        await message.answer("В нашей рецептотеке нет рецептов :(")
        return
    
    recipe = random.choice(recipes)
    
    image_path = recipe.image_url.path
    image = FSInputFile(image_path)
    
    caption = f"<b>{recipe.title}</b>\n\n{recipe.description}"
    buttons= [
        [types.InlineKeyboardButton(text="Что купить?", callback_data=f"ingredients_{recipe.id}")],
        [types.InlineKeyboardButton(text="Способ приготовления", callback_data=f"instructions_{recipe.id}")],
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer_photo(photo=recipe.image_url, caption=caption, parse_mode="HTML", reply_markup=markup)

    
@router.callback_query(F.data.startswith("ingredients_"))
async def show_ingredients(callback: types.CallbackQuery):
    recipe_id = int(callback.data.split("_")[1])
    recipe = Recipe.objects.get(id=recipe_id)
    await callback.message.answer(f"<b>Что купить:</b>\n{recipe.ingredients}", parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("instructions_"))
async def show_instructions(callback: types.CallbackQuery):
    recipe_id = int(callback.data.split("_")[1])
    recipe = Recipe.objects.get(id=recipe_id)
    await callback.message.answer(f"👨<b>Способ приготовления:</b>\n{recipe.instructions}", parse_mode="HTML")
    await callback.answer()


@router.message(F.text == "Найти рецепт")
async def ask_recipe_name(message: types.Message):
    await message.answer("Введите название бляда для поиска")


@router.message()
async def search_recipe(message: types.Message):
    query = message.text.lower()
    matches = Recipe.objects.filter(title__icontains=query)
    
    if matches.exists():
        text = "Найдено:\n" + "\n".join([f"• {r.title}" for r in matches])
    else:
        text = "Ничего не найдено. Попробуйте другое название."
        
    await message.answer(text)