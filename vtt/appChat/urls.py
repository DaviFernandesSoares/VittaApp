from django.urls import path
from . import views

app_name = 'appChat'

urlpatterns = [
    path('send/<int:user_id>/', views.send_message, name='send_message'),
]