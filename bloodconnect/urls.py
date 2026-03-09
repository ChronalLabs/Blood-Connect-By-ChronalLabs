"""
BloodConnect URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Homepage
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # User authentication and profiles
    path('users/', include('users.urls')),
    
    # App-specific URLs
    path('donors/', include('donors.urls')),
    path('seekers/', include('seekers.urls')),
    path('hospitals/', include('hospitals.urls')),
    path('requests/', include('blood_requests.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
