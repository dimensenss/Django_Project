# Generated by Django 4.2.6 on 2024-01-12 13:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0029_categorytree_alter_sneakers_cat_delete_category'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CategoryTree',
            new_name='Category',
        ),
    ]