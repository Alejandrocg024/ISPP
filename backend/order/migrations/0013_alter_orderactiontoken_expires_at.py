# Generated by Django 5.0.2 on 2024-04-11 16:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0012_alter_orderactiontoken_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderactiontoken',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 4, 17, 0, 45, 50, 276117, tzinfo=datetime.timezone.utc)),
        ),
    ]
