from django.urls import path
from . import views

urlpatterns = [
    # Add your views here
    path('', views.home, name='home'),
]