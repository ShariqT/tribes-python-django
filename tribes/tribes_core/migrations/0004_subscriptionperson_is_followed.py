# Generated by Django 3.1.2 on 2020-11-06 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tribes_core', '0003_auto_20201017_2146'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionperson',
            name='is_followed',
            field=models.BooleanField(default=False),
        ),
    ]
