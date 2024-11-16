from django.utils import timezone
from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.db import transaction
from django.contrib.auth import get_user_model

from chat.models import Channel, Message, Reaction
from chat.permissions import IsChannelMember
from chat.serializers import ChannelSerializer, MessageSerializer, ReactionCreateSerializer, ReactionSerializer
from users.serializers import UserSerializer

User = get_user_model()

class ChannelViewSet(viewsets.ModelViewSet):
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsChannelMember]

    USER_SPECIFIC_CHANNELS = True

    def get_queryset(self):
        if self.USER_SPECIFIC_CHANNELS:
            return self.request.user.channels.all()
        else:
            return self.queryset

    def perform_create(self, serializer):
        channel = serializer.save(created_by=self.request.user)
        channel.members.add(self.request.user)


    @action(detail=True, methods=['post'])
    def add_members(self, request, pk=None):
        channel = self.get_object()
        user_ids = request.data.get('user_ids')

        # Ensure user_ids is always a list
        if isinstance(user_ids, int):
            user_ids = [user_ids]
        elif not isinstance(user_ids, list):
            return Response({'error': 'Invalid user_ids format'}, status=status.HTTP_400_BAD_REQUEST)

        added_users = []
        not_found_users = []

        with transaction.atomic():
            for user_id in user_ids:
                try:
                    user = User.objects.get(id=user_id)
                    if user not in channel.members.all():
                        channel.members.add(user)
                        added_users.append(user_id)
                except User.DoesNotExist:
                    not_found_users.append(user_id)

        response_data = {
            'added_users': added_users,
            'not_found_users': not_found_users,
            'status': 'Users processed'
        }

        if not_found_users:
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
        return Response(response_data, status=status.HTTP_200_OK)

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

    @action(detail=False, methods=['get'])
    def search_channel(self, request):
        query = request.query_params.get('q', '')
        channels = Channel.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )[:20]
        serializer = self.get_serializer(channels, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsChannelMember]

    def get_queryset(self):
        user = self.request.user
        queryset = Message.objects.filter(
            Q(recipient_channel__members=user) |
            Q(sender=user, recipient_type='USER') |
            Q(recipient_user=user)
        )

        recipient_channel = self.request.query_params.get('recipient_channel')
        if recipient_channel:
            queryset = queryset.filter(recipient_channel_id=recipient_channel)

        recipient_user = self.request.query_params.get('recipient_user')
        if recipient_user:
            queryset = queryset.filter(
                Q(recipient_user_id=recipient_user) |
                Q(sender=user, recipient_user_id=recipient_user)
            )

        recipient_type = self.request.query_params.get('recipient_type')
        if recipient_type:
            queryset = queryset.filter(recipient_type=recipient_type)

        return queryset.order_by('timestamp')

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        messages = Message.objects.filter(
            Q(content__icontains=query)
        )[:20]
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


class ReactionViewSet(viewsets.ModelViewSet):
    queryset = Reaction.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ReactionCreateSerializer
        return ReactionSerializer

    def perform_create(self, serializer):
        serializer.save(reacted_by=self.request.user)
