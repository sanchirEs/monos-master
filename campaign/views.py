""" campaign views """
import json
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from receptmanager.models import ReceptManager
from campaign.models import Campaign
from store.views import convert_date_to_string


def has_related_user(user):
    """ check if user has rx """

    has_user = False

    try:

        has_user = (user.receptmanagers is not None)

    except ReceptManager.DoesNotExist:

        pass

    return has_user


@login_required
@csrf_exempt
@require_GET
def campaign_hashes(request):
    """
    index page
    """

    user = request.user

    receptmanager = user.receptmanagers

    if not has_related_user(user):

        return HttpResponse(json.dumps({'status': 101, 'response':'RX manager not found'}), content_type='application/json')

    recent_campaign_hashes = list(Campaign.objects.filter(is_active=True, campaign_category=receptmanager.manager_type).values_list('product_hash','end_date')[:50])

    return HttpResponse(json.dumps(recent_campaign_hashes, default=convert_date_to_string), content_type='application/json')
