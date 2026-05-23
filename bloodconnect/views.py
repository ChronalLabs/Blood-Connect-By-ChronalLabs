"""
BloodConnect Core Views - Homepage, About, Contact
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from hospitals.models import HospitalProfile
from blood_requests.models import BloodRequest
import json, requests as http_requests
from django.conf import settings


def home(request):
    """Main landing page with hero, stats, and map"""
    hospitals = HospitalProfile.objects.filter(verified=True)[:10]
    recent_requests = BloodRequest.objects.filter(
        status='open'
    ).order_by('-created_at')[:5]
    
    # Stats for display
    from users.models import CustomUser
    from donors.models import DonorProfile
    stats = {
        'donors': DonorProfile.objects.count(),
        'hospitals': HospitalProfile.objects.filter(verified=True).count(),
        'requests_fulfilled': BloodRequest.objects.filter(status='fulfilled').count(),
        'lives_saved': BloodRequest.objects.filter(status='fulfilled').count(),
    }
    
    context = {
        'hospitals': hospitals,
        'recent_requests': recent_requests,
        'stats': stats,
    }
    return render(request, 'base/home.html', context)


def about(request):
    """About page"""
    return render(request, 'base/about.html')


def contact(request):
    """Contact form - submits to Google Sheets"""
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        message = request.POST.get('message', '')
        
        # Submit to Google Sheets via Apps Script Web App URL
        google_sheets_url = settings.GOOGLE_SHEETS_CREDENTIALS
        if google_sheets_url:
            try:
                payload = {
                    'name': name, 'email': email,
                    'phone': phone, 'message': message
                }
                http_requests.post(google_sheets_url, json=payload, timeout=5)
            except Exception:
                pass  # Fail silently
        
        messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
        return redirect('contact')
    
    return render(request, 'base/contact.html')
