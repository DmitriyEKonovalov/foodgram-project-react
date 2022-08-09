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
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    ShoppingCartSerializer,
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

    # def get_serializer_class(self):
    #     if self.action == 'shopping_cart':
    #         return ShoppingCartSerializer
    #     serializer = super().get_serializer_class()
    #     return RecipeSerializer

    # recipes/download_shopping_cart/    Скачать список покупок
    @action(['get'], detail=True, url_path=r'download_shopping_cart')
    def download_shopping_cart(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    # recipes/{id}/shopping_cart/    Добавить рецепт в список покупок
    @action(['post', 'delete'], detail=True, url_path=r'shopping_cart')
    def shopping_cart(self, request, *args, **kwargs):
        # TODO здесь подумать надо, сюда приходит только id, который нужно или удалить или добаить
        #  если добавить, то обхекта еще не существует, а значит и нечего передавать в контекст
        """

        :param request:
        :param args:
        :param kwargs:
        :return:
       recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
        data = {'id': recipe.id}
        context = {
            'user': self.request.user,
            'recipe': recipe,
            'request': self.request
        }
        serializer = ShoppingCartSerializer(data=data, context=context)
        """
        if request.method == 'POST':
            data = {'id': kwargs['pk']}
            context = {'user_id': self.request.user.id, 'method': request.method}
            serializer = ShoppingCartSerializer(data=data, context=context)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
        recipe.in_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # recipes/{id}/favorite/         Добавить/Удалить рецепт из избранного
    @action(['post', 'delete'], detail=True, url_path=r'(?P<id>\d+)/favorite')
    def favorite(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
