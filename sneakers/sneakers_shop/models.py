from colorfield.fields import ColorField
from django.db import models
from django.urls import reverse, reverse_lazy


# Create your models here.
from django.utils.safestring import mark_safe
from taggit.managers import TaggableManager


class Sneakers(models.Model):
    title = models.CharField(max_length=255, verbose_name='Назва')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name= "URL")
    content = models.TextField(blank=True, verbose_name='Контент')
    price = models.DecimalField(default=0.0, max_digits=7, decimal_places=2, verbose_name='Ціна')
    color = ColorField(blank=True, null=True, verbose_name="Колір")
    size = models.JSONField(max_length=128, blank=True, null=True, verbose_name="Розміри")
    discount = models.DecimalField(default=0.0, max_digits=7, decimal_places=2, verbose_name='Ціна зі знижкою')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Час створення')
    time_update = models.DateTimeField(auto_now=True, verbose_name="Час оновлення")
    is_published = models.BooleanField(default=True, verbose_name='Опубліковано')
    quantity = models.PositiveSmallIntegerField(default=0, verbose_name="Кількість")
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, null=True, verbose_name="Категорія")
    tags = TaggableManager(blank=True, verbose_name='Теги')
    sell_price = models.DecimalField(default=0.0, max_digits=7, decimal_places=2, verbose_name='Актуальна ціна')
    variations = models.ManyToManyField('self', blank=True, verbose_name='Варіації')

    def save(self, *args, **kwargs):
        self.sell_price = self.calculate_sell_price()
        super().save(*args, **kwargs)

    def calculate_sell_price(self):
        return self.discount if self.discount else self.price

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product', kwargs={'product_slug': self.slug})

    def display_id(self):
        return f"{self.id:05}"

    class Meta:
        verbose_name = 'Кросівки'
        verbose_name_plural = 'Кросівки'
        ordering = ['-time_create', 'title']


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Назва")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('show_cat', kwargs = {'cat_slug':self.slug})

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['name', 'id']

class ProductImage(models.Model):
    product = models.ForeignKey(Sneakers, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to="product_images/%Y/%m/%d/", verbose_name='Зображення')

    class Meta:
        verbose_name = 'Фотографія'
        verbose_name_plural = 'Фотографії'


