from django.db import models
from django.urls import reverse, reverse_lazy


# Create your models here.
class Sneakers(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name= "URL")
    content = models.TextField(blank=True, verbose_name='Контент')
    price = models.TextField(blank=True, verbose_name='Цена')
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", verbose_name='Фото')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    time_update = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product', kwargs = {'product_slug':self.slug})

    class Meta:
        verbose_name = 'Кроссовки'
        verbose_name_plural = 'Кроссовки'
        ordering = ['-time_create', 'title']

class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Имя")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('show_cat', kwargs = {'cat_slug':self.slug})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name', 'id']

class ProductImage(models.Model):
    product = models.ForeignKey(Sneakers, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to="product_images/%Y/%m/%d/", verbose_name='Изображение')


