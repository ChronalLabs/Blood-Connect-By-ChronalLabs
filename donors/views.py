from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import DonorProfile, BloodDonationHistory
from .forms import DonorProfileForm, DonationHistoryForm
from blood_requests.models import BloodRequest, DonorResponse


@login_required
def donor_dashboard(request):
    if request.user.role != "donor":
        messages.error(request, "Access denied.")
        return redirect("home")
    
    try:
        profile = request.user.donor_profile
    except DonorProfile.DoesNotExist:
        return redirect("donor_setup")
    
    open_requests = BloodRequest.objects.filter(
        blood_group=profile.blood_group,
        rh_factor=profile.rh_factor,
        status="open"
    ).order_by("-created_at")[:10]
    
    my_responses = DonorResponse.objects.filter(donor=request.user).select_related("blood_request")[:10]
    recent_donations = profile.donation_history.all()[:5]
    
    return render(request, "donors/dashboard.html", {
        "donor": profile,
        "open_requests": open_requests,
        "my_responses": my_responses,
        "recent_donations": recent_donations,
    })


@login_required
def donor_setup(request):
    """Initial donor profile setup"""
    if request.user.role != "donor":
        return redirect("home")
    
    if request.method == "POST":
        form = DonorProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Donor profile created successfully!")
            return redirect("donor_dashboard")
    else:
        form = DonorProfileForm()
    
    return render(request, "donors/setup.html", {"form": form})


@login_required
def donor_profile_edit(request):
    """Edit donor medical profile"""
    profile = get_object_or_404(DonorProfile, user=request.user)
    
    if request.method == "POST":
        form = DonorProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Medical profile updated!")
            return redirect("donor_dashboard")
    else:
        form = DonorProfileForm(instance=profile)
    
    return render(request, "donors/edit_profile.html", {"form": form})


@login_required
def add_donation(request):
    if request.method == "POST":
        form = DonationHistoryForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user.donor_profile
            donation.save()
            # Update last donation date
            profile = request.user.donor_profile
            profile.last_blood_donation_date = donation.donation_date
            profile.total_donations += 1
            profile.save()
            messages.success(request, "Donation recorded!")
            return redirect("donor_dashboard")
    else:
        form = DonationHistoryForm()
    return render(request, "donors/add_donation.html", {"form": form})


@login_required
def respond_to_request(request, request_id):
    blood_request = get_object_or_404(BloodRequest, id=request_id)
    donor_profile = get_object_or_404(DonorProfile, user=request.user)
    
    response, created = DonorResponse.objects.get_or_create(
        blood_request=blood_request,
        donor=request.user,
        defaults={"status": "interested"}
    )
    
    if created:
        messages.success(request, f"You have expressed interest in donating for this request. The requester will contact you.")
    else:
        messages.info(request, "You have already responded to this request.")
    
    return redirect("donor_dashboard")


def search_donors(request):
    """Public donor search"""
    blood_group = request.GET.get("blood_group", "")
    rh_factor = request.GET.get("rh_factor", "")
    city = request.GET.get("city", "")
    
    donors = DonorProfile.objects.filter(
        availability_status="available"
    ).select_related("user")
    
    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    if rh_factor:
        donors = donors.filter(rh_factor=rh_factor)
    if city:
        donors = donors.filter(user__city__icontains=city)
    
    return render(request, "donors/search.html", {
        "donors": donors,
        "blood_group": blood_group,
        "rh_factor": rh_factor,
        "city": city,
    })
