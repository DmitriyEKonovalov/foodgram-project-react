from recipes.models import Subscribe
from rest_framework import serializers
from users.models import User
from users.serializers import BaseUserSerializer

from .base_serializers import BaseRecipeSerializer


class UserWithRecipesSerializer(BaseUserSerializer):
    recipes = BaseRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        recipes = obj.recipes.count()
        return recipes


class SubscribeSerializer(UserWithRecipesSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes', 'recipes_count')

    def to_internal_value(self, data):
        return self.context['author']

    def validate(self, attrs):
        request = self.context['request']
        user = self.context['user']
        author = self.context['author']
        method = request.method
        subscribe = user.subscribed.filter(author=author).exists()
        if method == 'POST':
            if subscribe:
                raise serializers.ValidationError('Подписка существует!')
            if user == author:
                raise serializers.ValidationError('Нельзя подписаться на себя')
        if method == 'DELETE':
            if not subscribe:
                raise serializers.ValidationError('подписки не существует')
        return attrs

    def save(self, **kwargs):
        author_id = self.validated_data.id
        user_id = self.context['user'].id
        Subscribe.objects.create(author_id=author_id, user_id=user_id)
        return self.context['author']
