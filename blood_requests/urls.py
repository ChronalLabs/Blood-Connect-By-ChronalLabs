from django.urls import path
from . import views

urlpatterns = [
    path("list/", views.request_list, name="request_list"),
    path("<int:pk>/", views.request_detail, name="request_detail"),
    path("api/requests.json", views.requests_json, name="requests_json"),
    path("chat/<int:response_id>/", views.chat_room, name="chat_room"),
    path("chat/<int:response_id>/messages/", views.chat_messages, name="chat_messages"),
    path("chat/<int:response_id>/stream/", views.chat_stream, name="chat_stream"),
    path("chats/", views.chat_list, name="chat_list"),
]
