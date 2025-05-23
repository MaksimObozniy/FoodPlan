# Generated by Django 5.2 on 2025-04-23 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BotUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.BigIntegerField(unique=True, verbose_name='Telegram ID')),
                ('username', models.CharField(blank=True, max_length=255, null=True, verbose_name='Username')),
                ('is_subscribed', models.BooleanField(default=False, verbose_name='Подписка активна')),
                ('free_request_left', models.IntegerField(default=3, verbose_name='Осталось бесплатных подписок')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('img_url', models.ImageField(upload_to='recipes_photo', verbose_name='Фото блюда')),
                ('ingredients', models.TextField(verbose_name='Ингредиенты')),
                ('instructions', models.TextField(verbose_name='Способ приготовления')),
            ],
        ),
    ]
