from django.urls import path
from . import views

urlpatterns = [
    path('tutor/painel/', views.tutor_panel, name='tutor_panel'),
    path('tutor/recurring/create/', views.create_recurring, name='create_recurring'),
    path('api/slots/', views.slots_json, name='api_slots'),
    path('api/bookings/create/', views.create_booking, name='api_create_booking'),
]