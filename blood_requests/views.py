from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone
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
    responses = list(blood_request.donor_responses.all().select_related("donor"))
    for resp in responses:
        resp.unread_count = resp.chat_messages.filter(is_read=False).exclude(sender=request.user).count() if request.user.is_authenticated else 0
    ranked_donors = blood_request.get_ranked_donors(radius_km=50)

    # Determine whether the currently logged-in hospital can fulfill this request.
    can_hospital_fulfill = False
    hospital_stock_for_type = 0
    if (
        request.user.is_authenticated
        and request.user.role == "hospital"
        and blood_request.linked_hospital is not None
    ):
        try:
            hospital = request.user.hospital_profile
            if hospital.pk == blood_request.linked_hospital_id and blood_request.status == "open":
                from hospitals.services import get_stock_field_name
                blood_stock = getattr(hospital, "blood_stock", None)
                if blood_stock:
                    field_name = get_stock_field_name(
                        blood_request.blood_group, blood_request.rh_factor
                    )
                    if field_name:
                        hospital_stock_for_type = getattr(blood_stock, field_name, 0)
                        can_hospital_fulfill = hospital_stock_for_type >= blood_request.units_remaining
        except Exception:
            # Never crash the detail page due to missing profile data.
            pass

    return render(request, "requests/detail.html", {
        "blood_request": blood_request,
        "responses": responses,
        "ranked_donors": ranked_donors,
        "can_hospital_fulfill": can_hospital_fulfill,
        "hospital_stock_for_type": hospital_stock_for_type,
    })


def requests_json(request):
    """API endpoint for map markers"""
    requests_qs = BloodRequest.objects.filter(status="open").values(
        "id", "blood_group", "rh_factor", "hospital_name",
        "urgency_level", "latitude", "longitude", "city"
    )
    return JsonResponse(list(requests_qs), safe=False)


@login_required
def chat_room(request, response_id):
    donor_response = get_object_or_404(DonorResponse, id=response_id)
    seeker = donor_response.blood_request.requester
    donor = donor_response.donor

    if request.user != seeker and request.user != donor:
        raise PermissionDenied("You do not have access to this chat room.")

    # Mark other sender's messages as read
    donor_response.chat_messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    other_user = donor if request.user == seeker else seeker
    
    return render(request, "requests/chat_room.html", {
        "donor_response": donor_response,
        "blood_request": donor_response.blood_request,
        "other_user": other_user,
    })


@login_required
def chat_messages(request, response_id):
    donor_response = get_object_or_404(DonorResponse, id=response_id)
    seeker = donor_response.blood_request.requester
    donor = donor_response.donor

    if request.user != seeker and request.user != donor:
        raise PermissionDenied("You do not have access to this chat room.")

    if request.method == "GET":
        last_id = request.GET.get("last_id")
        messages_qs = donor_response.chat_messages.all()
        if last_id:
            try:
                messages_qs = messages_qs.filter(id__gt=int(last_id))
            except ValueError:
                pass
        
        # Mark other sender's messages as read upon being fetched
        donor_response.chat_messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

        data = []
        for msg in messages_qs:
            data.append({
                "id": msg.id,
                "sender_username": msg.sender.username,
                "sender_name": msg.sender.get_full_name() or msg.sender.username,
                "is_me": msg.sender == request.user,
                "message": msg.message,
                "created_at": timezone.localtime(msg.created_at).strftime("%I:%M %p"),
            })
        return JsonResponse({"messages": data}, safe=False)

    elif request.method == "POST":
        message_text = ""
        if request.content_type == "application/json":
            try:
                body = json.loads(request.body.decode("utf-8"))
                message_text = body.get("message", "").strip()
            except json.JSONDecodeError:
                pass
        else:
            message_text = request.POST.get("message", "").strip()

        if not message_text:
            return JsonResponse({"error": "Message cannot be empty."}, status=400)

        from .models import ChatMessage
        msg = ChatMessage.objects.create(
            donor_response=donor_response,
            sender=request.user,
            message=message_text
        )

        return JsonResponse({
            "id": msg.id,
            "sender_username": msg.sender.username,
            "sender_name": msg.sender.get_full_name() or msg.sender.username,
            "is_me": True,
            "message": msg.message,
            "created_at": timezone.localtime(msg.created_at).strftime("%I:%M %p"),
        })

    return JsonResponse({"error": "Method not allowed."}, status=405)


@login_required
def chat_list(request):
    from django.db.models import Q
    responses = DonorResponse.objects.filter(
        Q(donor=request.user) | Q(blood_request__requester=request.user)
    ).select_related("donor", "blood_request", "blood_request__requester").order_by("-created_at")
    
    chat_rooms = []
    for resp in responses:
        last_msg = resp.chat_messages.all().order_by("-created_at").first()
        unread = resp.chat_messages.filter(is_read=False).exclude(sender=request.user).count()
        other_user = resp.donor if request.user == resp.blood_request.requester else resp.blood_request.requester
        chat_rooms.append({
            "response": resp,
            "other_user": other_user,
            "last_message": last_msg,
            "unread_count": unread,
        })
        
    return render(request, "requests/chat_list.html", {"chat_rooms": chat_rooms})

