from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from chat.serializers import ChannelSerializer
from users.serializers import UserSerializer

User = get_user_model()

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow users to edit their own profile.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj == request.user

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        if self.action == 'list':
            return User.objects.filter(id=self.request.user.id)
        return User.objects.all()

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(user, data=request.data, partial=request.method == 'PATCH')
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_channels(self, request):
        channels = request.user.channels_member_of.all()
        serializer = ChannelSerializer(channels, many=True)
        return Response(serializer.data)
