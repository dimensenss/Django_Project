# Generated by Django 4.2.6 on 2024-01-11 12:49

import colorfield.fields
from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
        ('goods', '0027_sneakers_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(db_index=True, max_length=100, verbose_name='Назва'),
        ),
        migrations.AlterField(
            model_name='sneakers',
            name='color',
            field=colorfield.fields.ColorField(blank=True, default=None, image_field=None, max_length=25, null=True, samples=None, verbose_name='Колір'),
        ),
        migrations.AlterField(
            model_name='sneakers',
            name='size',
            field=models.JSONField(blank=True, max_length=128, null=True, verbose_name='Розміри'),
        ),
        migrations.AlterField(
            model_name='sneakers',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Теги'),
        ),
        migrations.AlterField(
            model_name='sneakers',
            name='time_update',
            field=models.DateTimeField(auto_now=True, verbose_name='Час оновлення'),
        ),
    ]
