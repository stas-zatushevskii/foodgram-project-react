from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)

from recipe.models import IngredientInRecipe, Recipe
from .serializers import ShortRecipeSerializer

def get_ingredients(recipes_list):
    ingredients_dict = {}
    for recipe in recipes_list:
        ingredients = IngredientInRecipe.objects.filter(recipe=recipe.recipe)
        for ingredient in ingredients:
            amount = ingredient.amount
            name = ingredient.ingredients.name
            measurement_unit = ingredient.ingredients.measurement_unit
            if name not in ingredients_dict:
                ingredients_dict[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                    }
            else:
                ingredients_dict[name]['amount'] += amount
    to_buy = []
    for item in ingredients_dict:
        to_buy.append(f'{item} - {ingredients_dict[item]["amount"]} '
                      f'{ingredients_dict[item]["measurement_unit"]} \n')
    return to_buy

def download_file_response(list_to_download, filename):
    response = HttpResponse(list_to_download, 'Content-Type: text/plain')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

def obj_create(model, user, pk):
    recipe = get_object_or_404(Recipe, id=pk)
    model.objects.create(user=user, recipe=recipe)
    serializer = ShortRecipeSerializer(recipe)
    return Response(serializer.data, status=HTTP_201_CREATED)

def obj_delete(model, user, pk):
    obj = model.objects.filter(user=user, recipe__id=pk)
    obj.delete()
    return Response(status=HTTP_204_NO_CONTENT)
