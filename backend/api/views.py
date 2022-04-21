from django.shortcuts import get_object_or_404
from django.db.models import BooleanField, Exists, OuterRef, Value
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_400_BAD_REQUEST,
                                HTTP_201_CREATED, HTTP_204_NO_CONTENT)

from recipe.models import (Favorite, Follow, Ingredient, Recipe, ShopingCart,
                           Tag)
from .filters import IngredientSearchFilter, TagFavoritShopingFilter
from .permissions import IsAdminIsOwnerOrReadOnly, IsAdminOrReadOnly
from .serializers import (FollowSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeListSerializer,
                          TagSerializer)
from .pagination import LimitPageNumberPagination
from .utils import download_file_response, get_ingredients, obj_create, obj_delete


User = get_user_model()

class FollowViewSet(UserViewSet):
    pagination_class = LimitPageNumberPagination

    @action(
        methods=['post'], detail=True, permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            return Response({
                'errors': 'Ошибка подписки, нельзя подписываться на себя'
            }, status=HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(user=user, author=author).exists():
            return Response({
                'errors': 'Ошибка подписки, вы уже подписаны на пользователя'
            }, status=HTTP_400_BAD_REQUEST)

        follow = Follow.objects.create(user=user, author=author)
        serializer = FollowSerializer(
            follow, context={'request': request}
        )
        return Response(serializer.data, status=HTTP_201_CREATED)

    @subscribe.mapping.delete
    def del_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response({
                'errors': 'Ошибка отписки, нельзя отписываться от самого себя'
            }, status=HTTP_400_BAD_REQUEST)
        follow = Follow.objects.filter(user=user, author=author)
        if not follow.exists():
            return Response({
                'errors': 'Ошибка отписки, вы уже отписались'
            }, status=HTTP_400_BAD_REQUEST)
        follow.delete()
        return Response(status=HTTP_204_NO_CONTENT)

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
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_class = TagFavoritShopingFilter
    pagination_class = LimitPageNumberPagination
    permission_classes = [IsAdminIsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.all()

        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(Favorite.objects.filter(
                    user=user, recipe__pk=OuterRef('pk'))
                ),
                is_in_shopping_cart=Exists(ShopingCart.objects.filter(
                    user=user, recipe__pk=OuterRef('pk'))
                )
            ) 
        else:
            queryset = queryset.annotate(
                is_favorited=Value(False, output_field=BooleanField()),
                is_in_shopping_cart=Value(False, output_field=BooleanField())
            )
        return queryset

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        user = request.user
        model = Favorite
        return obj_create(model=model, user=user, pk=pk)

    @favorite.mapping.delete
    def del_favorite(self, request, pk):
        user = request.user
        model = Favorite
        return obj_delete(model=model, user=user, pk=pk)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        user = request.user
        model = ShopingCart
        return obj_create(model=model, user=user, pk=pk)

    @shopping_cart.mapping.delete
    def del_shopping_cart(self, request, pk):
        user = request.user
        model = ShopingCart
        return obj_delete(model=model, user=user, pk=pk)

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        recipes_list = user.cart.all()
        need_to_buy = get_ingredients(recipes_list)
        return download_file_response(need_to_buy, 'need_to_buy.txt')
