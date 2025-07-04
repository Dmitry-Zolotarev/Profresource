from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include  # добавили include

urlpatterns = [
    path('', include('main.urls')),  # добавили запятую для читаемости
]
