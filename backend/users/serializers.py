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
        user = self.context.get('user')
        return user.is_authenticated and user.subscribed.filter(author=obj).exists()


"""
### новый сериалайзер для
class EmailTokenObtainSerializer(TokenObtainSerializer):
    username_field = User.EMAIL_FIELD

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        email = attrs.get('email')
        self.user = User.objects.filter(email__iexact=email).first()
        if not (self.user and self.user.is_active):
            raise serializers.ValidationError('пользователь не найден')

        password = attrs.get('password')
        if not self.user.check_password(password):
            raise serializers.ValidationError('неправильный пароль')

        token = self.get_token(self.user)

        data = {'auth_token': str(token.access_token)}

        return data

"""
