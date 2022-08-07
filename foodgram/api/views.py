from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

from rest_framework import mixins
from rest_framework import viewsets

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
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer

    def get_queryset(self):
        queryset = Recipe.objects.select_related('author').prefetch_related('ingredients', 'tags').all()
        return queryset

    # def get_serializer(self, *args, **kwargs):
    #     return self.serializer_class(source=self.queryset)

    # recipes/download_shopping_cart/    Скачать список покупок
    @action(['get'], detail=False, url_path=r'download_shopping_cart')
    def download_shopping_cart(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    # recipes/{id}/shopping_cart/    Добавить рецепт в список покупок
    @action(['post', 'delete'], detail=False, url_path=r'(?P<id>\d+)/shopping_cart')
    def shopping_cart(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    # recipes/{id}/favorite/         Добавить/Удалить рецепт из избранного
    @action(['post', 'delete'], detail=False, url_path=r'(?P<id>\d+)/favorite')
    def favorite(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
