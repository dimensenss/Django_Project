from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    image = models.ImageField(upload_to="user_photo/%Y/%m/%d/", blank=True, null = True, verbose_name='Зображення користувача')
    phone = models.CharField(max_length=128, blank=True, null = True, verbose_name='Телефон')
    address = models.CharField(max_length=256, blank=True, null = True, verbose_name='Адреса')

    class Meta:
        db_table = 'user'
        verbose_name = 'Користувач'
        verbose_name_plural = 'Користувачі'

    def __str__(self):
        return self.username