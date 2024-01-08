# Generated by Django 4.2.6 on 2024-01-05 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sneakers_shop', '0016_remove_variants_color_remove_variants_size_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sneakers',
            name='color',
            field=models.JSONField(blank=True, null=True, verbose_name='Колір'),
        ),
        migrations.AddField(
            model_name='sneakers',
            name='size',
            field=models.JSONField(blank=True, null=True, verbose_name='Розмір'),
        ),
        migrations.AddIndex(
            model_name='sneakers',
            index=models.Index(fields=['color'], name='sneakers_sh_color_29dfac_idx'),
        ),
        migrations.AddIndex(
            model_name='sneakers',
            index=models.Index(fields=['size'], name='sneakers_sh_size_ba50b6_idx'),
        ),
    ]