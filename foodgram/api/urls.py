from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import IngredientViewSet, RecipeViewSet, TagViewSet

app_name = 'api'

router = DefaultRouter()

# ingredients/        Список ингредиентов
# ingredients/{id}/   Получение ингредиента
router.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)

# tags/               Cписок тегов
# tags/{id}/          Получение тега
router.register(
    'tags',
    TagViewSet,
    basename='tags'
)

# recipes/                       Список рецептов/Создание рецепта
# recipes/download_shopping_cart/    Скачать список покупок
# recipes/{id}/                  Получение/Обновление/Удаление рецепта
# recipes/{id}/favorite/         Добавить/Удалить рецепт из избранного
# recipes/{id}/shopping_cart/    Добавить рецепт в список покупок
router.register(
    'recipes',
    RecipeViewSet,
    basename='recipes'
)

urlpatterns = [
    path(
        '',
        include(router.urls)
    ),
]
