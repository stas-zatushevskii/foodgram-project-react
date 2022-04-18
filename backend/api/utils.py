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
    ingredient_list = (
        IngredientInRecipe.objects.filter(recipe__id__in=recipes_list)
        .values("ingredients__name", "ingredients__measurement_unit")
        .annotate(amountsum=Sum("amount"))
    )
    need_to_buy = {"ingredients": ingredient_list}
    return need_to_buy

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
