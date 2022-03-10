from django.contrib import admin
from recipe.models import Ingredient, Recipe, Tag
from users.models import User

admin.site.register(Recipe)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name')
    search_fields = ('text',)
    list_filter = ('author', 'name', 'tag')
    readonly_fields = ('count_favorites',)

    def count_favorites(self, obj):
        return obj.favorites.count()

    count_favorites.short_description = 'Число добавлений в избранное'


admin.site.register(Tag)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')


admin.site.register(Ingredient)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
