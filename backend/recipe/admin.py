from django.contrib.admin import ModelAdmin, register

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShopingCart, Tag)


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'color')


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    readonly_fields = ('count_favorites',)

    def count_favorites(self, obj):
        return obj.favorites.count()

    count_favorites.short_description = 'Число добавлений в избранное'


@register(IngredientInRecipe)
class IngredientAmountAdmin(ModelAdmin):
    pass


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    pass


@register(ShopingCart)
class CartAdmin(ModelAdmin):
    pass
