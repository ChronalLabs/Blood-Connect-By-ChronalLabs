from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.donor_dashboard, name="donor_dashboard"),
    path("setup/", views.donor_setup, name="donor_setup"),
    path("edit/", views.donor_profile_edit, name="donor_profile_edit"),
    path("add-donation/", views.add_donation, name="add_donation"),
    path("respond/<int:request_id>/", views.respond_to_request, name="respond_to_request"),
    path("search/", views.search_donors, name="search_donors"),
]
