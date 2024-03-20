from django.urls import path
from . import views

urlpatterns = [
    path('rockblock-receive/', views.receive_message, name='receive_message'),
]
