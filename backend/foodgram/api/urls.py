from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FollowerViewSet, IngredientsViewSet, RecipeViewSet,
                    TagViewSet)

router = DefaultRouter()
app_name = 'api'

router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', FollowerViewSet)
router.register('ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
