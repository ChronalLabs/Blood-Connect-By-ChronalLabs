from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
    open_requests = BloodRequest.objects.filter(status="open").order_by("-created_at")[:10]
    employees = hospital.employees.all()
    
    return render(request, "hospitals/dashboard.html", {
        "hospital": hospital,
        "blood_stock": blood_stock,
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
