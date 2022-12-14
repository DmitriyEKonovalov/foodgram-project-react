from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import Subscribe, Recipe
from users.models import CustomUser
from users.serializers import BaseUserSerializer
from .base_serializers import BaseRecipeSerializer


class UserWithRecipesSerializer(BaseUserSerializer):
    recipes = BaseRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        recipes = Recipe.objects.filter(author=obj).count()
        return recipes


class SubscribeSerializer(UserWithRecipesSerializer):
    author_id = serializers.IntegerField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)
    method = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes', 'recipes_count',
                  'author_id', 'user_id', 'method')

    def save(self, **kwargs):
        author_id = self.validated_data.get('author_id')
        user_id = self.validated_data.get('user_id')
        subscribe, is_created = Subscribe.objects.get_or_create(
            author_id=author_id, user_id=user_id
        )
        self.instance = subscribe.author
        context = {
            'user': get_object_or_404(CustomUser, id=user_id),
            'author': subscribe.author
        }
        ret = BaseUserSerializer(instance=self.instance, context=context).data
        return ret
