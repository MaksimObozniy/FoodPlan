
from asgiref.sync import sync_to_async
from recipes.models import BotUser

@sync_to_async
def check_and_use_access(telegram_id, username):
    user, _ = BotUser.objects.get_or_create(telegram_id=telegram_id)
    user.username = username
    return user.try_use_feature()