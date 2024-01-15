"""
Monos ReceptManager's Views

created by Mezorn LLC
"""
import json
from decimal import Decimal
from datetime import date, datetime, timedelta
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.db.models import F
# from django.shortcuts import render
# from django.urls import reverse
from receptmanager.models import ReceptManager, ReceptManagerData, ReceptManagerDataDaily, Notification, Device
from campaign.models import CampaignData

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

def xp_to_nextlevel(value, arg):
    """ xp next filter """

    quotient = 0

    try:

        current_xp = int(value)

        current_level = int(arg)

        quotient = int(2**(current_level-1)-1)*200+100-current_xp

    except  (ValueError, ZeroDivisionError):

        pass

    return quotient


@login_required
@csrf_exempt
@require_GET
def index(request):
    """
    index page
    """

    user = request.user

    if not has_related_user(user):

        return HttpResponse(json.dumps({'status': 101, 'response':'RX manager not found'}), content_type='application/json')

    rx_manager = user.receptmanagers

    data_dict = dict()

    rx_manager_data = dict()

    rx_manager_data['username'] = user.username

    rx_manager_data['email'] = user.email

    rx_manager_data['first_name'] = rx_manager.first_name

    rx_manager_data['last_name'] = rx_manager.last_name

    rx_manager_data['fullname'] = rx_manager.fullname

    rx_manager_data['role'] = rx_manager.role

    rx_manager_data['facebook_id'] = rx_manager.facebook_id

    rx_manager_data['facebook_id_workspace'] = rx_manager.facebook_id_workspace

    rx_manager_data['facebook_id_messenger'] = rx_manager.facebook_id_messenger

    rx_manager_data['phone'] = rx_manager.phone

    rx_manager_data['address'] = rx_manager.address

    rx_manager_data['facebook'] = rx_manager.facebook

    rx_manager_data['about'] = rx_manager.about

    rx_manager_data['avatar_link'] = rx_manager.avatar_link

    rx_manager_data['manager_url'] = rx_manager.manager_url

    rx_manager_data['is_active'] = rx_manager.is_active

    rx_manager_data['rx_xp'] = rx_manager.rx_xp

    rx_manager_data['rx_level'] = rx_manager.rx_level

    rx_manager_data['rx_weekly_xp'] = rx_manager.rx_weekly_xp

    rx_manager_data['rx_monthly_xp'] = rx_manager.rx_monthly_xp

    rx_manager_data['rx_coin_collected'] = rx_manager.rx_coin_collected

    rx_manager_data['rx_coin_consumed'] = rx_manager.rx_coin_consumed

    rx_manager_data['rx_coin_balance'] = rx_manager.rx_coin_balance

    rx_manager_data['rx_coin_from_sales'] = rx_manager.bum_coin_collected

    rx_manager_data['rx_coin_from_campaign'] = rx_manager.camp_coin_collected

    rx_manager_data['rx_coin_weekly_consumption'] = rx_manager.rx_coin_weekly_consumption

    rx_manager_data['rx_coin_monthly_consumption'] = rx_manager.rx_coin_monthly_consumption

    rx_manager_data['rx_xp_on_comment'] = rx_manager.rx_xp_on_comment

    rx_manager_data['rx_xp_on_advice'] = rx_manager.rx_xp_on_advice

    rx_manager_data['rx_xp_on_test'] = rx_manager.rx_xp_on_test

    rx_manager_data['rx_xp_on_like'] = rx_manager.rx_xp_on_like

    rx_manager_data['title'] = rx_manager.title

    rx_manager_data['department'] = rx_manager.department

    rx_manager_data['location'] = rx_manager.location

    rx_manager_data['badge_like'] = rx_manager.badge_like

    rx_manager_data['badge_test'] = rx_manager.badge_test

    rx_manager_data['badge_comment'] = rx_manager.badge_comment

    rx_manager_data['badge_advice'] = rx_manager.badge_advice

    rx_manager_data['badge_share'] = rx_manager.badge_share

    rx_manager_data['xp_to_nextlevel'] = xp_to_nextlevel(rx_manager.rx_xp, rx_manager.rx_level)

    data_dict['rx_manager'] = rx_manager_data

    last_six_campaign_data = CampaignData.objects.filter(manager=rx_manager)[:6]

    ls_campaign_list = list()

    for campaign_data in last_six_campaign_data:

        ls_campaign_data = dict()

        ls_campaign_data['campaign'] = campaign_data.related_campaign.product_name

        ls_campaign_data['is_test_given'] = campaign_data.is_test_given

        ls_campaign_data['xp_on_comment'] = campaign_data.xp_on_comment

        ls_campaign_data['xp_on_like'] = campaign_data.xp_on_like

        ls_campaign_data['xp_on_test'] = campaign_data.xp_on_test

        ls_campaign_data['xp_on_advise'] = campaign_data.xp_on_advise

        ls_campaign_data['xp_on_share'] = campaign_data.xp_on_share

        ls_campaign_data['xp_total'] = campaign_data.xp_total

        ls_campaign_data['result_on_test'] = campaign_data.result_on_test

        ls_campaign_data['advise_url'] = campaign_data.advise_url

        ls_campaign_data['liked_posts'] = campaign_data.liked_posts

        ls_campaign_data['commented_posts'] = campaign_data.commented_posts

        ls_campaign_data['shared_posts'] = campaign_data.shared_posts

        ls_campaign_list.append(ls_campaign_data)

    data_dict['last_six_campaign'] = ls_campaign_list

    last_six_week = ReceptManagerData.objects.filter(manager=rx_manager)[:6]

    ls_six_week_list = list()

    for week_data in last_six_week:

        ls_week_data = dict()

        ls_week_data['date'] = convert_date_to_string(week_data.date)

        ls_week_data['rx_xp'] = week_data.rx_xp

        ls_week_data['rx_level'] = week_data.rx_level

        ls_week_data['rx_weekly_xp'] = week_data.rx_weekly_xp

        ls_week_data['rx_coin_collected'] = week_data.rx_coin_collected

        ls_week_data['rx_coin_consumed'] = week_data.rx_coin_consumed

        ls_week_data['rx_coin_balance'] = week_data.rx_coin_balance

        ls_week_data['rx_coin_weekly_consumption'] = week_data.rx_coin_weekly_consumption

        ls_six_week_list.append(ls_week_data)

    data_dict['last_six_week'] = ls_six_week_list

    # last week by day
    last_week_daily = ReceptManagerDataDaily.objects.filter(manager=rx_manager)[:7]

    ls_week_list = list()

    for day_data in last_week_daily:

        ls_week_data = dict()

        ls_week_data['date'] = convert_date_to_string(day_data.date)

        ls_week_data['rx_xp'] = day_data.rx_xp

        ls_week_data['rx_level'] = day_data.rx_level

        ls_week_data['rx_daily_xp'] = day_data.rx_daily_xp

        ls_week_data['rx_coin_collected'] = day_data.rx_coin_collected

        ls_week_data['rx_coin_consumed'] = day_data.rx_coin_consumed

        ls_week_data['rx_coin_balance'] = day_data.rx_coin_balance

        ls_week_data['rx_coin_weekly_consumption'] = day_data.rx_coin_daily_consumption

        ls_week_list.append(ls_week_data)

    data_dict['last_week_daily'] = ls_week_list

    top_user = ReceptManager.objects.order_by('-rx_xp', 'updated_date').first()

    top_xp_user = ReceptManagerDataDaily.objects.filter(manager_id=top_user.id)[:7]

    top_xp_user_list = list()

    for day_data in top_xp_user:

        ls_week_data = dict()

        ls_week_data['date'] = convert_date_to_string(day_data.date)

        ls_week_data['rx_xp'] = day_data.rx_xp

        ls_week_data['rx_level'] = day_data.rx_level

        ls_week_data['rx_daily_xp'] = day_data.rx_daily_xp

        ls_week_data['rx_coin_collected'] = day_data.rx_coin_collected

        ls_week_data['rx_coin_consumed'] = day_data.rx_coin_consumed

        ls_week_data['rx_coin_balance'] = day_data.rx_coin_balance

        ls_week_data['rx_coin_weekly_consumption'] = day_data.rx_coin_daily_consumption

        top_xp_user_list.append(ls_week_data)

    data_dict['top_user_last_week_daily'] = top_xp_user_list

    return HttpResponse(json.dumps(data_dict, default=convert_date_to_string), content_type='application/json')


