# Generated by Django 5.0.2 on 2024-02-26 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_remove_product_imageroute_alter_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='imageRoute',
            field=models.CharField(default='', max_length=100),
        ),
    ]