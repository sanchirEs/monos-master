"""
monos posts's URL Configuration
"""
from django.urls import path
from post.views import recent_posts

urlpatterns = [
    path('recentposts', recent_posts, name='recent-posts')
]
