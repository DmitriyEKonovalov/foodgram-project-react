from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser


class BaseUserSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return user.subscribed.filter(author=obj).exists()
        return False
