# Generated by Django 4.2.6 on 2024-01-13 13:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0033_alter_sneakers_cat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sneakers',
            name='cat',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='sneakers', to='goods.category', verbose_name='Категорія'),
        ),
    ]
