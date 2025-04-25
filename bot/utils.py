from datetime import datetime
from recipes.models import BotUser
from asgiref.sync import sync_to_async
from django.utils import timezone

DAILY_LIMIT = 3

@sync_to_async
def check_and_use_access(user_id: int, username: str) -> bool:
    user, created = BotUser.objects.get_or_create(telegram_id=user_id)
    user.username = username
    user.save()

    return user.try_use_feature()
# def check_and_use_access(user_id: int, username: str) -> bool:
#     user, created = BotUser.objects.get_or_create(telegram_id=user_id)
#     user.username = username

#     today = datetime.now().date()
#     if user.last_request_date != today:
#         user.requests_today = 0
#         user.last_request_date = today

#     if user.requests_today >= DAILY_LIMIT:
#         user.save()
#         return False

#     user.requests_today += 1
#     user.save()
#     return True