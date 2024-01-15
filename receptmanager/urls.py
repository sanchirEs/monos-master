"""
monos receptmanager's URL Configuration
"""
from django.urls import path
from receptmanager.views import index as data, top as top_users, top_list, clear_xp, update_profile, rx_manager, notifications, notif_read, check_login, unread_notification

urlpatterns = [
    path('', data, name='data'),
    path('top_users', top_users, name='top-users'),
    path('top_list', top_list, name='top-list'),
    path('clear_xp', clear_xp, name='clear-xp'),
    path('update_profile', update_profile, name='update-profile'),
    path('rx_manager', rx_manager, name='rx-manager'),
    path('notifications', notifications, name='notifications'),
    path('notif_read', notif_read, name='notif-read'),
    path('check_login', check_login, name='check-login'),
    path('unread_notification', unread_notification, name='unread-notification'),
]
