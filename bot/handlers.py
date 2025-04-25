from aiogram import Router, types, F
from aiogram.filters import CommandStart
from keyboards import main_menu, get_recipes_keyboard, get_subscription_keyboard
from recipes.models import Recipe, BotUser
import random
import os
from states import SearchRecipe
from utils import check_and_use_access
from aiogram.types import (
    Message, 
    PreCheckoutQuery,
    ContentType,
    FSInputFile, 
    CallbackQuery, 
    LabeledPrice
)
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from django.db.models.functions import Lower
from datetime import timedelta
from django.utils import timezone


router = Router()


SUBSCRIPTION_PRICE = 29900
SUBSCRIPTION_DURATION = 30


payment_router = Router()

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


@router.message(F.text == "Оформить подписку")
async def offer_subscription(message: types.Message):
    await message.answer(
        "Премиум подписка дает неограниченный доступ ко всем рецептам!\n"
        f"Стоимость: 299 руб / {SUBSCRIPTION_DURATION} дней\n\n"
        "После оплаты подписка активируется автоматически.",
        reply_markup=get_subscription_keyboard()
    )


@router.callback_query(F.data == "buy_subscription")
async def buy_subscription(callback: types.CallbackQuery):
    await callback.bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="Премиум подписка FoodPlan",
        description=f"Доступ ко всем рецептам на {SUBSCRIPTION_DURATION} дней",
        payload="month_sub",
        provider_token="1744374395:TEST:52fffc9e8301b69827ef",
        currency="RUB",
        prices=[LabeledPrice(label="Подписка", amount=SUBSCRIPTION_PRICE)],
        start_parameter="month_sub",
        photo_size=512,
        need_email=True,
        send_email_to_provider=True
    )
    await callback.answer()


@payment_router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@payment_router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):     
    user, created = await sync_to_async(BotUser.objects.get_or_create)(
        telegram_id=message.from_user.id,
        defaults={'username': message.from_user.username}
    )

    user.is_subscribed = True
    user.subscription_end = timezone.now() + timedelta(days=SUBSCRIPTION_DURATION)
    await sync_to_async(user.save)()
        
    await message.answer(
        "🎉 Подписка успешно активирована!\n"
        f"Доступ открыт до {user.subscription_end.strftime('%d.%m.%Y')}"
    )


@router.message(F.text == "Случайный рецепт")
async def random_recipe(message: types.Message):
    user = await sync_to_async(BotUser.objects.get)(telegram_id=message.from_user.id)
    access = await sync_to_async(user.try_use_feature)()
    # acces = await check_and_use_access(message.from_user.id, message.from_user.username)
    if not access:
        await message.answer(
            "Вы исчерпали 3 бесплатных запроса на сегодня. Оформите подписку для неограниченного доступа.",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="Оформить подписку", callback_data="buy_subscription")]
            ])
        )
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