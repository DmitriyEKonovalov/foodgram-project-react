from django.db.models import Sum, Exists, OuterRef, Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient,
    ShoppingCart, Tag
)
from .filters import RecipeFilter, IngredientFilter
from .paginators import CustomPageNumberPagination
from .serializers.base_serializers import (
    BaseIngredientSerializer, BaseTagSerializer
)
from .serializers.recipe_serializer import (
    RecipeSerializer,
    UsersChoiceRecipeWriteSerializer,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = BaseTagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = BaseIngredientSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.select_related(
            'author'
        ).prefetch_related(
            'ingredients', 'tags'
        )
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(Favorite.objects.filter(recipe=OuterRef('pk'), user=user)),
                is_in_shopping_cart=Exists(ShoppingCart.objects.filter(recipe=OuterRef('pk'), user=user))
            )
            is_in_shopping_cart_filter = self.request.query_params.get('is_in_shopping_cart')
            if is_in_shopping_cart_filter == '1':
                queryset = queryset.filter(is_in_shopping_cart=True)

            is_favorited_filter = self.request.query_params.get('is_favorited')
            if is_favorited_filter == '1':
                queryset = queryset.filter(is_favorited=True)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def _users_recipe(self, model, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        data = {'user': user.id, 'recipe': recipe_id}
        context = {'model': model, 'method': self.request.method}
        serializer = UsersChoiceRecipeWriteSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)

        if self.request.method == 'POST':
            response = serializer.save()
            return Response(response, status=status.HTTP_201_CREATED)

        model.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['post', 'delete'], detail=True, url_path=r'shopping_cart')
    def shopping_cart(self, request, *args, **kwargs):
        return self._users_recipe(model=ShoppingCart, recipe_id=kwargs['pk'])

    @action(['post', 'delete'], detail=True, url_path=r'favorite')
    def favorite(self, request, *args, **kwargs):
        return self._users_recipe(model=Favorite, recipe_id=kwargs['pk'])

    @action(['get'], detail=False, url_path=r'download_shopping_cart')
    def download_shopping_cart(self, request, *args, **kwargs):
        """Скачать список покупок (recipes/download_shopping_cart/)."""
        recipes = request.user.cart.values_list('recipe_id', flat=True)
        ingredients_list = RecipeIngredient.objects.filter(
            recipe__in=recipes
        ).select_related(
            'ingredient'
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total=Sum('amount')
        ).values_list(
            'ingredient__name',
            'total',
            'ingredient__measurement_unit'
        ).all()
        text = '\n'.join([f'{i} - {t} {m}' for (i, t, m) in ingredients_list])
        response = HttpResponse(text, content_type='application/txt')
        response['Content-Disposition'] = 'attachment; filename="shopping-list.txt"'
        return response
