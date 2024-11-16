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
from django.db.models import Q
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


class RegisterView(views.APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()

            return Response({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

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
        channels = request.user.channels.all()
        serializer = ChannelSerializer(channels, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def searchUserName(self, request):
        query = request.query_params.get('q', '')
        users = User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )[:20]
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search_user(self, request):
        query = request.query_params.get('q', '')
        users = User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )[:20]
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

class EmailCheck(views.APIView):
    def get(self, request):
        email = request.GET.get('email', None)
        data = {
            'is_taken': User.objects.filter(email__iexact=email).exists()
        }
        return Response(data)