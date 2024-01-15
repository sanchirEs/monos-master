"""
monosbot URL Configuration
"""
from django.urls import path
from monosbot.views import MonosBotView, MonosGroupBotView, last_response, response_msg, material_request, send_sms
from monosbot.views_settings import set_get_started, set_hello_text, white_list_domains
from monosbot.user_reg import location_user

urlpatterns = [
    path('a57e74a5ce6807554c2a93607d0876e62f61d2354e321c8ea7/', MonosBotView.as_view()),
    path('7e07138f1e36acec8eca541b1c601fb462603e015ed37aa630/', MonosGroupBotView.as_view()),
    path('last_response/', last_response),
    path('response_msg/', response_msg),
    path('set_get_started/', set_get_started),
    path('set_hello_text/', set_hello_text),
    path('white_list_domains/', white_list_domains),
    path('material_request/', material_request),
    path('send_sms/', send_sms),
    path('location_update/', location_user)
]