#pylint: disable=W0613
@login_required
@csrf_exempt
@require_GET
def top(request):
    """
    get top service
    """
    user = request.user

    rxmanager = user.receptmanagers

    top_comment_user = ReceptManager.objects.filter(is_active=True, manager_type=rxmanager.manager_type).order_by('-rx_xp_on_comment', 'updated_date').first()

    top_advice_user = ReceptManager.objects.filter(is_active=True, manager_type=rxmanager.manager_type).order_by('-rx_xp_on_advice', 'updated_date').first()

    top_test_user = ReceptManager.objects.filter(is_active=True, manager_type=rxmanager.manager_type).order_by('-rx_xp_on_test', 'updated_date').first()

    top_like_user = ReceptManager.objects.filter(is_active=True, manager_type=rxmanager.manager_type).order_by('-rx_xp_on_like', 'updated_date').first()

    top_total_users = ReceptManager.objects.filter(is_active=True, manager_type=rxmanager.manager_type).order_by('-rx_xp', 'updated_date')[:5]

    data = dict()

    top_comment_data = dict()

    top_comment_data['first_name'] = top_comment_user.first_name

    top_comment_data['last_name'] = top_comment_user.last_name

    top_comment_data['title'] = top_comment_user.title

    top_comment_data['department'] = top_comment_user.department

    top_comment_data['location'] = top_comment_user.location

    top_comment_data['avatar_link'] = top_comment_user.avatar_link

    top_comment_data['order_xp'] = top_comment_user.rx_xp_on_comment

    top_comment_data['order_name'] = 'rx_xp_on_comment'

    data['top_comment'] = top_comment_data

    top_advice_data = dict()

    top_advice_data['first_name'] = top_advice_user.first_name

    top_advice_data['last_name'] = top_advice_user.last_name

    top_advice_data['avatar_link'] = top_advice_user.avatar_link

    top_advice_data['order_xp'] = top_advice_user.rx_xp_on_advice

    top_advice_data['title'] = top_advice_user.title

    top_advice_data['department'] = top_advice_user.department

    top_advice_data['location'] = top_advice_user.location

    top_advice_data['order_name'] = 'rx_xp_on_advice'

    data['top_advice'] = top_advice_data

    top_test_data = dict()

    top_test_data['first_name'] = top_test_user.first_name

    top_test_data['last_name'] = top_test_user.last_name

    top_test_data['avatar_link'] = top_test_user.avatar_link

    top_test_data['order_xp'] = top_test_user.rx_xp_on_test

    top_test_data['title'] = top_test_user.title

    top_test_data['department'] = top_test_user.department

    top_test_data['location'] = top_test_user.location

    top_test_data['order_name'] = 'rx_xp_on_test'

    data['top_test'] = top_test_data

    top_like_data = dict()

    top_like_data['first_name'] = top_like_user.first_name

    top_like_data['last_name'] = top_like_user.last_name

    top_like_data['avatar_link'] = top_like_user.avatar_link

    top_like_data['order_xp'] = top_like_user.rx_xp_on_like

    top_like_data['title'] = top_like_user.title

    top_like_data['department'] = top_like_user.department

    top_like_data['location'] = top_like_user.location

    top_like_data['order_name'] = 'rx_xp_on_like'

    data['top_like'] = top_like_data

    top_xp_users = list()

    for rx in top_total_users:

        top_xp_data = dict()

        top_xp_data['id'] = rx.id

        top_xp_data['first_name'] = rx.first_name

        top_xp_data['last_name'] = rx.last_name

        top_xp_data['avatar_link'] = rx.avatar_link

        top_xp_data['order_xp'] = rx.rx_xp

        top_xp_data['title'] = rx.title

        top_xp_data['department'] = rx.department

        top_xp_data['location'] = rx.location

        top_xp_data['badge_like'] = rx.badge_like

        top_xp_data['badge_test'] = rx.badge_test

        top_xp_data['badge_comment'] = rx.badge_comment

        top_xp_data['badge_advice'] = rx.badge_advice

        top_xp_data['badge_share'] = rx.badge_share

        top_xp_users.append(top_xp_data)

    data['top_xp_users'] = {'users':top_xp_users, 'order_name':'rx_xp'}

    return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

