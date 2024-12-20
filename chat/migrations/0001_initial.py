# Generated by Django 5.1 on 2024-10-07 09:51

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='channels_created', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(related_name='channels_member_of', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('recipient_type', models.CharField(choices=[('User', 'User'), ('Channel', 'Channel')], max_length=7)),
                ('content', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('edited_at', models.DateTimeField(blank=True, null=True)),
                ('recipient_channel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='channel_messages', to='chat.channel')),
                ('recipient_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='received_dms', to=settings.AUTH_USER_MODEL)),
                ('reply_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='thread_messages', to='chat.message')),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Reaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emoji_name', models.CharField(max_length=20)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.message')),
                ('reacted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_reactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('reacted_by', 'message', 'emoji_name')},
            },
        ),
    ]
