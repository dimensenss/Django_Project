# Generated by Django 4.2.6 on 2024-01-14 10:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0004_alter_cart_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='size',
        ),
    ]