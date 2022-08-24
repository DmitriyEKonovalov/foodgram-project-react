from django.urls import include, path
from rest_framework.routers import DefaultRouter
# from rest_framework_simplejwt.views import TokenBlacklistView

from .views import CustomUserViewSet
# from .views import EmailTokenObtainPairView, LogoutView

app_name = 'users'

router = DefaultRouter()

router.register(
    'users',
    CustomUserViewSet,
    basename='user'
)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
