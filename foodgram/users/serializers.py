from rest_framework import serializers
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import User


class BaseUserSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            not user.is_anonymous
            and user.subscribed.filter(author=obj).exists()
        )


"""
class BaseUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
        ]

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            not user.is_anonymous
            and user.subscribed.filter(author=obj).exists()
        )

"""
