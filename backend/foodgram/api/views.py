from django.db import IntegrityError

from django.shortcuts import get_object_or_404
from recipe.models import (Favorite, Follow, Ingredient,
                           Recipe, ShopingCart, Tag, User)
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_400_BAD_REQUEST)

from .filters import IngredientSearchFilter, TagFavoritShopingFilter
from .permissions import IsAdminIsOwnerOrReadOnly, IsAdminOrReadOnly
from .serializers import (FollowSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeListSerializer,
                          TagSerializer)
from .utils import download_file_response, get_ingredients, obj_create_or_dele


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
                follow = get_object_or_404(Follow, author=author)
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
    permission_classes = [IsAdminIsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        else:
            return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        super(RecipeViewSet, self).perform_update(serializer)

    @action(
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
        name='favorite',
        detail=True)
    def favorite(self, request, pk):
        user = request.user
        model = Favorite
        return obj_create_or_dele(model=model, user=user, pk=pk)

    @action(
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
        name='shopping_cart',
        detail=True)
    def shopping_cart(self, request, pk):
        user = request.user
        model = ShopingCart
        return obj_create_or_dele(model=model, user=user, pk=pk)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated],
        name='download_shopping_cart',)
    def download_shopping_cart(self, request):
        user = request.user
        recipes_list = user.cart.all()
        need_to_buy = get_ingredients(recipes_list)
        return download_file_response(need_to_buy, 'need_to_buy.txt')
