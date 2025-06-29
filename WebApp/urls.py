from django.contrib import admin
from django.urls import path, include  # добавили include

urlpatterns = [
    path('', include('main.urls')),  # добавили запятую для читаемости
]
