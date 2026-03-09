"""
BloodConnect User Views - Registration, Login, Dashboard routing
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, EmergencyContact
from .forms import UserRegistrationForm, CustomLoginForm, UserProfileForm, EmergencyContactForm


def register(request):
    """User registration with role selection"""
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create role-specific profile
            role = form.cleaned_data["role"]
            if role == "donor":
                from donors.models import DonorProfile
                # Donor profile created in donor registration flow
                pass
            elif role == "seeker":
                from seekers.models import SeekerProfile
                SeekerProfile.objects.get_or_create(user=user)
            elif role == "hospital":
                from hospitals.models import HospitalProfile, BloodStock
                hp = HospitalProfile.objects.create(
                    user=user,
                    hospital_name=f"{user.get_full_name()} Hospital",
                    address=user.address or "",
                    city=user.city or "",
                    state=user.state or "",
                    pincode=user.pincode or "",
                    contact_number=user.phone_number or "",
                )
                BloodStock.objects.create(hospital=hp)
            
            login(request, user)
            messages.success(request, f"Welcome to BloodConnect, {user.first_name}!")
            return redirect("dashboard")
    else:
        form = UserRegistrationForm()
    
    return render(request, "users/register.html", {"form": form})


def user_login(request):
    """Login view"""
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get("next", "dashboard")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()
    
    return render(request, "users/login.html", {"form": form})


def user_logout(request):
    """Logout view"""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("home")


@login_required
def dashboard(request):
    """Route to role-specific dashboard"""
    user = request.user
    if user.role == "donor":
        return redirect("donor_dashboard")
    elif user.role == "seeker":
        return redirect("seeker_dashboard")
    elif user.role == "hospital":
        return redirect("hospital_dashboard")
    else:
        return redirect("home")


@login_required
def profile(request):
    """User profile view and edit"""
    user = request.user
    emergency_contact = getattr(user, "emergency_contact", None)
    
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        ec_form = EmergencyContactForm(
            request.POST,
            instance=emergency_contact
        )
        if form.is_valid():
            form.save()
            if ec_form.is_valid():
                ec = ec_form.save(commit=False)
                ec.user = user
                ec.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = UserProfileForm(instance=user)
        ec_form = EmergencyContactForm(instance=emergency_contact)
    
    return render(request, "users/profile.html", {
        "form": form, "ec_form": ec_form,
    })
