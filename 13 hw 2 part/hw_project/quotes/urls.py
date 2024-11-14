from django.urls import path
from . import views


app_name = 'quotes'  # Пространство имен для приложения quotes

urlpatterns = [
    path('', views.main, name='root'),  # Главная страница
    path('<int:page>/', views.main, name='root_paginate'),  # Пагинация на главной странице
    path('add_author/', views.AddAuthorView.as_view(), name='add_author'),  # Страница добавления автора
    path('add_quote/', views.AddQuoteView.as_view(), name='add_quote'),  # Страница добавления цитаты
    path('quote_list/', views.QuoteListView.as_view(), name='quote_list'),  # Страница со списком цитат
    path('author/<str:pk>/', views.author_detail_view, name='author_detail'),
    path('tag/<str:tag_name>/', views.tag_view, name='tag_detail'),
]


