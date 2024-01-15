"""monos URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from monos.views import index as main_page, parameters, login_view, logout_view, ranking
from monosmobile.views import change_password


urlpatterns = [
    path('', main_page, name='index'),
    path('parameters', parameters, name='parameters'),
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('admin/', admin.site.urls),
    path('bot/', include('monosbot.urls')),
    path('mobile/', include('monosmobile.urls')),
    path('login/', login_view, name='monos-login'),
    path('logout/', logout_view, name='monos-logout'),
    path('ranking/', ranking, name='monos-ranking'),
    path('rxmanager/', include('receptmanager.urls')),
    path('store/', include('store.urls')),
    path('campaign/', include('campaign.urls')),
    path('post/', include('post.urls')),
    path('api/', include('monosapi.urls')),
    path('change_password', change_password, name='change-password'),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    # path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