ALLOWED_KEYWORDS = ['rx_xp', 'rx_xp_on_comment', 'rx_xp_on_advice', 'rx_xp_on_test', 'rx_xp_on_like', 'rx_weekly_xp', 'rx_monthly_xp']

#pylint: disable=W0613
@login_required
@csrf_exempt
@require_GET
def top_list(request):
    """
    get top list service
    """
    rx_manager = request.user.receptmanagers

    page = 1

    if request.GET.__contains__('page'):

        try:

            page = int(request.GET['page'])

            if not page:

                page = 1

        except ValueError:

            page = 1

    order = 'rx_xp'

    if request.GET.__contains__('order'):

        try:

            order_raw = request.GET['order']

            if order_raw in ALLOWED_KEYWORDS:

                order = order_raw

        except ValueError:

            pass

    page_length = 20

    data = dict()

    values = [
        'id',
        'first_name',
        'last_name',
        'avatar_link',
        'title',
        'department',
        'location',
        'badge_advice',
        'badge_share',
        'badge_like',
        'badge_test',
        'badge_comment',
        order
    ]

    query_order = '-' + order

    all_managers = ReceptManager.objects.filter(is_active=True, manager_type=rx_manager.manager_type).annotate(order_xp=F(order)).values(*values).order_by(query_order, 'updated_date')

    manager = ReceptManager.objects.filter(id=rx_manager.id, manager_type=rx_manager.manager_type).annotate(order_xp=F(order)).values(*values).order_by(query_order, 'updated_date').first()
 
    start = (page - 1) * page_length

    end = page* page_length

    all_managers_count = all_managers.count()

    managers = all_managers[start:end]

    list_managers = list()

    manager = dict(manager)  

    for idx, m in enumerate(all_managers):
        m = dict(m)
        if m['id'] == rx_manager.id:
            manager['current_manager_number'] = idx + 1
            manager['rx_xp'] = m[order]

    for idx, m in enumerate(managers):
        m = dict(m)
        m['order_num'] = (idx + 1) + ((page - 1) * page_length)
        m['rx_xp'] = m[order]
        list_managers.append(m)

    data['users'] = list_managers

    data['count'] = all_managers_count

    data['manager'] = manager

    data['pagecount'] = int((all_managers_count -1)/page_length) + 1 if all_managers_count > 0 else 0

    data['page'] = page

    data['status'] = 200

    return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

