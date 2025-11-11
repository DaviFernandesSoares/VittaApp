# appAgenda/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/slots/', views.slots_json, name='api_slots'),
    path('api/bookings/create/', views.create_booking, name='api_create_booking'),
]