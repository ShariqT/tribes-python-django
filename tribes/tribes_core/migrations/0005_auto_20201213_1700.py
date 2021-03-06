# Generated by Django 3.1.2 on 2020-12-13 17:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tribes_core', '0004_subscriptionperson_is_followed'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='is_followed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='person',
            name='is_follower',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='person',
            name='is_owner',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='message',
            name='receipent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='messaged_received', to='tribes_core.person'),
        ),
        migrations.AlterField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='message_sent', to='tribes_core.person'),
        ),
    ]
