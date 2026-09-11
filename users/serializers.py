import re

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('email', 'password', 'phone_number', 'birthdate')

    def validate_phone_number(self, value):
        if value is None or value == '':
            return value

        if not re.fullmatch(r'\+996\d{9}', value):
            raise serializers.ValidationError(
                'Phone number must be in format +996XXXXXXXXX.'
            )

        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        return User.objects.create_user(password=password, **validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get('request'),
            username=attrs['email'],
            password=attrs['password'],
        )

        if user is None:
            raise serializers.ValidationError(
                'Invalid email or password.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'User account is inactive.'
            )

        attrs['user'] = user
        return attrs


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'
