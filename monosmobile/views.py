from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponse
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


from campaign.models import Campaign
from receptmanager.models import ReceptManager, Device, Sales, SalesLog, Notification
from monos.celery_scheduled_tasks import run_buman_it, buman_it, buman_it_every_midnight
from decimal import Decimal
import requests
import json
import csv

from receptmanager.notification import send_notification_by_managers, send_single_notification

from monos.celery_scheduled_tasks import update_fb_image as update_fb_image_task
from campaign.models import Campaign, CampaignAxis

from django.db.models import Sum

import redis

def convert_date_to_string(o):
    """date converter"""

    if isinstance(o, Decimal):

        return str(o)

    elif isinstance(o, date):

        return o.strftime('%Y-%m-%d')

    else:

        return None


@csrf_exempt
@require_GET
def reload_sales(request):
    # saleslog = SalesLog.objects.select_related('manager').filter(collected_date__startswith='2019-12-12')
    # for sl in saleslog:
    #     manager = sl.manager
    #     manager.rx_coin_collected -= sl.collected_coin

    #     manager.bum_coin_collected -= sl.collected_coin

    #     manager.bum_coin_collected_daily -= sl.collected_coin

    #     manager.bum_coin_collected_weekly -= sl.collected_coin

    #     manager.bum_coin_collected_monthly -= sl.collected_coin
    #     manager.save()

    #     sl.delete()

    if request.GET.__contains__('year') and request.GET.__contains__('month') and request.GET.__contains__('day'):
        response = buman_it_every_midnight(int(request.GET['year']), int(request.GET['month']), int(request.GET['day']))
    else:
        response = {
            'error' : 'params are must consists of year, month and day'
        }

    return HttpResponse(json.dumps(response, default=convert_date_to_string), content_type="application/json")


@csrf_exempt
@login_required
@require_GET
def revert(request):

    managers = ReceptManager.objects.all()

    for manager in managers:

        manager.rx_coin_collected = manager.rx_coin_collected - manager.bum_coin_collected

        manager.bum_coin_collected = 0 

        manager.bum_coin_collected_daily = 0

        manager.bum_coin_collected_weekly = 0

        manager.bum_coin_collected_monthly = 0

        manager.save()

    return HttpResponse(None, content_type="application/json")



@csrf_exempt
@require_GET
def update_fb_image(request):

    managers = ReceptManager.objects.all()

    for manager in managers:

        response = requests.get('https://graph.facebook.com/v3.1/'+manager.username+'/picture?access_token=DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD&redirect=0&width=200&height=200',
        headers={"Content-Type": "application/json; charset=utf-8"})
        
        data_dict = response.json()

        try:
            
            manager.avatar_link = data_dict['data']['url']

            manager.save()

        except Exception:

            pass

    # update_fb_image_task.delay()

    return HttpResponse(None)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Таны нууц үг амжилттай солигдлоо!')
            return redirect('/change_password')
        else:
            messages.error(request, 'Нууц үг буруу байна!')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {
        'form': form
    })

@login_required
@csrf_exempt
@require_GET
def n_token(request):

    if request.GET.__contains__('token') and not request.user.is_anonymous:

        device = Device.objects.update_or_create(manager=request.user.receptmanagers, token=request.GET['token'])

        data = {'status' : '200', 'description' : 'success'}

        return HttpResponse(json.dumps(data), content_type="application/json")
    
    else:

        data = {'status' : '500', 'description' : 'fail'}

        return HttpResponse(json.dumps(data), content_type="application/json")


@csrf_exempt
@require_GET
def mobilehtml(request):
    notification = Notification.objects.get(pk=request.GET['notification_id'])
    campaign = Campaign.objects.filter(product_hash=notification.content)

    data = {'notification_id': notification.id, 'url': notification.url, 'token' : request.GET['token']}

    if campaign:
        data['has_campaign'] = True
    else:
        data['has_campaign'] = False

    return render(request, 'mobile.html', data)

@login_required
@csrf_exempt
@require_POST
def share(request):
    if request.POST['has_campaign']:
        notification = Notification.objects.get(pk=request.POST['notification_id'])
        campaign = Campaign.objects.filter(product_hash=notification.content).first()
        rxmanager = request.user.receptmanagers
        if notification.is_shared:
            return HttpResponse(json.dumps({'status':121}), content_type="application/json")
        else:
            xp = campaign.add_on_share
            rxmanager.increase_share_xp_by(xp)
            notification.is_shared = True
            notification.save()

        return HttpResponse(json.dumps({'status':200}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'status':121}), content_type="application/json")

@csrf_exempt
@require_POST
def fix(request):

    sales = Sales.objects.all()
    SalesLog.objects.all().delete()
    bulk = list()
    for sale in sales:
        print(sale.quantity)
        log = SalesLog(manager=sale.manager, collected_coin=Decimal(sale.collected_coin), collected_date=sale.collected_date, campaign_axis=sale.campaign_axis, quantity=Decimal(sale.quantity))
        bulk.append(log)

    SalesLog.objects.bulk_create(bulk)
    return HttpResponse(json.dumps({'status':200}), content_type="application/json") 

@csrf_exempt
@require_POST
def user_create_csv(request):
    # """ register existings user's location and department """

    row = 0

    with open('monosbot/csv/managers-1.csv', newline='', encoding='utf-8') as csv_file:

        reader = csv.reader(csv_file, delimiter=',')
        for user_info in reader:

            fbid = user_info[0]
            department = user_info[1]
            location = user_info[2]
            title = user_info[3]
            email = user_info[4]
            phone = user_info[5]

            if department == '#$%':
                department = ''

            if phone == '#$%':
                phone = ''

            try:
                user = ReceptManager.objects.filter(facebook_id_messenger=fbid).first()
                user.department=department
                user.location=location
                user.title=title
                user.email=email
                user.phone=phone
                user.save()
            except Exception as e:
                pass

    with open('monosbot/csv/managers-2.csv', newline='', encoding='utf-8') as csv_file:

        reader = csv.reader(csv_file, delimiter=',')
        for user_info in reader:

            fbid = user_info[0]
            department = user_info[1]
            location = user_info[2]
            title = user_info[3]
            email = user_info[4]
            phone = user_info[5]

            if department == '#$%':
                department = ''

            if phone == '#$%':
                phone = ''

            try:
                user = ReceptManager.objects.filter(facebook_id_messenger=fbid).first()
                user.department=department
                user.location=location
                user.title=title
                user.email=email
                user.phone=phone
                user.save()
            except Exception as e:
                pass

    return HttpResponse(json.dumps({'status':200, 'total' : row}), content_type="application/json") 