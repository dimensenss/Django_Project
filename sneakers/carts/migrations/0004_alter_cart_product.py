# Generated by Django 4.2.6 on 2024-01-14 10:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0041_remove_sneakersvariations_color_name'),
        ('carts', '0003_alter_cart_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='goods.sneakersvariations', verbose_name='Товар'),
        ),
    ]
