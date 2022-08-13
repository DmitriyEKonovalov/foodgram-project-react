from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenBlacklistView,
                                            TokenObtainPairView)

from .views import CustomUserViewSet

app_name = 'users'

router = DefaultRouter()

router.register(
    'users',
    CustomUserViewSet,
    basename='user'
)


urlpatterns = [
    path(
        '',
        include(router.urls)
    ),

    path(
        'auth/token/login/',
        TokenObtainPairView.as_view(),
        name='login'
    ),
    path(
        'auth/token/logout/',
        TokenBlacklistView.as_view(),
        name='logout'
    )
]
