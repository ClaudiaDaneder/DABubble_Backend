from django.utils import timezone
from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model

from chat.models import Channel, Message, Reaction
from chat.permissions import IsChannelMember
from chat.serializers import ChannelSerializer, MessageSerializer, ReactionSerializer
from users.serializers import UserSerializer

User = get_user_model()

class ChannelViewSet(viewsets.ModelViewSet):
    serializer_class = ChannelSerializer
    # permission_classes = [permissions.IsAuthenticated, IsChannelMember]

    def get_queryset(self):
        return self.request.user.channels_member_of.all()

    def perform_create(self, serializer):
        channel = serializer.save(created_by=self.request.user)
        channel.members.add(self.request.user)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        channel = self.get_object()
        user_id = request.data.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        channel.members.add(user)
        return Response({'status': 'User added to channel'})

    @action(detail=True, methods=['post'])
    def leave_channel(self, request, pk=None):
        channel = self.get_object()
        channel.members.remove(request.user)
        return Response({'status': 'left channel'})

    @action(detail=True, methods=['get'])
    def memberlist(self, request, pk=None):
        channel = self.get_object()
        members = channel.members.all()
        serializer = UserSerializer(members, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsChannelMember]

    def get_queryset(self):
        return Message.objects.filter(channel__members=self.request.user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if instance.sender != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save(edited_at=timezone.now())


class ReactionViewSet(viewsets.ModelViewSet):
    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer
    # permission_classes = [permissions.IsAuthenticated, IsChannelMember]

    def get_queryset(self):
         return Reaction.objects.filter(message__channel__members=self.request.user)

    def perform_create(self, serializer):
        serializer.save(reacted_by=self.request.user)
