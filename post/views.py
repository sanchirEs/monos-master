""" campaign views """
import json
from decimal import Decimal
from datetime import datetime, date
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.db.models import F
from receptmanager.models import ReceptManager
from post.models import Post

def has_related_user(user):
    """ check if user has rx """

    has_user = False

    try:

        has_user = (user.receptmanagers is not None)

    except ReceptManager.DoesNotExist:

        pass

    return has_user

def convert_date_to_string(o):
    """date converter"""

    if isinstance(o, Decimal):

        return str(o)

    elif isinstance(o, date):

        return o.strftime('%Y-%m-%d')

    else:

        return None


@login_required
@csrf_exempt
@require_GET
def recent_posts(request):
    """
    index page
    """

    user = request.user

    if not has_related_user(user):

        return HttpResponse(json.dumps({'status': 101, 'response':'RX manager not found'}), content_type='application/json')

    rxmanager = user.receptmanagers

    values = ['post_name',
              'facebook_id',
              'related_campaing__product_hash',
              'like_count',
              'like_count',
              'comment_count',
              'post_url',
              'image_url',
              'refetch_data',
              'created_date']

    recentposts = list(Post.objects.annotate(post_campaign=F('related_campaing__product_hash')).filter(related_campaing__is_active=True, related_campaing__campaign_category=rxmanager.manager_type).values(*values).order_by('-created_date')[:10])

    return HttpResponse(json.dumps(recentposts, default=convert_date_to_string), content_type='application/json')
