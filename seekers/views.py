from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SeekerProfile
from .forms import BloodRequestForm, DonorSearchForm
from donors.models import DonorProfile
from hospitals.models import HospitalProfile
from blood_requests.models import BloodRequest


@login_required
def seeker_dashboard(request):
    if request.user.role != "seeker":
        messages.error(request, "Access denied.")
        return redirect("home")
    
    my_requests = BloodRequest.objects.filter(requester=request.user).order_by("-created_at")[:10]
    hospitals = HospitalProfile.objects.filter(verified=True)[:6]
    
    return render(request, "seekers/dashboard.html", {
        "my_requests": my_requests,
        "hospitals": hospitals,
    })


@login_required
def create_request(request):
    if request.method == "POST":
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.requester = request.user
            blood_request.save()
            messages.success(request, "Blood request submitted! Nearby donors will be notified.")
            return redirect("seeker_dashboard")
    else:
        form = BloodRequestForm()
    return render(request, "seekers/create_request.html", {"form": form})


@login_required
def my_requests(request):
    requests_list = BloodRequest.objects.filter(requester=request.user).order_by("-created_at")
    return render(request, "seekers/my_requests.html", {"requests_list": requests_list})


@login_required
def cancel_request(request, request_id):
    blood_request = get_object_or_404(BloodRequest, id=request_id, requester=request.user)
    blood_request.status = "cancelled"
    blood_request.save()
    messages.success(request, "Request cancelled.")
    return redirect("my_requests")


def donor_search(request):
    """Search for blood donors"""
    form = DonorSearchForm(request.GET or None)
    donors = DonorProfile.objects.filter(availability_status="available").select_related("user")
    
    if form.is_valid():
        if form.cleaned_data.get("blood_group"):
            donors = donors.filter(blood_group=form.cleaned_data["blood_group"])
        if form.cleaned_data.get("rh_factor"):
            donors = donors.filter(rh_factor=form.cleaned_data["rh_factor"])
        if form.cleaned_data.get("city"):
            donors = donors.filter(user__city__icontains=form.cleaned_data["city"])
    
    return render(request, "seekers/donor_search.html", {"form": form, "donors": donors})
