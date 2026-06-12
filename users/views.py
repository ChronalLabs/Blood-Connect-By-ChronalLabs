"""
BloodConnect User Views - Registration, Login, Dashboard routing
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache
from .models import CustomUser, EmergencyContact
from .forms import UserRegistrationForm, CustomLoginForm, UserProfileForm, EmergencyContactForm


LOGIN_ATTEMPT_LIMIT = 5
LOGIN_LOCKOUT_SECONDS = 15 * 60


def _client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _login_throttle_keys(request, username):
    normalized_username = (username or "").strip().lower()
    client_ip = _client_ip(request)
    keys = {
        "ip_attempts": f"login:attempts:ip:{client_ip}",
        "ip_lock": f"login:lock:ip:{client_ip}",
    }
    if normalized_username:
        keys["user_attempts"] = f"login:attempts:user:{normalized_username}"
        keys["user_lock"] = f"login:lock:user:{normalized_username}"
    return keys


def _login_is_locked(request, username):
    keys = _login_throttle_keys(request, username)
    return any(cache.get(lock_key) for lock_key in (
        keys["ip_lock"],
        keys.get("user_lock"),
    ) if lock_key)


def _record_login_failure(request, username):
    keys = _login_throttle_keys(request, username)
    counters = [keys["ip_attempts"]]
    if keys.get("user_attempts"):
        counters.append(keys["user_attempts"])

    for counter_key in counters:
        try:
            attempts = cache.incr(counter_key)
        except ValueError:
            cache.add(counter_key, 1, LOGIN_LOCKOUT_SECONDS)
            attempts = 1
        if attempts >= LOGIN_ATTEMPT_LIMIT:
            lock_key = counter_key.replace("attempts", "lock")
            cache.set(lock_key, True, LOGIN_LOCKOUT_SECONDS)


def _clear_login_throttle(request, username):
    keys = _login_throttle_keys(request, username)
    for key in (
        keys["ip_attempts"],
        keys["ip_lock"],
        keys.get("user_attempts"),
        keys.get("user_lock"),
    ):
        if key:
            cache.delete(key)


def _login_locked_response(request, template_name, form, message):
    messages.error(request, message)
    return render(request, template_name, {"form": form}, status=429)


def register(request):
    """User registration with role selection"""
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        form = UserRegistrationForm(request.POST, request.FILES)
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
                    hospital_name=form.cleaned_data.get("hospital_name"),
                    hospital_type=form.cleaned_data.get("hospital_type"),
                    registration_number=form.cleaned_data.get("registration_number"),
                    address=form.cleaned_data.get("address") or "",
                    city=form.cleaned_data.get("city") or "",
                    state=form.cleaned_data.get("state") or "",
                    pincode=form.cleaned_data.get("pincode") or "",
                    contact_number=form.cleaned_data.get("phone_number") or "",
                    emergency_contact=form.cleaned_data.get("emergency_contact") or "",
                    email=form.cleaned_data.get("email") or "",
                    website=form.cleaned_data.get("website") or "",
                    verification_document=form.cleaned_data.get("verification_document"),
                    latitude=form.cleaned_data.get("latitude"),
                    longitude=form.cleaned_data.get("longitude"),
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
        username = request.POST.get("username", "")
        if _login_is_locked(request, username):
            return _login_locked_response(
                request,
                "users/login.html",
                form,
                "Too many failed login attempts. Please try again later.",
            )
        if form.is_valid():
            user = form.get_user()
            _clear_login_throttle(request, username)
            login(request, user)
            if user.role == "hospital":
                messages.info(request, f"Welcome {user.first_name or user.username}! For hospital-specific features, consider using the Hospital Login.")
            else:
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get("next", "dashboard")
            return redirect(next_url)
        else:
            _record_login_failure(request, username)
            if _login_is_locked(request, username):
                return _login_locked_response(
                    request,
                    "users/login.html",
                    form,
                    "Too many failed login attempts. Please try again later.",
                )
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()
    
    return render(request, "users/login.html", {"form": form})


def hospital_login(request):
    """Hospital-specific login view"""
    if request.user.is_authenticated:
        if request.user.role == "hospital":
            return redirect("hospital_dashboard")
        else:
            messages.info(request, "You're already logged in. Please use the regular dashboard.")
            return redirect("dashboard")

    if request.method == "POST":
        form = CustomLoginForm(data=request.POST)
        username = request.POST.get("username", "")
        if _login_is_locked(request, username):
            return _login_locked_response(
                request,
                "users/hospital_login.html",
                form,
                "Too many failed login attempts. Please try again later.",
            )
        if form.is_valid():
            user = form.get_user()
            _clear_login_throttle(request, username)
            if user.role != "hospital":
                messages.error(request, "This login is for hospital accounts only. Please use the regular login.")
                return redirect("login")
            else:
                login(request, user)
                messages.success(request, f"Welcome to BloodConnect, {user.hospital_profile.hospital_name}!")
                next_url = request.GET.get("next", "hospital_dashboard")
                return redirect(next_url)
        else:
            _record_login_failure(request, username)
            if _login_is_locked(request, username):
                return _login_locked_response(
                    request,
                    "users/hospital_login.html",
                    form,
                    "Too many failed login attempts. Please try again later.",
                )
            messages.error(request, "Invalid hospital credentials.")
    else:
        form = CustomLoginForm()

    return render(request, "users/hospital_login.html", {"form": form})


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
def hospital_dashboard_redirect(request):
    """Hospital-specific dashboard redirect with validation"""
    if request.user.role != "hospital":
        messages.warning(request, "Access restricted to hospital users only.")
        return redirect("dashboard")
    return redirect("hospital_dashboard")


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
