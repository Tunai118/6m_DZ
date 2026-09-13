import requests
import random
from .models import User
from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404

from .serializers import RegisterSerializer, LoginSerializer, ConfirmSerializer



class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class LoginView(APIView):
    serializer_class = LoginSerializer

    @extend_schema(
        request=LoginSerializer,
        responses={200: dict},
    )
    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        refresh['birthdate'] = user.birthdate.isoformat() if user.birthdate else None

        return Response(
            {'refresh': str(refresh), 'access': str(refresh.access_token)},
            status=status.HTTP_200_OK,
            )

class GoogleLoginView(APIView):
    def get(self, request):
        google_url = 'https://accounts.google.com/o/oauth2/v2/auth'

        params = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'openid email profile',
            'access_type': 'offline',
        }

        url = requests.Request('GET', google_url, params=params).prepare().url

        return redirect(url)


class GoogleCallbackView(APIView):
    def get(self, request):
        code = request.query_params.get('code')

        if not code:
            return Response(
                {'error': 'Google authorization code is missing.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'redirect_uri': settings.GOOGLE_REDIRECT_URI,
                'grant_type': 'authorization_code',
            },
        )

        if token_response.status_code != 200:
            return Response(
                {'error': 'Failed to get Google access token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        google_access_token = token_response.json().get('access_token')

        user_response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {google_access_token}'},
        )

        if user_response.status_code != 200:
            return Response(
                {'error': 'Failed to get Google user data.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        google_user = user_response.json()

        email = google_user.get('email')
        first_name = google_user.get('given_name', '')
        last_name = google_user.get('family_name', '')

        if not email:
            return Response(
                {'error': 'Google account does not have an email.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True,
                'registration_source': 'google',
            },
        )

        user.first_name = first_name
        user.last_name = last_name
        user.is_active = True
        user.last_login = timezone.now()

        if created:
            user.registration_source = 'google'

        user.save()

        refresh = RefreshToken.for_user(user)
        refresh['birthdate'] = user.birthdate.isoformat() if user.birthdate else None

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class ConfirmView(APIView):
    serializer_class = ConfirmSerializer

    @extend_schema(request=ConfirmSerializer, responses={200: dict})
    def post(self, request):
        serializer = ConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        user = get_object_or_404(User, email=email)

        redis_key = f'confirmation_code:{user.id}'
        saved_code = redis_client.get(redis_key)

        if saved_code is None:
            return Response(
                {'error': 'Confirmation code expired or does not exist.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if saved_code != code:
            return Response(
                {'error': 'Invalid confirmation code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.save(update_fields=['is_active'])

        redis_client.delete(redis_key)

        return Response(
            {'message': 'User successfully confirmed.'},
            status=status.HTTP_200_OK,
        )