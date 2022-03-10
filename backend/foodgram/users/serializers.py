from django.db.models import CharField, EmailField
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.models import User


class CustomUserSerializer(UserSerializer):
    email = EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'role', 'is_subscribed',
        )
        model = User
