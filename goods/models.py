from PIL import Image
from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Avg
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
    sku = models.CharField(max_length=255, verbose_name='Артикул', blank=True, null=True, unique=True)
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
    brand = models.ForeignKey('Brand', blank=True, null=True, on_delete=models.SET_NULL, related_name='brand',
                              verbose_name='Бренд')

    tags = TaggableManager(blank=True, verbose_name='Теги', help_text='')
    sell_price = models.DecimalField(default=0.0, max_digits=7, decimal_places=2, verbose_name='Актуальна ціна')
    first_image = models.OneToOneField(
        'ProductImage',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Перше зображення'
    )

    @property
    def discount_info(self):
        discount = 100
        if self.price:
            discount = (self.price - self.discount) * 100 / self.price
        return round(discount, 2) if discount < 100 else 0

    def in_stock(self):
        if self.variations.all().total_quantity() > 0:
            return True
        return False

    def save(self, *args, **kwargs):
        self.sell_price = self.calculate_sell_price()
        super().save(*args, **kwargs)

    def calculate_sell_price(self):
        return self.discount if self.discount else self.price

    def calculate_rate(self):
        average_rating = self.reviews.aggregate(Avg('rate'))['rate__avg']
        if average_rating is not None:
            return round(average_rating, 2)
        return 0

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse_lazy('goods:product', kwargs={'product_slug': self.slug})

    def display_id(self):
        if self.sku:
            return self.sku
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
        return ''.join([ancestor.title + ' > ' for ancestor in self.get_ancestors(include_self=True)])[:-3]

    def get_absolute_url(self):
        # return '/category/'+'/'.join([ancestor.slug for ancestor in self.get_ancestors(include_self=True)])
        slug = '/'.join([ancestor.slug for ancestor in self.get_ancestors(include_self=True)])
        return reverse_lazy('goods:show_cat', kwargs={'cat_slug': slug})


class ProductImage(models.Model):
    product = models.ForeignKey(Sneakers, on_delete=models.CASCADE, related_name='images')
    image = ProcessedImageField(
        upload_to="product_images/%Y/%m/%d/",
        processors=[ResizeToFill(800, 800)],
        format='JPEG',
        options={'quality': 90}
    )

    class Meta:
        verbose_name = 'Фотографія'
        verbose_name_plural = 'Фотографії'


class Brand(models.Model):
    name = models.CharField(max_length=255, verbose_name='Назва бренду')
    image = ProcessedImageField(
        upload_to="brand_images/%Y/%m/%d/",
        processors=[ResizeToFill(200, 100)],
        format='JPEG',
        options={'quality': 90}
    )

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренди'

    def __str__(self):
        return self.name


class Review(models.Model):
    RATING_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
    product = models.ForeignKey(Sneakers, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, default='Анонім', on_delete=models.SET_DEFAULT, related_name='reviews')
    text = models.TextField(verbose_name='Текст', max_length=500)
    date = models.DateTimeField(auto_now_add=True)
    rate = models.PositiveSmallIntegerField(choices=RATING_CHOICES)

    class Meta:
        verbose_name = 'Відгук'
        verbose_name_plural = 'Відгуки'

    def __str__(self):
        return self.text


class WishQuerySet(models.QuerySet):
    def total_count(self):
        return self.count()


class Wish(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Користувач")
    product = models.ForeignKey(Sneakers, on_delete=models.CASCADE, verbose_name="Товар")
    session_key = models.CharField(max_length=32, null=True, blank=True)
    created_timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата додавання")

    class Meta:
        db_table = 'wish'
        verbose_name = "Побажання"
        verbose_name_plural = "Побажання"
        unique_together = ('user', 'product', 'session_key')

    objects = models.Manager()

    def __str__(self):
        if self.user:
            return f"Бажання користувача {self.user.username} | Товар {self.product.title}"
        return f"Анонімне бажання | Товар {self.product.title}"