from django.urls import path
from django.urls.conf import include

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
