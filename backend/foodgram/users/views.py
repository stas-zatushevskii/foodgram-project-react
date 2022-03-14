from api.permissions import IsAdmin
from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializers import CustomUserSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'
    permission_classes = (IsAuthenticated, IsAdmin,)
    serializer_class = CustomUserSerializer
    search_fields = ('username',)
