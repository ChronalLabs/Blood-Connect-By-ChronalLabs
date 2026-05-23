from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.seeker_dashboard, name="seeker_dashboard"),
    path("request/", views.create_request, name="create_request"),
    path("my-requests/", views.my_requests, name="my_requests"),
    path("cancel/<int:request_id>/", views.cancel_request, name="cancel_request"),
    path("search/", views.donor_search, name="donor_search"),
]
