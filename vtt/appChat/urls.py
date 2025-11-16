from django.urls import path
from . import views

app_name = 'appChat'

urlpatterns = [
    path('send/<int:user_id>/', views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('conversation/<int:user_id>/', views.conversation, name='conversation'),
    path('send/<int:user_id>/', views.send_message, name='send_message'),
    path('history/<int:user_id>/', views.message_history, name='message_history'),
]