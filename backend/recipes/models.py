from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=16,
        unique=True,

    )
    slug = models.SlugField(
        verbose_name='Slug',
        unique=True,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __repr__(self):
        return f'{self.id}, {self.name}, {self.color}, {self.slug}'

    def __str__(self):
        return self.__repr__()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
    )
    measurement_unit = models.CharField(
        verbose_name='Цвет',
        max_length=20,

    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __repr__(self):
        return f'{self.name}, {self.measurement_unit}'

    def __str__(self):
        return self.__repr__()


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    image = models.ImageField(
        upload_to='upload/',
        verbose_name='Картинка',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги',
        blank=True,
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __repr__(self):
        return f'{self.name}'

    def __str__(self):
        return self.__repr__()


class RecipeIngredient(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients',
        on_delete=models.CASCADE,
        verbose_name='ингридиенты',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='используется в рецептах',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Кол-во',
    )

    class Meta:
        models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='unique_ingredient_in_recipe'
        )
        verbose_name = 'Состав рецепта (ингридиенты)'
        verbose_name_plural = 'Составы рецептов (ингридиенты)'

    def __repr__(self):
        return f'{self.recipe}, {self.ingredient}, {self.amount}'

    def __str__(self):
        return self.__repr__()


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='cart',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_cart',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_recipe_in_cart'
        )
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorite_recipes',
        on_delete=models.CASCADE,
        verbose_name='Избранное пользователя',
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_favor',
        on_delete=models.CASCADE,
        verbose_name='Избранные рецепты',
    )

    class Meta:
        models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_recipe_in_favor'
        )
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        related_name='subscribed',
        on_delete=models.CASCADE,
        verbose_name='Подписки пользователя',
    )
    author = models.ForeignKey(
        User,
        related_name='subscribers',
        on_delete=models.CASCADE,
        verbose_name='Подписчики',
    )

    class Meta:
        models.UniqueConstraint(
            fields=['author', 'user'],
            name='unique_author_subscribe'
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
