# Generated by Django 4.2.6 on 2024-01-05 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0020_alter_sneakers_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='sneakers',
            name='variations',
            field=models.ManyToManyField(blank=True, related_name='variations', to='goods.sneakers', verbose_name='Варіації'),
        ),
    ]
