"""BloodConnect - Requests Views"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BloodRequest


@login_required
def cancel_request(request, pk):
    req = get_object_or_404(BloodRequest, pk=pk, seeker=request.user)
    if req.status == 'open':
        req.status = 'cancelled'
        req.save()
        messages.success(request, 'Request cancelled.')
    return redirect('seekers:dashboard')


@login_required
def mark_fulfilled(request, pk):
    req = get_object_or_404(BloodRequest, pk=pk)
    if request.user == req.seeker or request.user.role in ['hospital', 'admin']:
        req.status = 'fulfilled'
        req.save()
        messages.success(request, 'Request marked as fulfilled. Thank you!')
    return redirect('dashboard')


def emergency_request(request):
    """Public emergency quick request form"""
    from .forms import BloodRequestForm
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to create a blood request.')
            return redirect('users:login')
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.seeker = request.user
            req.seeker_contact = request.user.phone_number
            req.urgency_level = 4  # Emergency
            req.save()
            messages.success(request, 'Emergency request submitted! Donors will be alerted.')
            return redirect('dashboard')
    else:
        from .forms import BloodRequestForm
        form = BloodRequestForm(initial={'urgency_level': 4})

    return render(request, 'home/emergency_request.html', {'form': form})
