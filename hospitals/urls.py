from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.hospital_dashboard, name="hospital_dashboard"),
    path("edit/", views.hospital_profile_edit, name="hospital_profile_edit"),
    path("blood-stock/", views.update_blood_stock, name="update_blood_stock"),
    path("employee/add/", views.add_employee, name="add_employee"),
    path("list/", views.hospital_list, name="hospital_list"),
    path("<int:pk>/", views.hospital_detail, name="hospital_detail"),
    # API: returns JSON for a verified hospital — used by create-request auto-fill JS.
    path("api/<int:pk>/info/", views.hospital_info_api, name="hospital_info_api"),
    # Fulfill a linked blood request from the hospital's stock inventory.
    path("requests/<int:request_id>/fulfill/", views.fulfill_request, name="fulfill_request"),
]
