import json

from models import Ingredient

from django.db import transaction


json_file_path = (
    'C:/app/recipe/ingredients.json')

with open(json_file_path, encoding='utf-8') as f:

    data = json.load(f)
    with transaction.atomic():
        for item in data:
            Ingredient.objects.create(
                name=item['name'],
                measurement_unit=item['measurement_unit'])
