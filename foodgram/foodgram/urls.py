"""
USERS
    /api/users/                         Список пользователей
    /api/users/{id}/                    Профиль пользователя
    /api/users/me/                      Текущий пользователь
    /api/users/subscriptions/           Мои подписки
    /api/users/{id}/subscribe/          Подписаться/Отписаться от пользователя
    /api/users/set_password/            Изменение пароля
    /api/auth/token/login/              Получить токен авторизации
    /api/auth/token/logout/             Удаление токена

TAGS
    /api/tags/                          Cписок тегов
    /api/tags/{id}/                     Получение тега

RECIPES
    /api/recipes/                       Список рецептов/Создание рецепта
    /api/recipes/download_shopping_cart/    Скачать список покупок
    /api/recipes/{id}/                  Получение/Обновление/Удаление рецепта
    /api/recipes/{id}/favorite/         Добавить/Удалить рецепт из избранного
    /api/recipes/{id}/shopping_cart/    Добавить рецепт в список покупок

ingredientS
    /api/ingredients/                   Список ингредиентов
    /api/ingredients/{id}/              Получение ингредиента

"""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView

urlpatterns = [
    path('api/', include('users.urls'), name='users'),
    path('api/', include('api.urls'), name='api'),
    path('admin/', admin.site.urls),
    path(
        'schema/',
        SpectacularAPIView.as_view(),
        name='schema'
    ),
    path(
        'schema/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),

]
