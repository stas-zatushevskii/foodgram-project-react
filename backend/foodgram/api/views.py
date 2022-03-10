from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse
from recipe.models import (Favorite, Follow, Ingredient, IngredientInRecipe,
                           Recipe, ShopingCard, Tag, User)
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST)

from .filters import IngredientSearchFilter, TagFavoritShopingFilter
from .permissions import IsAdminOrReadOnly, IsAdminUserReadOnly
from .serializers import (FollowSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeListSerializer,
                          TagSerializer)


class FollowerViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)
    queryset = Follow.objects.all()
    pagination_class = PageNumberPagination

    @action(
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
        name='subscribe',
        detail=True)
    def subscribe(self, request, pk):
        user = request.user
        try:
            author = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(status=HTTP_400_BAD_REQUEST)
        if self.action == 'POST':
            try:
                Follow.objects.create(user=user, author=author)
                return Response(status=HTTP_201_CREATED)
            except IntegrityError:
                return Response(status=HTTP_400_BAD_REQUEST)
        if self.action == 'DELETE':
            try:
                follow = Follow.objects.get(user=user, author=author)
                follow.delete()
                return Response(status=HTTP_200_OK)
            except IntegrityError:
                return Response(status=HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def list(self, request):
        tag = Tag.objects.all()
        serializer = self.get_serializer(tag, many=True)
        return Response(serializer.data)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_class = TagFavoritShopingFilter
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminUserReadOnly]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        else:
            return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise('Изменение чужого контента запрещено!')
        super(RecipeViewSet, self).perform_update(serializer)

    @action(
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
        name='favorite',
        detail=True)
    def favorite(self, request, pk):
        user = request.user
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            return Response(status=HTTP_400_BAD_REQUEST)
        if self.action == 'POST':
            try:
                Favorite.objects.create(user=user, recipe=recipe)
                return Response(status=HTTP_201_CREATED)
            except IntegrityError:
                return Response(status=HTTP_400_BAD_REQUEST)
        if self.action == 'DELETE':
            try:
                favorite = Favorite.objects.get(user=user, recipe=recipe)
                favorite.delete()
                return Response(status=HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
        name='shopping_cart',
        detail=True)
    def shopping_cart(self, request, pk):
        user = request.user
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            return Response(status=HTTP_400_BAD_REQUEST)
        if self.action == 'POST':
            try:
                ShopingCard.objects.create(user=user, id=pk)
                return Response(status=HTTP_201_CREATED)
            except Recipe.DoesNotExist:
                return Response(status=HTTP_400_BAD_REQUEST)
        if self.action == 'DELETE':
            try:
                recipe_in_list = ShopingCard.objects.get(
                    user=user, recipe=recipe
                )
                recipe_in_list.delete()
                return Response(status=HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated],
        name='download_shopping_cart',)
    def download_shopping_cart(self, request):
        user = request.user
        user_list = user.card.all()
        need_to_buy = get_ingredients(user_list)
        return download_file_response(need_to_buy, 'need_to_buy.txt')


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
    need_to_buy = []
    for item in ingredients_dict:
        need_to_buy.append(
            f'{item} - {ingredients_dict[item]["amount"]}',
            f'{ingredients_dict[item]["measurement_unit"]} \n'
        )
    return need_to_buy


def download_file_response(list_to_download, filename):
    response = HttpResponse(list_to_download, 'Content-Type: text/plain')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
