from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import DonorProfile, BloodDonationHistory
from .forms import DonorProfileForm, DonationHistoryForm
from blood_requests.models import BloodRequest, DonorResponse


def _blood_type_query(blood_types):
    query = Q()
    for bg, rh in blood_types:
        query |= Q(blood_group=bg, rh_factor=rh)
    return query


@login_required
def donor_dashboard(request):
    if request.user.role != "donor":
        messages.error(request, "Access denied.")
        return redirect("home")
    
    try:
        profile = request.user.donor_profile
    except DonorProfile.DoesNotExist:
        return redirect("donor_setup")
    
    from utils.blood_compatibility import get_compatible_recipient_types
    compatible_types = get_compatible_recipient_types(profile.blood_group, profile.rh_factor)
    open_requests = BloodRequest.objects.filter(
        _blood_type_query(compatible_types),
        status="open",
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
    if request.user.role != "donor":
        messages.error(request, "Only donors can respond to blood requests.")
        return redirect("home")

    blood_request = get_object_or_404(BloodRequest, id=request_id)
    donor_profile = get_object_or_404(DonorProfile, user=request.user)

    if blood_request.status != "open" or blood_request.units_remaining <= 0:
        messages.error(request, "This blood request is no longer open for donor responses.")
        return redirect("donor_dashboard")

    if donor_profile.availability_status != "available":
        messages.error(request, "Please mark yourself available before responding to a request.")
        return redirect("donor_dashboard")

    if not donor_profile.can_donate():
        messages.error(request, "You are still in the 90-day donation cooldown period.")
        return redirect("donor_dashboard")

    from utils.blood_compatibility import get_donation_priority
    is_compatible = get_donation_priority(
        donor_profile.blood_group,
        donor_profile.rh_factor,
        blood_request.blood_group,
        blood_request.rh_factor,
    ) > 0

    if not is_compatible:
        messages.error(request, "Your blood type is not compatible with this request.")
        return redirect("donor_dashboard")
    
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
    
    if city:
        donors = donors.filter(user__city__icontains=city)
    if blood_group and rh_factor:
        from utils.blood_compatibility import get_compatible_donor_types
        from django.db.models import Q
        compatible_types = get_compatible_donor_types(blood_group, rh_factor)
        query = Q()
        for bg, rh in compatible_types:
            query |= Q(blood_group=bg, rh_factor=rh)
        donors = donors.filter(query)
    elif blood_group:
        donors = donors.filter(blood_group=blood_group)

    return render(request, "donors/search.html", {
        "donors": donors,
        "blood_group": blood_group,
        "rh_factor": rh_factor,
        "city": city,
    })
