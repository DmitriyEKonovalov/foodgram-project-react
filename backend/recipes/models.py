from django.db import models

from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Name',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Color',
        max_length=16,
        unique=True,

    )
    slug = models.SlugField(
        verbose_name='Slug',
        unique=True,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __repr__(self):
        return f'{self.id}, {self.name}, {self.color}, {self.slug}'

    def __str__(self):
        return self.__repr__()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='name',
        max_length=200,
        unique=True,
    )
    measurement_unit = models.CharField(
        verbose_name='color',
        max_length=20,

    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __repr__(self):
        return f'{self.name}, {self.measurement_unit}'

    def __str__(self):
        return self.__repr__()


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Name',
        max_length=200,
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='recipes',
        verbose_name='Author',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name='Text',
    )
    image = models.ImageField(
        upload_to='upload/',
        verbose_name='Picture',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Tags',
        blank=True,
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Cocking time (in min)',
    )
    pub_date = models.DateTimeField(
        'Pub date',
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __repr__(self):
        return f'{self.name}'

    def __str__(self):
        return self.__repr__()


class RecipeIngredient(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients',
        on_delete=models.CASCADE,
        verbose_name='Ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Using in recipes',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Amount',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe'
            )
        ]
        verbose_name = 'Recipe compose (ingredients)'
        verbose_name_plural = 'Recipes composes (ingredients)'

    def __repr__(self):
        return f'{self.recipe}, {self.ingredient}, {self.amount}'

    def __str__(self):
        return self.__repr__()


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name='cart',
        on_delete=models.CASCADE,
        verbose_name='User',
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_cart',
        on_delete=models.CASCADE,
        verbose_name='Recipes',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_in_cart'
            )
        ]
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name='favorite_recipes',
        on_delete=models.CASCADE,
        verbose_name='Users favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_favor',
        on_delete=models.CASCADE,
        verbose_name='Favorite recipes',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_in_favor'
            )
        ]
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'


class Subscribe(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name='subscribed',
        on_delete=models.CASCADE,
        verbose_name='Users subscribe',
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='subscribers',
        on_delete=models.CASCADE,
        verbose_name='Subscribers',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_author_subscribe'
            )
        ]
        verbose_name = 'Subscribe'
        verbose_name_plural = 'Subscribes'
