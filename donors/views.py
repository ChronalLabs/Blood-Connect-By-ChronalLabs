from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import DonorProfile, BloodDonationHistory
from .forms import DonorProfileForm, DonationHistoryForm
from blood_requests.models import BloodRequest, DonorResponse

from utils.blood_compatibility import (
    get_compatible_recipient_types,
    get_compatible_donor_types,
    get_donation_priority,
)


# ==========================================================
# Helpers
# ==========================================================
def build_blood_query(blood_types):
    query = Q()

    for blood_group, rh_factor in blood_types:
        query |= Q(
            blood_group=blood_group,
            rh_factor=rh_factor,
        )

    return query


def donor_only(view_func):
    """
    Custom donor access validation decorator
    """
    def wrapper(request, *args, **kwargs):
        if getattr(request.user, "role", None) != "donor":
            messages.error(request, "Access denied.")
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return login_required(wrapper)


# ==========================================================
# Dashboard
# ==========================================================
@donor_only
def donor_dashboard(request):
    profile = getattr(request.user, "donor_profile", None)

    if not profile:
        return redirect("donor_setup")

    compatible_types = get_compatible_recipient_types(
        profile.blood_group,
        profile.rh_factor,
    )

    open_requests = (
        BloodRequest.objects.filter(
            build_blood_query(compatible_types),
            status="open",
        )
        .order_by("-created_at")[:10]
    )

    # Combined master's chat loop tracking with your optimized query execution
    my_responses = list(
        DonorResponse.objects
        .filter(donor=request.user)
        .select_related("blood_request")[:10]
    )
    
    for resp in my_responses:
        resp.unread_count = (
            resp.chat_messages
            .filter(is_read=False)
            .exclude(sender=request.user)
            .count()
        )

    recent_donations = (
        profile.donation_history.all()[:5]
    )

    context = {
        "donor": profile,
        "open_requests": open_requests,
        "my_responses": my_responses,
        "recent_donations": recent_donations,
    }

    return render(request, "donors/dashboard.html", context)


# ==========================================================
# Setup Donor Profile
# ==========================================================
@donor_only
def donor_setup(request):
    if hasattr(request.user, "donor_profile"):
        return redirect("donor_dashboard")

    form = DonorProfileForm(
        request.POST or None
    )

    if request.method == "POST" and form.is_valid():
        profile = form.save(commit=False)
        profile.user = request.user
        profile.save()

        messages.success(
            request,
            "Donor profile created successfully!"
        )

        return redirect("donor_dashboard")

    return render(
        request,
        "donors/setup.html",
        {"form": form},
    )


# ==========================================================
# Edit Profile
# ==========================================================
@donor_only
def donor_profile_edit(request):
    profile = get_object_or_404(
        DonorProfile,
        user=request.user,
    )

    form = DonorProfileForm(
        request.POST or None,
        instance=profile,
    )

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(
            request,
            "Profile updated successfully!"
        )

        return redirect("donor_dashboard")

    # FIXED: Added missing 'request' parameter to prevent runtime crashes
    return render(
        request,
        "donors/edit_profile.html",
        {"form": form},
    )


# ==========================================================
# Add Donation History
# ==========================================================
@donor_only
def add_donation(request):
    form = DonationHistoryForm(
        request.POST or None
    )

    if request.method == "POST" and form.is_valid():
        donation = form.save(commit=False)

        profile = request.user.donor_profile

        donation.donor = profile
        donation.save()

        # Update donor stats
        profile.last_blood_donation_date = donation.donation_date
        profile.total_donations += 1
        profile.save()

        messages.success(
            request,
            "Donation added successfully!"
        )

        return redirect("donor_dashboard")

    return render(
        request,
        "donors/add_donation.html",
        {"form": form},
    )


# ==========================================================
# Respond to Blood Request
# ==========================================================
@donor_only
def respond_to_request(request, request_id):
    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id,
    )

    donor_profile = get_object_or_404(
        DonorProfile,
        user=request.user,
    )

    # Validate request
    if (
        blood_request.status != "open"
        or blood_request.units_remaining <= 0
    ):
        messages.error(
            request,
            "This request is closed."
        )
        return redirect("donor_dashboard")

    # Availability check
    if donor_profile.availability_status != "available":
        messages.error(
            request,
            "Please mark yourself available first."
        )
        return redirect("donor_dashboard")

    # Cooldown check
    if not donor_profile.can_donate():
        messages.error(
            request,
            "You are in the 90-day cooldown period."
        )
        return redirect("donor_dashboard")

    # Compatibility check
    compatible = (
        get_donation_priority(
            donor_profile.blood_group,
            donor_profile.rh_factor,
            blood_request.blood_group,
            blood_request.rh_factor,
        ) > 0
    )

    if not compatible:
        messages.error(
            request,
            "Blood type is not compatible."
        )
        return redirect("donor_dashboard")

    response, created = DonorResponse.objects.get_or_create(
        blood_request=blood_request,
        donor=request.user,
        defaults={"status": "interested"},
    )

    if created:
        messages.success(
            request,
            "Response submitted successfully!"
        )
    else:
        messages.info(
            request,
            "You already responded to this request."
        )

    return redirect("donor_dashboard")


# ==========================================================
# Search Donors
# ==========================================================
def search_donors(request):
    blood_group = request.GET.get("blood_group", "")
    rh_factor = request.GET.get("rh_factor", "")
    city = request.GET.get("city", "")

    donors = (
        DonorProfile.objects
        .filter(availability_status="available")
        .select_related("user")
    )

    # Filter city
    if city:
        donors = donors.filter(
            user__city__icontains=city
        )

    # Blood compatibility filter
    if blood_group and rh_factor:
        compatible_types = get_compatible_donor_types(
            blood_group,
            rh_factor,
        )

        donors = donors.filter(
            build_blood_query(compatible_types)
        )

    elif blood_group:
        donors = donors.filter(
            blood_group=blood_group
        )

    context = {
        "donors": donors,
        "blood_group": blood_group,
        "rh_factor": rh_factor,
        "city": city,
    }

    return render(
        request,
        "donors/search.html",
        context,
    )