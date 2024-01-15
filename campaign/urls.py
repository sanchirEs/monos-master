"""
monos campaign's URL Configuration
"""
from django.urls import path
from campaign.views import campaign_hashes

urlpatterns = [
    path('hashes', campaign_hashes, name='campaign-hashes')
]
