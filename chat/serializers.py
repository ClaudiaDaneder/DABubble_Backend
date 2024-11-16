from django.utils import timezone
from rest_framework import serializers
from chat.models import Channel, Reaction, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChannelSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)

    class Meta:
        model = Channel
        fields = ['id', 'created_by', 'title', 'description', 'members']


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ['emoji_name', 'reacted_by', 'id']

class ReactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ['emoji_name', 'reacted_by', 'message']


class MessageSerializer(serializers.ModelSerializer):
    reactions = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient_type', 'recipient_user', 'recipient_channel', 'content', 'timestamp', 'reactions', 'reply_to', 'edited_at']

    def get_reactions(self, obj):
        reactions = Reaction.objects.filter(message=obj)
        return ReactionSerializer(reactions, many=True).data

    def update(self, instance, validated_data):
        content_changed = 'content' in validated_data and validated_data['content'] != instance.content
        instance = super().update(instance, validated_data)
        if content_changed:
            instance.edited_at = timezone.now()
            instance.save()
        return instance