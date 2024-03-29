# Generated by Django 4.2.6 on 2024-02-01 14:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('goods', '0042_sneakers_first_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sneakersvariations',
            name='sneakers',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variations', to='goods.sneakers', verbose_name='Кросівки'),
        ),
        migrations.CreateModel(
            name='UserProductTimestamp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(blank=True, null=True, verbose_name='Time Stamp')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timestamps', to='goods.sneakers')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timestamps', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
