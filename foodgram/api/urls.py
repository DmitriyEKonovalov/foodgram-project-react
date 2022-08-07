from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenBlacklistView
from django.urls import include
from django.urls import path
from .views import IngridientViewSet, TagViewSet, RecipeViewSet

app_name = 'api'

"""
"""


router = DefaultRouter()

# ingredients/        Список ингредиентов
# ingredients/{id}/   Получение ингредиента
router.register(
    'ingredients',
    IngridientViewSet,
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

