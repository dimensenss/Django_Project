# Generated by Django 4.2.6 on 2024-01-05 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0018_color_size_variants_and_more'),
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
        migrations.AddField(
            model_name='sneakers',
            name='color',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='sneakers',
            name='size',
            field=models.JSONField(default=1, max_length=128),
            preserve_default=False,
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