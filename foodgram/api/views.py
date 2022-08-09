from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredients,
    Subscribe,
    Favorite,
    ShoppingCart,
    Tag
)
from .serializers.base_serializers import BaseTagSerializer
from .serializers.base_serializers import BaseIngredientSerializer
from .serializers.base_serializers import BaseRecipeSerializer
from .serializers.users_serializers import SubscribeSerializer
from .serializers.users_serializers import UserWithRecipesSerializer
from .serializers.recipe_serializer import RecipeSerializer
from .serializers.recipe_serializer import UsersChoiceRecipeSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = BaseTagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = BaseIngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer

    def _users_recipe(self, model, recipe_id):
        """Универсальная функция для создания записей в shopping_cart и favorite."""
        user_id = self.request.user.id
        data = {'id': recipe_id}
        method = self.request.method
        context = {'user_id': user_id, 'method': method, 'model': model}
        serializer = UsersChoiceRecipeSerializer(data=data, context=context)
        if serializer.is_valid(raise_exception=True):
            # CREATE
            if self.request.method == 'POST':
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            # DELETE
            recipe = get_object_or_404(Recipe, id=recipe_id)
            model.objects.filter(user=user_id, recipe=recipe.id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        queryset = Recipe.objects.select_related('author').prefetch_related('ingredients', 'tags').all()
        return queryset

    @action(['get'], detail=True, url_path=r'download_shopping_cart')
    def download_shopping_cart(self, request, *args, **kwargs):
        """Скачать список покупок (recipes/download_shopping_cart/)."""
        return self.retrieve(request, *args, **kwargs)

    @action(['post', 'delete'], detail=True, url_path=r'shopping_cart')
    def shopping_cart(self, request, *args, **kwargs):
        """Добавить рецепт в список покупок (recipes/{id}/shopping_cart/)."""
        return self._users_recipe(model=ShoppingCart, recipe_id=kwargs['pk'])

    @action(['post', 'delete'], detail=True, url_path=r'favorite')
    def favorite(self, request, *args, **kwargs):
        """Добавить/Удалить рецепт из избранного (recipes/{id}/favorite/)."""
        return self._users_recipe(model=Favorite, recipe_id=kwargs['pk'])


"""
    @action(['get'], detail=False, url_path='kuku', serializer_class=RecipeSerializer, permission_classes=[])
    def kuku(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(['post', 'delete'], detail=True, url_path=r'shopping_cart')
    def shopping_cart(self, request, *args, **kwargs):
        if request.method == 'POST':
            data = {'id': kwargs['pk']}
            context = {'user_id': self.request.user.id, 'method': request.method}
            serializer = ShoppingCartSerializer(data=data, context=context)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
        recipe.in_cart.filter(user=self.request.user.id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

"""