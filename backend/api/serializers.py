from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ListField
from django.db.models import F

from users.serializers import CustomUserSerializer
from recipe.models import (Favorite, Follow, Ingredient, IngredientInRecipe,
                           Recipe, ShopingCart, Tag)
from drf_extra_fields.fields import Base64ImageField

User = get_user_model()

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
                       source='ingredients.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer
    ingredients = serializers.SerializerMethodField()
    tag = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        fields = (
            'id', 'ingredients', 'author', 'name', 'image',
            'text', 'tag', 'pub_date', 'cooking_time', 'is_favorited',
            'is_in_shopping_cart'

        )
        model = Recipe

    def get_favorite(self, obj):
        request = self.context.get('request')
        return Favorite.objects.filter(recipe=obj, user=request.user).exists()

    def get_shopping_cart(self, obj):
        request = self.context.get('request')
        return ShopingCart.objects.filter(recipe=obj,
                                           user=request.user).exists()

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    tag = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)

    class Meta:
        fields = ('id', 'tag', 'author', 'ingredients', 'name',
                  'image', 'text', 'cooking_time')
        model = Recipe

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        unique_ingredients = set()
        cooking_time = self.initial_data.get('cooking_time')
        for ingredient in ingredients:
            id = ingredient.get('id')
            if type(ingredient.get('amount')) == str:
                raise ValidationError(
                    'Неправильный формат количества ингредиентов, '
                    'ожидается int'
                )
            if ingredient.get('amount') <= 0:
                raise ValidationError(
                    'Количество ингредиента должно быть больше 0'
                )
            if id in unique_ingredients:
                raise ValidationError(
                    'Ингредиент не должен повторяться'
                )
            unique_ingredients.add(id)
        if cooking_time <= 0:
            raise ValidationError(
                'Время готовки должно быть больше 0'
            )
        data['ingredients'] = ingredients
        data['cooking_time'] = cooking_time
        return data

    def tag_ingredient_add(self, instance, **validated_data):
        tag = validated_data['tag']
        ingredients = validated_data['ingredients']

        for tags in tag:
            instance.tag.add(tags)

        for ingredient in ingredients:
            currents_ingredients = ingredient.get('id')
            currents_amount = ingredient.get('amount')

            IngredientInRecipe.objects.create(
                ingredients_id=currents_ingredients,
                amount=currents_amount,
                recipe=instance
                )
        return instance

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = self.initial_data.get('tag')
        recipe = super().create(validated_data)
        return self.tag_ingredient_add(
            recipe, ingredients=ingredients, tag=tags)

    def update(self, instance, validated_data):
        ingredients = validated_data.get('ingredients')
        tag = validated_data.get('tag')
        instance = self.tag_ingredient_add(
            instance, Ingredients=ingredients, tag=tag
        )
        return super().update(instance, validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    following = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = ('user', 'following')

