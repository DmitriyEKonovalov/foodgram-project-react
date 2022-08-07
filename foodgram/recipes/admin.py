from django.contrib import admin

from .models import (
    Favorite,
    Ingridient,
    Recipe,
    RecipeIngridients,
    ShoppingCart,
    Subscribe
)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    # list_display = '__all__'
    pass


@admin.register(Ingridient)
class IngridientAdmin(admin.ModelAdmin):
    # list_display = '__all__'
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    # list_display = '__all__'
    pass


@admin.register(RecipeIngridients)
class RecipeIngridientsAdmin(admin.ModelAdmin):
    # list_display = '__all__'
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    # list_display = '__all__'
    pass


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    # list_display = '__all__'
    pass
