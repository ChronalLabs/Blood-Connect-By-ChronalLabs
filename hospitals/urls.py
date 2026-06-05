from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.hospital_dashboard, name="hospital_dashboard"),
    path("edit/", views.hospital_profile_edit, name="hospital_profile_edit"),
    path("blood-stock/", views.update_blood_stock, name="update_blood_stock"),
    path("employee/add/", views.add_employee, name="add_employee"),
    path("list/", views.hospital_list, name="hospital_list"),
    path("<int:pk>/", views.hospital_detail, name="hospital_detail"),
]
