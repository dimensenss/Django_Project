# Generated by Django 4.2.6 on 2024-01-05 20:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sneakers_shop', '0021_sneakers_variations'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sneakers',
            name='variations',
        ),
    ]
