from django.urls import path
from .views import *

urlpatterns = [
    path("chat/", chatbot_view, name="chatbot"),
]