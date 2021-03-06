from django.core.validators import MinValueValidator
from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=64,
        verbose_name='название'
    )
    measurement_unit = models.TextField(
        verbose_name='единица измерения'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'ингредиент'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        max_length=64,
        verbose_name='название'
    )
    color = models.CharField(
        max_length=7,
        default="#ffffff",
        verbose_name='цвет'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='слуг',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return f'{self.name}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='автор',
        related_name='recipes',
    )
    name = models.CharField(
        max_length=64,
        verbose_name='название'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='картинки'
    )
    text = models.TextField(
        help_text='введите текст рецепта',
        verbose_name='текст рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='recipe.IngredientInRecipe',
        related_name='recipes',
        verbose_name='ингредиент'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='тег'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления',
        validators=[MinValueValidator(
            1,
            'минимальное время приготовления 1 минута'
        )]
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self) -> str:
        return f'{self.name}'


class IngredientInRecipe(models.Model):
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='ингредиенты'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=(
            MinValueValidator(
                1, message='Минимальное количество ингридиентов 1'),),
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'ингредиенты'
        verbose_name_plural = 'ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredients', 'recipe'],
                name='unique_ingredient',
            )
        ]

    def __str__(self) -> str:
        return f'{self.ingredients.name} - {self.amount}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow',
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
        related_name='favorites',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'избранное'
        verbose_name_plural = 'избранные'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_user_recipe')
        ]

    def __str__(self):
        return f'{self.user}'


class ShopingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
        related_name='cart'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'корзина'
        verbose_name_plural = 'в корзине'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_cart_user')
        ]
