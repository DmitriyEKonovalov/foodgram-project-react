from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
        blank=False
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=16,
        unique=True,
        blank=False

    )
    slug = models.SlugField(
        verbose_name='Slug',
        unique=True,
        blank=False
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
        blank=False
    )
    measurement_unit = models.CharField(
        verbose_name='Цвет',
        max_length=20,
        blank=False

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
        blank=False
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Автор',
        on_delete=models.CASCADE,
        null=True,
    )
    text = models.TextField(
        verbose_name='Описание',
        blank=False
    )
    image = models.ImageField(
        upload_to='upload/',
        verbose_name='Картинка',
        blank=False
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги',
        blank=True,
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (в минутах)',
        blank=False
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        blank=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __repr__(self):
        return f'{self.name}'

    def __str__(self):
        return self.__repr__()


class RecipeIngredients(models.Model):

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
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Кол-во',
    )

    class Meta:
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
        verbose_name='Корзина',
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_cart',
        on_delete=models.CASCADE,
        verbose_name='Корзина',
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        unique_together = ('user', 'recipe')


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
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ('user', 'recipe')


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
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('user', 'author')

