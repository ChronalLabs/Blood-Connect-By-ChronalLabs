from blood_requests.models import ChatMessage
from django.db.models import Q

def unread_chat_count(request):
    """Global context processor providing total count of unread incoming chat messages."""
    if request.user.is_authenticated:
        unread_count = ChatMessage.objects.filter(
            is_read=False
        ).exclude(
            sender=request.user
        ).filter(
            Q(donor_response__donor=request.user) | Q(donor_response__blood_request__requester=request.user)
        ).count()
        return {'total_unread_chats': unread_count}
    return {'total_unread_chats': 0}
