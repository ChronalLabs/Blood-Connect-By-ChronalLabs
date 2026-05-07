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
    if request.user.role != "seeker":
        messages.error(request, "Access denied.")
        return redirect("home")

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
    if request.user.role != "seeker":
        messages.error(request, "Access denied.")
        return redirect("home")

    requests_list = BloodRequest.objects.filter(requester=request.user).order_by("-created_at")
    return render(request, "seekers/my_requests.html", {"requests_list": requests_list})


@login_required
def cancel_request(request, request_id):
    if request.user.role != "seeker":
        messages.error(request, "Access denied.")
        return redirect("home")

    blood_request = get_object_or_404(BloodRequest, id=request_id, requester=request.user)
    blood_request.status = "cancelled"
    blood_request.save()
    messages.success(request, "Request cancelled.")
    return redirect("my_requests")


def donor_search(request):
    """Search for blood donors using blood compatibility matrix"""
    form = DonorSearchForm(request.GET or None)
    donors = DonorProfile.objects.filter(availability_status="available").select_related("user")
    ranked_donors = None

    if form.is_valid():
        blood_group = form.cleaned_data.get("blood_group")
        rh_factor = form.cleaned_data.get("rh_factor")
        city = form.cleaned_data.get("city")
        radius_km = form.cleaned_data.get("radius_km") or 50

        if city:
            donors = donors.filter(user__city__icontains=city)

        if blood_group and rh_factor:
            from utils.blood_compatibility import get_compatible_donor_types, rank_donors
            from django.db.models import Q
            compatible_types = get_compatible_donor_types(blood_group, rh_factor)
            query = Q()
            for bg, rh in compatible_types:
                query |= Q(blood_group=bg, rh_factor=rh)
            donors = donors.filter(query)
            eligible = [d for d in donors if d.can_donate()]
            ranked_donors = rank_donors(eligible, blood_group, rh_factor, radius_km=radius_km)
        elif blood_group:
            donors = donors.filter(blood_group=blood_group)

    return render(request, "seekers/donor_search.html", {
        "form": form,
        "donors": donors if ranked_donors is None else None,
        "ranked_donors": ranked_donors,
    })
