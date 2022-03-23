from django.db.models import CharField, EmailField
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model

from recipe.models import Follow

User = get_user_model()

class CustomUserSerializer(UserSerializer):
    email = EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    is_subscribed = serializers.SerializerMethodField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    class Meta:
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'is_subscribed',
        )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()

class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'password',
            'username',
            'first_name',
            'last_name'
        )