@login_required
@csrf_exempt
@require_GET
def rx_manager(request):

    try:

        if request.GET.__contains__('manager_id'):

            manager_id = int(request.GET['manager_id'])

        else:

            manager_id = request.user.receptmanagers.id    

    except ValueError:

        manager_id = request.user.receptmanagers.id


    manager = ReceptManager.objects.filter(id=manager_id).first()

    if manager is not None:

        manager_dict = dict()

        manager_dict['id'] = manager.id
        manager_dict['first_name'] = manager.first_name
        manager_dict['last_name'] = manager.last_name
        manager_dict['rx_level'] = manager.rx_level
        manager_dict['rx_xp'] = manager.rx_xp
        manager_dict['badge_advice'] = manager.badge_advice
        manager_dict['badge_comment'] = manager.badge_comment
        manager_dict['badge_like'] = manager.badge_like
        manager_dict['badge_share'] = manager.badge_share
        manager_dict['badge_test'] = manager.badge_test
        manager_dict['location'] = manager.location
        manager_dict['avatar_link'] = manager.avatar_link
        manager_dict['xp_to_nextlevel'] = xp_to_nextlevel(manager.rx_xp, manager.rx_level)
        manager_dict['rx_coin_balance'] = manager.rx_coin_balance
        manager_dict['bum_coin_collected'] = manager.bum_coin_collected
        manager_dict['bum_coin_collected_daily'] = manager.bum_coin_collected_daily
        manager_dict['bum_coin_collected_weekly'] = manager.bum_coin_collected_weekly
        manager_dict['bum_coin_collected_monthly'] = manager.bum_coin_collected_monthly
        manager_dict['camp_coin_collected'] = manager.camp_coin_collected
        manager_dict['camp_coin_collected_daily'] = manager.camp_coin_collected_daily
        manager_dict['camp_coin_collected_weekly'] = manager.camp_coin_collected_weekly
        manager_dict['camp_coin_collected_monthly'] = manager.camp_coin_collected_monthly

        return HttpResponse(json.dumps(manager_dict, default=convert_date_to_string), content_type='application/json')

    else:

        return HttpResponse(None, content_type='application/json')



