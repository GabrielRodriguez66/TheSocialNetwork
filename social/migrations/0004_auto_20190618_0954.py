# Generated by Django 2.1.2 on 2019-06-18 17:54

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0003_shout'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shout',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 6, 18, 9, 54, 51, 749949), verbose_name='date published'),
        ),
    ]
