"""
monosapi's URL Configuration
"""
from django.urls import path, include
import oauth2_provider.views as oauth2_views
from monosapi.views import AxisProductManagerEndPoint, AxisCampaignEndPoint

oauth2_endpoint_views = [
    path('authorize', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    path('token', oauth2_views.TokenView.as_view(), name="token"),
    path('revoke-token', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

urlpatterns = [
    path('oauth/', include(oauth2_endpoint_views)),
    path('productmanager', AxisProductManagerEndPoint.as_view()),
    path('campaign', AxisCampaignEndPoint.as_view())
]
