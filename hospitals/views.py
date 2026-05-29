from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import HospitalProfile, BloodStock, HospitalEmployee
from .forms import HospitalProfileForm, BloodStockForm, HospitalEmployeeForm
from blood_requests.models import BloodRequest
import json


@login_required
def hospital_dashboard(request):
    if request.user.role != "hospital":
        messages.error(request, "Access denied.")
        return redirect("home")
    
    hospital = get_object_or_404(HospitalProfile, user=request.user)
    blood_stock, _ = BloodStock.objects.get_or_create(hospital=hospital)
    # Requests targeting this specific registered hospital (linked via FK).
    linked_requests = (
        BloodRequest.objects
        .filter(linked_hospital=hospital, status="open")
        .order_by("-created_at")[:10]
    )
    # Global open requests (excluding those already shown in linked_requests).
    open_requests = (
        BloodRequest.objects
        .filter(status="open")
        .exclude(linked_hospital=hospital)
        .order_by("-created_at")[:10]
    )
    employees = hospital.employees.all()
    
    return render(request, "hospitals/dashboard.html", {
        "hospital": hospital,
        "blood_stock": blood_stock,
        "linked_requests": linked_requests,
        "open_requests": open_requests,
        "employees": employees,
        "stock_json": json.dumps(blood_stock.as_dict()),
    })


@login_required
def hospital_profile_edit(request):
    hospital = get_object_or_404(HospitalProfile, user=request.user)
    
    if request.method == "POST":
        form = HospitalProfileForm(request.POST, request.FILES, instance=hospital)
        if form.is_valid():
            form.save()
            messages.success(request, "Hospital profile updated!")
            return redirect("hospital_dashboard")
    else:
        form = HospitalProfileForm(instance=hospital)
    
    return render(request, "hospitals/edit_profile.html", {"form": form, "hospital": hospital})


@login_required
def update_blood_stock(request):
    hospital = get_object_or_404(HospitalProfile, user=request.user)
    blood_stock, _ = BloodStock.objects.get_or_create(hospital=hospital)
    
    if request.method == "POST":
        form = BloodStockForm(request.POST, instance=blood_stock)
        if form.is_valid():
            form.save()
            messages.success(request, "Blood stock updated successfully!")
            return redirect("hospital_dashboard")
    else:
        form = BloodStockForm(instance=blood_stock)
    
    return render(request, "hospitals/blood_stock.html", {"form": form, "hospital": hospital})


@login_required
def add_employee(request):
    hospital = get_object_or_404(HospitalProfile, user=request.user)
    
    if request.method == "POST":
        form = HospitalEmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.hospital = hospital
            employee.save()
            messages.success(request, "Employee added!")
            return redirect("hospital_dashboard")
    else:
        form = HospitalEmployeeForm()
    
    return render(request, "hospitals/add_employee.html", {"form": form})


def hospital_list(request):
    """Public hospital listing with map"""
    hospitals = HospitalProfile.objects.filter(verified=True).select_related("blood_stock")
    
    hospitals_data = []
    for h in hospitals:
        if h.latitude and h.longitude:
            hospitals_data.append({
                "name": h.hospital_name,
                "lat": float(h.latitude),
                "lng": float(h.longitude),
                "address": h.address,
                "contact": h.contact_number,
                "blood_bank": h.blood_bank_available,
                "verified": h.verified,
            })
    
    return render(request, "hospitals/list.html", {
        "hospitals": hospitals,
        "hospitals_json": json.dumps(hospitals_data),
    })


def hospital_detail(request, pk):
    hospital = get_object_or_404(HospitalProfile, pk=pk, verified=True)
    blood_stock = getattr(hospital, "blood_stock", None)
    return render(request, "hospitals/detail.html", {
        "hospital": hospital,
        "blood_stock": blood_stock,
    })


def hospital_info_api(request, pk):
    """Public JSON endpoint returning basic info for a verified hospital.

    Used by the create-request form's auto-fill JavaScript to populate the
    plain-text hospital fields when a registered hospital is selected.
    Only verified hospitals are exposed.
    """
    hospital = get_object_or_404(HospitalProfile, pk=pk, verified=True)
    data = {
        "name": hospital.hospital_name,
        "address": hospital.address,
        "contact": hospital.contact_number,
        "city": hospital.city,
        "latitude": float(hospital.latitude) if hospital.latitude else None,
        "longitude": float(hospital.longitude) if hospital.longitude else None,
    }
    return JsonResponse(data)


@login_required
@require_POST
def fulfill_request(request, request_id):
    """POST-only view: fulfill a blood request from the hospital's stock.

    Security:
    - @login_required ensures only authenticated users can access this.
    - Role check ensures only hospital accounts can fulfill.
    - get_object_or_404(HospitalProfile, user=request.user) ensures a hospital
      can only use its own inventory, never another hospital's stock.
    - The service layer performs an atomic select_for_update to prevent races.
    """
    if request.user.role != "hospital":
        messages.error(request, "Access denied. Only hospital accounts can fulfill requests.")
        return redirect("home")

    hospital = get_object_or_404(HospitalProfile, user=request.user)
    blood_request = get_object_or_404(BloodRequest, pk=request_id)

    # Enforce that this hospital is the one linked to the request.
    if blood_request.linked_hospital_id != hospital.pk:
        messages.error(request, "This request is not linked to your hospital.")
        return redirect("request_detail", pk=request_id)

    success, message = blood_request.fulfill_from_hospital_stock(hospital)

    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)

    return redirect("request_detail", pk=request_id)
