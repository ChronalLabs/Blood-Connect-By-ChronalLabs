from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import BloodRequest, DonorResponse
import json


def request_list(request):
    """Public emergency request board"""
    blood_group = request.GET.get("blood_group", "")
    rh_factor = request.GET.get("rh_factor", "")
    urgency = request.GET.get("urgency", "")
    
    requests_qs = BloodRequest.objects.filter(status="open").order_by("-created_at")
    if blood_group:
        requests_qs = requests_qs.filter(blood_group=blood_group)
    if rh_factor:
        requests_qs = requests_qs.filter(rh_factor=rh_factor)
    if urgency:
        requests_qs = requests_qs.filter(urgency_level=urgency)
    
    return render(request, "requests/list.html", {
        "requests_list": requests_qs,
        "blood_group": blood_group,
        "rh_factor": rh_factor,
    })


def request_detail(request, pk):
    blood_request = get_object_or_404(BloodRequest, pk=pk)
    responses = blood_request.donor_responses.all().select_related("donor")
    return render(request, "requests/detail.html", {
        "blood_request": blood_request,
        "responses": responses,
    })


def requests_json(request):
    """API endpoint for map markers"""
    requests_qs = BloodRequest.objects.filter(status="open").values(
        "id", "blood_group", "rh_factor", "hospital_name",
        "urgency_level", "latitude", "longitude", "city"
    )
    return JsonResponse(list(requests_qs), safe=False)
