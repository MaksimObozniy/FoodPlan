from django.db import models

class Recipe(models.Model):
    title = models.CharField(max_length=50, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    img_url = models.ImageField(upload_to="recipes_photo", verbose_name="Фото блюда")
    ingredients = models.TextField(verbose_name="Ингредиенты")
    instructions = models.TextField(verbose_name="Способ приготовления")
    
    def __str__(self):
        return self.title
    
class BotUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(max_length=255, null=True, blank=True, verbose_name="Username")
    is_subscribed = models.BooleanField(default=False, verbose_name="Подписка активна")
    free_request_left = models.IntegerField(default=3, verbose_name="Осталось бесплатных подписок")
    
    def __str__(self):
        return f"{self.username or self.telegram_id}"