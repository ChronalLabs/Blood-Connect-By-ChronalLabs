from django.urls import path
from . import views

app_name = 'requests_app'

urlpatterns = [
    path('cancel/<int:pk>/', views.cancel_request, name='cancel'),
    path('fulfilled/<int:pk>/', views.mark_fulfilled, name='fulfilled'),
    path('emergency/', views.emergency_request, name='emergency'),
]
