from PIL import Image
from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse, reverse_lazy

# Create your models here.
from django.utils.safestring import mark_safe
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from taggit_autosuggest.managers import TaggableManager
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

User = get_user_model()


class Sneakers(models.Model):
    title = models.CharField(max_length=255, verbose_name='Назва')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    content = models.TextField(blank=True, verbose_name='Контент')
    price = models.DecimalField(default=0.0, max_digits=7, decimal_places=2, verbose_name='Ціна')
    color = ColorField(blank=True, null=True, verbose_name="Колір")
    discount = models.DecimalField(default=0.0, max_digits=7, decimal_places=2, verbose_name='Ціна зі знижкою')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Час створення')
    time_update = models.DateTimeField(auto_now=True, verbose_name="Час оновлення")
    is_published = models.BooleanField(default=True, verbose_name='Опубліковано')
    cat = models.ForeignKey('Category', models.SET_DEFAULT, default=0, related_name='sneakers',
                            verbose_name='Категорія')
    tags = TaggableManager(blank=True, verbose_name='Теги', help_text='')
    sell_price = models.DecimalField(default=0.0, max_digits=7, decimal_places=2, verbose_name='Актуальна ціна')
    first_image = models.OneToOneField(
        'ProductImage',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Перше зображення'
    )

    def save(self, *args, **kwargs):
        self.sell_price = self.calculate_sell_price()
        super().save(*args, **kwargs)

    def calculate_sell_price(self):
        return self.discount if self.discount else self.price

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse_lazy('goods:product', kwargs={'product_slug': self.slug})

    def display_id(self):
        return f"{self.id:05}"

    class Meta:
        verbose_name = 'Кросівки'
        verbose_name_plural = 'Кросівки'
        ordering = ['-time_create', 'title']


class SneakersVariationsQS(models.QuerySet):
    def total_quantity(self):
        total_sum = 0
        if self:
            for pd in self:
                total_sum += pd.quantity
            return total_sum
        return 0


class SneakersVariations(models.Model):
    sneakers = models.ForeignKey(Sneakers, on_delete=models.CASCADE, related_name='variations', verbose_name='Кросівки')
    size = models.CharField(max_length=8, verbose_name='Розмір')
    quantity = models.PositiveSmallIntegerField(default=0, verbose_name="Кількість")

    def __str__(self):
        return f"{self.sneakers.title}  Розмір: {self.size}"

    class Meta:
        verbose_name = 'Варіація'
        verbose_name_plural = 'Варіації'
        ordering = ['size']

    objects = SneakersVariationsQS.as_manager()


class Category(MPTTModel):
    title = models.CharField(max_length=255, verbose_name='Назва категорії')
    slug = models.SlugField(max_length=255, verbose_name='URL', unique=True)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
        related_name='children',
        verbose_name='Батьківська категорія'
    )

    class MPTTMeta:
        order_insertion_by = ('title',)

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'

    def __str__(self):
        return ''.join([ancestor.title + ' ' for ancestor in self.get_ancestors(include_self=True)])

    def get_absolute_url(self):
        # return '/category/'+'/'.join([ancestor.slug for ancestor in self.get_ancestors(include_self=True)])
        slug = '/'.join([ancestor.slug for ancestor in self.get_ancestors(include_self=True)])
        return reverse_lazy('goods:show_cat', kwargs={'cat_slug': slug})


class ProductImage(models.Model):
    product = models.ForeignKey(Sneakers, on_delete=models.CASCADE, related_name='images')
    image = ProcessedImageField(
        upload_to="product_images/%Y/%m/%d/",
        processors=[ResizeToFill(800, 800)],
        format='JPEG',  # или 'PNG' в зависимости от ваших требований
        options={'quality': 90}  # Качество изображения
    )

    class Meta:
        verbose_name = 'Фотографія'
        verbose_name_plural = 'Фотографії'
