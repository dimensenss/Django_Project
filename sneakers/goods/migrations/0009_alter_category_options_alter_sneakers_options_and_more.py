# Generated by Django 4.2.6 on 2023-12-30 14:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0008_sneakers_tags'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name', 'id'], 'verbose_name': 'Категорія', 'verbose_name_plural': 'Категорії'},
        ),
        migrations.AlterModelOptions(
            name='sneakers',
            options={'ordering': ['-time_create', 'title'], 'verbose_name': 'Кросівки', 'verbose_name_plural': 'Кросівки'},
        ),
        migrations.AlterField(
            model_name='sneakers',
            name='cat',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='goods.category', verbose_name='Категорія'),
        ),
        migrations.AlterField(
            model_name='sneakers',
            name='discount',
            field=models.DecimalField(decimal_places=2, max_digits=7, verbose_name='Знижка'),
        ),
        migrations.AlterField(
            model_name='sneakers',
            name='is_published',
            field=models.BooleanField(default=True, verbose_name='Опубліковано'),
        ),
        migrations.AlterField(
            model_name='sneakers',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=7, verbose_name='Ціна'),
        ),
        migrations.AlterField(
            model_name='sneakers',
            name='time_create',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Час створення'),
        ),
    ]
