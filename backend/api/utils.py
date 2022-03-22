from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)

from recipe.models import IngredientInRecipe, Recipe


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
