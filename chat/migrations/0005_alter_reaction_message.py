# Generated by Django 5.1 on 2024-10-13 19:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_alter_channel_members'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reaction',
            name='message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reactions', to='chat.message'),
        ),
    ]
