from django.db import models
from django.conf import settings
import uuid

recipient_type_choices = [('User', 'User'), ('Channel', 'Channel')]

class Channel(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='channels_created')
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='channels')

    def __str__(self):
        return self.title


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    recipient_type = models.CharField(max_length=7, choices=recipient_type_choices)
    recipient_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='received_dms')
    recipient_channel = models.ForeignKey(Channel, on_delete=models.CASCADE, blank=True, null=True, related_name='channel_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='thread_messages')
    edited_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"{self.sender} to {self.recipient_type} at {self.timestamp}"

class Reaction(models.Model):
    emoji_name = models.CharField(max_length=20)
    reacted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='user_reactions')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')

    class Meta:
        unique_together = ('reacted_by', 'message', 'emoji_name')

    def __str__(self):
        return f"{self.reacted_by} reacted with {self.emoji_name} to message {self.message.id}"