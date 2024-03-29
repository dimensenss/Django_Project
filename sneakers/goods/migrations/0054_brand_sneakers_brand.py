# Generated by Django 4.2.6 on 2024-02-25 14:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0053_sneakers_sku'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Назва бренду')),
            ],
        ),
        migrations.AddField(
            model_name='sneakers',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='brand', to='goods.brand', verbose_name='Бренд'),
        ),
    ]
