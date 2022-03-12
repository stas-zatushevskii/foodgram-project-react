from django_filters import AllValuesMultipleFilter
from django_filters import rest_framework as filters
from django_filters.widgets import BooleanWidget
from recipe.models import Recipe
from rest_framework.filters import SearchFilter


class TagFavoritShopingFilter(filters.FilterSet):
    is_in_shopping_cart = filters.BooleanFilter(widget=BooleanWidget())
    is_favorited = filters.BooleanFilter(widget=BooleanWidget())
    tag = AllValuesMultipleFilter(field_name='tag__slug')
    author = AllValuesMultipleFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = [
            'author__id', 'tag__slug',
            'is_favorited', 'is_in_shopping_cart'
        ]


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'
