from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets, permissions, views, status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model, authenticate, login, logout
from rest_framework.permissions import IsAuthenticated
from chat.serializers import ChannelSerializer
from users.serializers import CustomAuthSerializer, UserSerializer
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(ObtainAuthToken):
    serializer_class = CustomAuthSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user.online = True
        user.save()
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'online': user.online
        })

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    if request.user.is_authenticated:
        request.user.online = False
        request.user.save()

    logout(request)
    return Response({'message': 'Logged out successfully'})


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
    permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    # def get_queryset(self):
    #     if self.action == 'list':
    #         return User.objects.filter(id=self.request.user.id)
    #     return User.objects.all()

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        logger.debug(f"Me endpoint called. User: {request.user}, Method: {request.method}")
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            logger.debug(f"Returning user data: {serializer.data}")
            return Response(serializer.data)
        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(user, data=request.data, partial=request.method == 'PATCH')
            serializer.is_valid(raise_exception=True)
            serializer.save()
            logger.debug(f"Updated user data: {serializer.data}")
            return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_channels(self, request):
        channels = request.user.channels_member_of.all()
        serializer = ChannelSerializer(channels, many=True)
        return Response(serializer.data)