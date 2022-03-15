from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ListField

from users.serializers import UserSerializer
from recipe.models import (Favorite, Follow, Ingredient, IngredientInRecipe,
                           Recipe, ShopingCart, Tag)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug', 'recipes')
        model = Tag


class RecipeIngredientReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount', )


class RecipeListSerializer(serializers.ModelSerializer):
    author = UserSerializer
    ingredients = RecipeIngredientReadSerializer(many=True)
    tag = ListField(
        child=SlugRelatedField(
            slug_field='id',
            queryset=Tag.objects.all(),
        ),
    )
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        fields = (
            'id', 'ingredients', 'author', 'name', 'image',
            'text', 'tag', 'pub_date', 'cooking_time', 'is_favorited',
            'is_in_shopping_cart'

        )
        model = Recipe

    def get_favorite(self, instance, **validate_data):
        user = self.context['request'].user
        id = validate_data['id']
        recipe = get_object_or_404(Recipe, id=id)
        answer = Favorite.objects.filter(recipe=recipe, user=user).exists()
        instance.is_favorited.add(answer)
        return instance

    def get_shopping_cart(self, instance, **validate_data):
        user = self.context['request'].user
        id = validate_data['id']
        recipe = get_object_or_404(Recipe, id=id)
        answer = ShopingCart.objects.filter(recipe=recipe, user=user).exists()
        instance.is_in_shopping_cart.add(answer)
        return instance

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user, author=obj.author).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientReadSerializer(many=True)

    class Meta:
        fields = (
            'id', 'name', 'image',
            'text', 'tag', 'ingredients', 'cooking_time'
        )
        model = Recipe

    def validate(self, data):
        ingredients = data['ingredients']
        unique_ingredients = set()
        cooking_time = data['cooking_time']
        for ingredient in ingredients:
            if type(ingredient.get('amount')) == str:
                raise ValidationError(
                    'Неправильный формат количества ингредиентов, '
                    'ожидается int'
                )
            if ingredient.get('amount') <= 0:
                raise ValidationError(
                    'Количество ингредиента должно быть больше 0'
                )
            if ingredient.id in unique_ingredients:
                raise ValidationError(
                    'Ингредиент не должен повторяться'
                )
            unique_ingredients.add(ingredient.id)
        if cooking_time <= 0:
            raise ValidationError(
                'Время готовки должно быть больше 0'
            )
        data['ingredients'] = ingredients
        data['cooking_time'] = cooking_time
        return data

    def tag_ingredient_add(self, instance, **validated_data):
        tags = validated_data['tag']
        ingredients = validated_data['ingredients']

        for tag in tags:
            current_tag = Tag.objects.get_or_create(**tag)
        instance.tag.add(current_tag)

        for ingredients in ingredients:
            currents_ingredients = get_object_or_404(
                Ingredient, id=ingredients['id']
            )

            IngredientInRecipe.objects.get_or_create(
                ingredient=currents_ingredients,
                amount=ingredients['amount'],
                recipe=instance
                )
        return instance

    def create(self, validated_data):
        ingredient = validated_data.get('ingredients')
        tag = validated_data.get('tag')
        recipe = Recipe.objects.create(**validated_data)
        return self.tag_ingredient_add(recipe, Ingredients=ingredient, tag=tag)

    def update(self, instance, validated_data):
        ingredient = validated_data.get('ingredients')
        tag = validated_data.get('tag')
        instance = self.tag_ingredient_add(
            instance, Ingredients=ingredient, tag=tag
        )
        return super().update(instance, validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class ShopingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    image = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = ShopingCart


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user, author=obj.author).exists()

    def get_resicpes(self, obj):
        queryset = Recipe.objects.filter(author=obj.author)
        return ShortRecipeSerializer(queryset, many=True).data

    def get_recipe_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
