# Generated by Django 4.2.6 on 2024-01-05 17:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0015_color_size_sneakers_variant_variants'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='variants',
            name='color',
        ),
        migrations.RemoveField(
            model_name='variants',
            name='size',
        ),
        migrations.RemoveField(
            model_name='variants',
            name='sneakers',
        ),
        migrations.RemoveField(
            model_name='sneakers',
            name='variant',
        ),
        migrations.DeleteModel(
            name='Color',
        ),
        migrations.DeleteModel(
            name='Size',
        ),
        migrations.DeleteModel(
            name='Variants',
        ),
    ]
