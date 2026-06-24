"""URL configuration for ruralcare project."""
from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path


def home(request):
    return render(request, 'home.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('healthcare/', include('healthcare.urls')),
    path('', home, name='home'),
]
