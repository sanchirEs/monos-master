"""
Monos Main Views

created by Mezorn LLC
"""
import json
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.shortcuts import render
from django.urls import reverse
from monos.common import get_current_campaign_data
from receptmanager.models import ReceptManager
from campaign.models import CampaignData
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

#pylint: disable=W0613
@login_required
@csrf_exempt
@require_GET
def index(request):
    """
    index page
    """

    user = request.user

    if not has_related_user(user):

        return render(request, 'index.html', {'status': 101, 'response':'RX manager not found'})

    rx_manager = user.receptmanagers

    last_six_campaign_data = CampaignData.objects.filter(manager=rx_manager)[:6]

    return render(request, 'index.html', {'status': 200, 'response':'Success', 'rx_manager':rx_manager, 'last_six_campaign':last_six_campaign_data})


def has_related_user(user):
    """ check if user has rx """

    has_user = False

    try:

        has_user = (user.receptmanagers is not None)

    except ReceptManager.DoesNotExist:

        pass

    return has_user


#pylint: disable=W0613
def parameters(request):
    """
    parameters test
    """
    print('-------parameters-------')
    print(request)
    # return HttpResponse(status=200)

    return HttpResponse(json.dumps(get_current_campaign_data()), content_type='application/json')


def login_view(request):

    """ login view """

    next = ""

    if request.method == 'GET':

        if request.GET.__contains__('next'):

            next = request.GET['next']

        return render(request, 'login.html', {
            'next' : next
        })

    elif request.method == 'POST':

        next = ""

        if request.POST.__contains__('next'):

            if request.POST['next'] != "" and request.POST['next'] != "/":

                next = request.POST['next']

        email = request.POST['email']

        password = request.POST['password']

        try:

            username = User.objects.get(email=email).email

        except User.DoesNotExist:

            username = None

        if username is not None:

            the_user = authenticate(username=username, password=password)

            remember_me = request.POST.get('remember_me', None)

            if remember_me:

                request.session.set_expiry(120)

            if the_user is not None:

                login(request, the_user)

                if next != "" and next != "/":

                    return HttpResponseRedirect(next)

                return HttpResponseRedirect(reverse('index'))

            else:
                return render(request, 'login.html', {'invalid': True, 'next' : next})

        else:
            return render(request, 'login.html', {'unknown': True, 'next' : next})


def logout_view(request):
    """ logging out """

    logout(request)

    return HttpResponseRedirect(reverse('monos-login'))


@login_required
@csrf_exempt
@require_GET
def ranking(request):
    """
    raniking page
    """
    user = request.user

    if not has_related_user(user):

        return render(request, 'ranking.html', {'status': 101, 'response':'RX manager not found'})

    rx_manager = user.receptmanagers

    return render(request, 'ranking.html', {'status': 200, 'response':'Success', 'rx_manager':rx_manager})
