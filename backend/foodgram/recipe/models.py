from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=64,
        blank=False
    )
    measurement_unit = models.TextField(
        blank=False
    )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        blank=False,
        max_length=64
    )
    color = models.CharField(
        max_length=7,
        default="#ffffff",
        blank=False
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='слуг',
        blank=False
    )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
        blank=False
    )
    name = models.CharField(
        blank=False,
        max_length=64
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=False
    )
    text = models.TextField(
        help_text='Введите текст рецепта',
        blank=False
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        related_name='recipes',
    )
    tag = models.ManyToManyField(
        Tag,
        blank=False,
        related_name='recipes'
    )
    pub_date = models.DateTimeField(
        "date published",
        auto_now_add=True
    )
    cooking_time = models.PositiveSmallIntegerField(
       validators=[MinValueValidator(
           1,
           'минимальное время приготовления 1 минута'
       )]
    )

    class Meta:
        ordering = ["-pub_date"]


class IngredientInRecipe(models.Model):
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amount'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amount'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиента'
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following'
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
        related_name='favorites'
    )


class ShopingCard(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='card'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
        related_name='cards'
    )
