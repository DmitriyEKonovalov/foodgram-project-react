from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Subscribe
)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    # list_display = '__all__'
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    # list_display = '__all__'
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    # list_display = '__all__'
    pass


@admin.register(RecipeIngredients)
class RecipeingredientsAdmin(admin.ModelAdmin):
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
