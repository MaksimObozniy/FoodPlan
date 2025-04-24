from aiogram import Router, types, F
from aiogram.filters import CommandStart
from keyboards import main_menu, get_recipes_keyboard
from recipes.models import Recipe
import random
import os
from states import SearchRecipe
from utils import check_and_use_access
from aiogram.types import FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from django.db.models.functions import Lower


router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    from recipes.models import BotUser
    user, created = await sync_to_async(BotUser.objects.get_or_create)(telegram_id=message.from_user.id)
    user.username = message.from_user.username
    await sync_to_async(user.save)()
    
    await message.answer(
        "Привет! Я бот FoodPlan и я помогу тебе найти рецепт по душе. Выбери опцию ниже 👇",
        reply_markup=main_menu
        )


@router.message(F.text == "Случайный рецепт")
async def random_recipe(message: types.Message):
    acces = await check_and_use_access(message.from_user.id, message.from_user.username)
    if not acces:
        await message.answer("Вы исчерпали 3 бесплатных запроса на сегодня. Оформите подписку для неограниченного доступа.")
        return
    
    
    
    recipes = await sync_to_async(list)(Recipe.objects.all())
    if not recipes:
        await message.answer("В нашей рецептотеке нет рецептов :(")
        return
    
    recipe = random.choice(recipes)
    
    photo_path = recipe.img_url.path 
    photo = FSInputFile(photo_path)
    
    caption = f"<b>{recipe.title}</b>\n\n{recipe.description}"
    buttons= [
        [types.InlineKeyboardButton(text="Что купить?", callback_data=f"ingredients_{recipe.id}")],
        [types.InlineKeyboardButton(text="Способ приготовления", callback_data=f"instructions_{recipe.id}")],
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer_photo(photo=photo, caption=caption, parse_mode="HTML", reply_markup=markup)

    
@router.callback_query(F.data.startswith("ingredients_"))
async def show_ingredients(callback: types.CallbackQuery):
    recipe_id = int(callback.data.split("_")[1])
    recipe = await sync_to_async(Recipe.objects.get)(id=recipe_id)
    
    await callback.message.answer(f"<b>Что купить:</b>\n{recipe.ingredients}", parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("instructions_"))
async def show_instructions(callback: types.CallbackQuery):
    recipe_id = int(callback.data.split("_")[1])
    recipe = await sync_to_async(Recipe.objects.get)(id=recipe_id)
    
    await callback.message.answer(f"👨<b>Способ приготовления:</b>\n{recipe.instructions}", parse_mode="HTML")
    await callback.answer()


@router.message(F.text == "Найти рецепт")
async def ask_recipe_name(message: types.Message, state: FSMContext):
    
    await state.set_state(SearchRecipe.waiting_for_recipe_name)
    await message.answer("Введите название блюда для поиска:")


@router.message(SearchRecipe.waiting_for_recipe_name)
async def search_recipe(message: types.Message, state: FSMContext):
    access = await check_and_use_access(message.from_user.id, message.from_user.username)
    if not access:
        await message.answer("Вы исчерпали 3 бесплатных запроса на сегодня. Оформите подписку для неограниченного доступа.")
        await state.clear()
        return

    @sync_to_async
    def get_matches(search_text: str):
        return [
            r for r in Recipe.objects.all()
            if search_text.lower() in r.title.lower()
        ]

    matches = await get_matches(message.text)

    if matches:
        await message.answer(f"Найдено рецептов: {len(matches)}", reply_markup=get_recipes_keyboard(matches))
    else:
        await message.answer("Ничего не найдено 😢")

    await state.clear()


@router.callback_query(F.data.startswith("recipe_"))
async def send_recipe(callback: CallbackQuery):
    recipe_id = int(callback.data.split("_")[1])

    recipe = await sync_to_async(Recipe.objects.get)(id=recipe_id)

    photo_path = recipe.img_url.path
    photo = FSInputFile(photo_path)

    caption = f"<b>{recipe.title}</b>\n\n{recipe.description}"

    buttons = [
        [types.InlineKeyboardButton(text="Что купить?", callback_data=f"ingredients_{recipe.id}")],
        [types.InlineKeyboardButton(text="Способ приготовления", callback_data=f"instructions_{recipe.id}")],
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.answer_photo(photo=photo, caption=caption, parse_mode="HTML", reply_markup=markup)
    await callback.answer()