@login_required
@csrf_exempt
@require_GET
def clear_xp(request):
    all_managers = ReceptManager.objects.filter(rx_level=1)

    for manager in all_managers:
        manager.rx_coin_collected=0
        manager.save()
    
    return HttpResponse(json.dumps(None), content_type='application/json')


@login_required
@csrf_exempt
@require_GET
def update_profile(request):
    all_managers = ReceptManager.objects.all()
    for manager in all_managers:
        manager.avatar_link = 'https://graph.facebook.com/v2.11/'+manager.username+'/picture?access_token=DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD'
        manager.save()
    
    return HttpResponse(json.dumps(None), content_type='application/json')


@login_required
@csrf_exempt
@require_POST
def notifications(request):

    user = request.user
    
    rx_manager = user.receptmanagers

    page = 1

    if request.POST.__contains__('page'):

        try:

            page = int(request.POST['page'])

            if not page:

                page = 1

        except ValueError:

            page = 1

    page_length = 20

    values = [
        'id',
        'created_date',
        'updated_date',
        'is_public',
        'read',
        'type',
        'content',
        'manager_id',
        'title',
        'url',
    ]


    notifications = Notification.objects.filter(manager_id=rx_manager.id).values(*values).order_by('-created_date')

    start = (page - 1) * page_length

    end = page* page_length

    notification_count = notifications.count()

    notifications = notifications[start:end]

    notifications = list(notifications)

    n_data = list()

    for n in notifications:

        date = datetime.strptime(str(n['created_date'].date()), '%Y-%m-%d')

        nDate = datetime.today().date()

        if str(date.date()) == str(nDate - timedelta(days=1)):

            date = "өчигдөр"

        elif str(date.date()) == str(nDate):

            date = str(n['created_date'].hour) + ":" + str(n['created_date'].minute)

        else:

            date = str(date.month) + " сарын " + str(date.day)
        
        n['date'] = date

        n_data.append(n)

    data = dict()

    data['notifications'] = n_data

    data['count'] = notification_count

    data['pagecount'] = int((notification_count -1)/page_length) + 1 if notification_count > 0 else 0

    data['page'] = page

    data['status'] = 200

    return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')


@login_required
@csrf_exempt
@require_GET
def notif_read(request):

    data = dict()

    id = 0

    if request.GET.__contains__('id'):

        try:

            id = int(request.GET['id'])

            if not id:

                data['status'] = 404

                data['description'] = 'Id is empty'

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')    

        except ValueError:

            data['status'] = 404

            data['description'] = 'Parse Error'

            return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

        notification = Notification.objects.get(pk=id)

        notification.read = 1

        notification.save()

        data['status'] = 200

        data['description'] = 'success'

        return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')


    else:

        data['status'] = 404

        data['description'] = 'Id is missing'

        return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

@csrf_exempt
@require_GET
def check_login(request):

    data = dict()

    if not request.user.is_anonymous:

        data['status'] = 200

        data['description'] = 'Token is active'

        return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

    else:

        data['status'] = 404

        data['description'] = 'Token expired'

        return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

@csrf_exempt
@require_GET
@login_required
def unread_notification(request):

    unread_count = Notification.objects.filter(manager=request.user.receptmanagers, read=0).count()

    data = {'count' : unread_count}

    return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

    