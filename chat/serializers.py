from rest_framework import serializers
from chat.models import Channel, Reaction, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChannelSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = Channel
        fields = ['id', 'created_by', 'title', 'description', 'members']


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ['emoji_name', 'reacted_by', 'message']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient_type', 'recipient_user', 'recipient_channel', 'content', 'timestamp', 'reactions', 'reply_to', 'edited_at']