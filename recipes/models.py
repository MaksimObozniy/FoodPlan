from django.db import models
from django.utils import timezone
class Recipe(models.Model):
    title = models.CharField(max_length=50, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    img_url = models.ImageField(upload_to="recipes_photo/", verbose_name="Фото блюда")
    ingredients = models.TextField(verbose_name="Ингредиенты")
    instructions = models.TextField(verbose_name="Способ приготовления")
    
    def __str__(self):
        return self.title
    
class BotUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(max_length=255, null=True, blank=True, verbose_name="Username")
    is_subscribed = models.BooleanField(default=False, verbose_name="Подписка активна")
    requests_today = models.IntegerField(default=0)
    last_request_date = models.DateField(null=True, blank=True, verbose_name="Дата последнего запроса")
    
    def reset_requests_if_new_day(self):
        today = timezone.now().date()
        if self.last_request_date != today:
            self.free_request_left = 3
            self.last_request_date = today
            self.save()
            
    def try_use_feature(self) -> bool:
        self.reset_requests_if_new_day()
        
        if self.is_subscribed:
            return True

        if self.free_request_left > 0:
            self.free_request_left -= 1
            self.save()
            return True
        return False
    
    def __str__(self):
        return self.username