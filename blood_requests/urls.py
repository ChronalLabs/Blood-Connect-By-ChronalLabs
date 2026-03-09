from django.urls import path
from . import views

urlpatterns = [
    path("list/", views.request_list, name="request_list"),
    path("<int:pk>/", views.request_detail, name="request_detail"),
    path("api/requests.json", views.requests_json, name="requests_json"),
]
