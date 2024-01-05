from django.db import models
from django.urls import reverse, reverse_lazy


# Create your models here.
from django.utils.safestring import mark_safe
from taggit.managers import TaggableManager


class Sneakers(models.Model):
    VARIANTS = (
        ('None', 'None'),
        ('Size', 'Size'),
        ('Color', 'Color'),
        ('Size-Color', 'Size-Color'),

    )

    title = models.CharField(max_length=255, verbose_name='Назва')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name= "URL")
    content = models.TextField(blank=True, verbose_name='Контент')
    price = models.DecimalField(default=0.0, max_digits=7, decimal_places=2, verbose_name='Ціна')
    discount = models.DecimalField(default=0.0, max_digits=7, decimal_places=2, verbose_name='Знижка')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Час створення')
    time_update = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True, verbose_name='Опубліковано')
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, null=True, verbose_name="Категорія")
    tags = TaggableManager()
    sell_price = models.DecimalField(default=0.0, max_digits=7, decimal_places=2, verbose_name='Актуальна ціна')
    variant = models.CharField(max_length=10, choices=VARIANTS, default='None')

    def save(self, *args, **kwargs):
        self.sell_price = self.calculate_sell_price()
        super().save(*args, **kwargs)

    def calculate_sell_price(self):
        return self.discount if self.discount else self.price

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product', kwargs = {'product_slug':self.slug})

    def display_id(self):
        return f"{self.id:05}"

    class Meta:
        verbose_name = 'Кросівки'
        verbose_name_plural = 'Кросівки'
        ordering = ['-time_create', 'title']

class Color(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=10, blank=True, null=True)
    def __str__(self):
        return self.name
    def color_tag(self):
        if self.code is not None:
            return mark_safe('<p style="background-color:{}">Color </p>'.format(self.code))
        else:
            return ""


class Size(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=10, blank=True,null=True)
    def __str__(self):
        return self.name

class Variants(models.Model):
    title = models.CharField(max_length=100, blank=True,null=True)
    sneakers = models.ForeignKey(Sneakers, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE,blank=True,null=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE,blank=True,null=True)
    image_id = models.IntegerField(blank=True,null=True,default=0)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2,default=0)

    def __str__(self):
        return self.title

    def image(self):
        img = ProductImage.objects.get(id=self.image_id)
        if img.id is not None:
             varimage=img.image.url
        else:
            varimage=""
        return varimage

    def image_tag(self):
        img = ProductImage.objects.get(id=self.image_id)
        if img.id is not None:
             return mark_safe('<img src="{}" height="50"/>'.format(img.image.url))
        else:
            return ""





class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Имя")
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


