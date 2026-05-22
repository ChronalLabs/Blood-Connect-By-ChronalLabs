from django.urls import path

from .views import (
    add_employee,
    hospital_dashboard,
    hospital_detail,
    hospital_list,
    hospital_profile_edit,
    update_blood_stock,
)

app_name = "hospitals"

urlpatterns = [
    path("dashboard/", hospital_dashboard, name="dashboard"),
    path("edit/", hospital_profile_edit, name="edit_profile"),
    path("blood-stock/", update_blood_stock, name="blood_stock"),
    path("employee/add/", add_employee, name="add_employee"),
    path("list/", hospital_list, name="list"),
    path("<int:pk>/", hospital_detail, name="detail"),
]