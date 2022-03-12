from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from recipe.models import Recipe
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)
from recipe.models import IngredientInRecipe

def obj_create_or_dele(self, model, user, pk):
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            return Response(status=HTTP_400_BAD_REQUEST)
        if self.action == 'POST':
            try:
                model.objects.create(user=user, recipe=recipe)
                return Response(status=HTTP_201_CREATED)
            except IntegrityError:
                return Response(status=HTTP_400_BAD_REQUEST)
        if self.action == 'DELETE':
            obj = get_object_or_404(model, user=user, recipe=recipe)
            obj.delete()
            return Response(status=HTTP_204_NO_CONTENT)

def get_ingredients(recipes_list):
    ingredients_dict = {}
    amount = IngredientInRecipe.objects.filter(recipe=recipes_list.recipe).annotate('amount')
    name = IngredientInRecipe.objects.filter(recipe=recipes_list.recipe).annotate('name')
    measurement_unit = IngredientInRecipe.objects.filter(recipe=recipes_list.recipe).annotate('measurement_unit')
    if name not in ingredients_dict:
        ingredients_dict[name] = {
            'measurement_unit': measurement_unit,
            'amount': amount
            }
    else:
        ingredients_dict[name]['amount'] += amount
    need_to_buy = []
    for item in ingredients_dict:
        need_to_buy.append(
            f'{item} - {ingredients_dict[item]["amount"]}',
            f'{ingredients_dict[item]["measurement_unit"]} \n'
        )
    return need_to_buy