from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from quotes import views as quotes_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('quotes/', include('quotes.urls')),
    path('users/', include('users.urls')),
    path('', RedirectView.as_view(url='/quotes/', permanent=False)),
    path('author/<int:pk>/', quotes_views.author_detail_view, name='author_detail'),

]