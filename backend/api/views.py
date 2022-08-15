from django.db.models import Sum
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
from .filters import RecipeFilter
from .serializers.base_serializers import (
    BaseIngredientSerializer, BaseTagSerializer
)
from .serializers.recipe_serializer import (
    RecipeSerializer, UsersChoiceRecipeSerializer
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = BaseTagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = BaseIngredientSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related(
        'author'
    ).prefetch_related(
        'ingredients', 'tags'
    ).all()
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    def _users_recipe(self, model, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        data = {
            'user_id': user.id,
            'recipe_id': recipe.id,
        }
        context = {'user': user, 'model': model, 'method': self.request.method}
        serializer = UsersChoiceRecipeSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)

        if self.request.method == 'POST':
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        recipe = get_object_or_404(Recipe, id=recipe_id)
        model.objects.filter(user=user.id, recipe=recipe.id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        response['Content-Disposition'] = 'attachment; filename=shopping-list'
        return response

    @action(['post', 'delete'], detail=True, url_path=r'shopping_cart')
    def shopping_cart(self, request, *args, **kwargs):
        return self._users_recipe(model=ShoppingCart, recipe_id=kwargs['pk'])

    @action(['post', 'delete'], detail=True, url_path=r'favorite')
    def favorite(self, request, *args, **kwargs):
        return self._users_recipe(model=Favorite, recipe_id=kwargs['pk'])
