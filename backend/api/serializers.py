from django.contrib.auth import get_user_model
from django.db.models import F
from django.forms import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.serializers import CustomUserSerializer
from recipe.models import (Follow, Ingredient, IngredientInRecipe,
                           Recipe, Tag)

User = get_user_model()

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


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
    author = CustomUserSerializer()
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        fields = (
            'id', 'ingredients', 'author', 'name', 'image',
            'text', 'tags', 'pub_date', 'cooking_time', 'is_favorited',
            'is_in_shopping_cart'

        )
        model = Recipe

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        fields = ('tags', 'ingredients', 'name',
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
            if type(ingredient.get('amount')) == str:
                if not ingredient.get('amount').isdigit():
                    raise serializers.ValidationError(
                        ('Количество ингредиента дольжно быть числом')
                    )
            if int(ingredient.get('amount')) <= 0:
                raise ValidationError(
                    'Количество ингредиента должно быть больше 0'
                )
            id = ingredient.get('id')
            if id in unique_ingredients:
                raise ValidationError(
                    'Ингредиент не должен повторяться'
                )
            unique_ingredients.add(id)
        if int(cooking_time) <= 0:
            raise ValidationError(
                'Время готовки должно быть больше 0'
            )
        data['ingredients'] = ingredients
        data['cooking_time'] = cooking_time
        return data

    def tag_ingredient_add(self, instance, **validated_data):
        tags = validated_data['tags']
        ingredients = validated_data['ingredients']

        for tag in tags:
            instance.tags.add(tag)

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
        tags = self.initial_data.get('tags')
        recipe = super().create(validated_data)
        return self.tag_ingredient_add(
            recipe, ingredients=ingredients, tags=tags)

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        tags = self.initial_data.get('tags')
        instance = self.tag_ingredient_add(
            instance, ingredients=ingredients, tags=tags)
        return super().update(instance, validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return ShortRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
