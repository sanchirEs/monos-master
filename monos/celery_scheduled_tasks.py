"""
celery scheduled tasks
"""
from __future__ import absolute_import
from datetime import date, datetime, timedelta
from celery import task
from decimal import Decimal
import redis
import requests
from monosbot.bot_campaign_section import get_campaign_id_redis
from monosbot.celery_scheduled_tasks import fetch_post_data_lock, fetch_post_data, summurize_campaign
from receptmanager.models import ReceptManager, ReceptManagerData, ReceptManagerDataMonthly, ReceptManagerDataDaily, Sales, SalesLog
from store.models import StoreItem, ItemSaleWeekly, ItemSaleMonthly, ItemSaleDaily
from campaign.models import Campaign, CampaignAxis
from receptmanager.notification import send_single_notification

REDISPOOL = redis.ConnectionPool(path='/tmp/redis.sock', encoding="utf-8", decode_responses=True, connection_class=redis.UnixDomainSocketConnection)
# REDISPOOL = redis.ConnectionPool(host='localhost', port='6379', encoding="utf-8", decode_responses=True)

@task()
def each_minutes():
    """ 
    run each ten minutes
    """

    r = redis.Redis(connection_pool=REDISPOOL)

    campaign_id = get_campaign_id_redis(r, 0)
    campaign_beautician_id = get_campaign_id_redis(r, 1)

    print('Each minute running pharmacist...' + str(campaign_id))
    print('Each minute running beautician...' + str(campaign_beautician_id))

    if campaign_id:

        fetch_post_data_lock(campaign_id)

    if campaign_beautician_id:

        fetch_post_data_lock(campaign_beautician_id)


@task()
def each_ten():
    """
    each day method
    """
    from campaign.models import Campaign

    r = redis.Redis(connection_pool=REDISPOOL)

    if r.exists('each_ten_started'):

        print('Each ten exists. Returning ...')

        return

    print('Each ten Starting....')

    r.set('each_ten_started', 'OK', ex=1000)

    now = datetime.now()

    date_60_days_ago = now - timedelta(days=60)

    campaign_ids = list(Campaign.objects.filter(is_active=True, end_date__gt=now, start_date__gte=date_60_days_ago).values_list('id', flat=True)[:50])

    each_hour_on_campaign(campaign_ids, 0)


@task()
def each_hour_on_campaign(campaign_id_list, list_index):
    """ each day method """

    if len(campaign_id_list) > list_index:

        campaign_id = campaign_id_list[list_index]

        fetch_post_data(campaign_id)

        summurize_campaign(campaign_id)

        each_hour_on_campaign.delay(campaign_id_list, list_index + 1)

        print('Each ten finshed on ' + str(list_index))

    else:

        r = redis.Redis(connection_pool=REDISPOOL)

        r.delete('each_ten_started')

        print('Each ten finished....DELETED')


@task()
def summarize_weekly():
    """ summarize weekly rx data """

    rx_managers = ReceptManager.objects.all()

    today = date.today()

    #pylint: disable=W0613
    for manager in rx_managers:

        update_data = {
            'rx_xp':manager.rx_xp,
            'rx_level':manager.rx_level,
            'rx_weekly_xp':manager.rx_weekly_xp,
            'rx_coin_collected':manager.rx_coin_collected,
            'rx_coin_consumed':manager.rx_coin_consumed,
            'rx_coin_balance':manager.rx_coin_balance,
            'rx_coin_weekly_consumption':manager.rx_coin_weekly_consumption
        }

        ReceptManagerData.objects.update_or_create(manager_id=manager.id, date=today, defaults=update_data)

        manager.rx_weekly_xp = 0

        manager.rx_coin_weekly_consumption = 0

        manager.bum_coin_collected_weekly = 0
        manager.camp_coin_collected_weekly = 0

        manager.save()

    items = StoreItem.objects.all()

    for item in items:

        ItemSaleWeekly.objects.create(item=item, amount=item.sold_count_weekly, date=today)

        item.sold_count_weekly = 0

        item.save()

@task()
def summarize_daily():
    """ summarize daily rx data """

    rx_managers = ReceptManager.objects.all()

    today = date.today()

    #pylint: disable=W0613
    for manager in rx_managers:

        update_data = {
            'rx_xp':manager.rx_xp,
            'rx_level':manager.rx_level,
            'rx_daily_xp':manager.rx_daily_xp,
            'rx_coin_collected':manager.rx_coin_collected,
            'rx_coin_consumed':manager.rx_coin_consumed,
            'rx_coin_balance':manager.rx_coin_balance,
            'rx_coin_daily_consumption':manager.rx_coin_daily_consumption
        }

        ReceptManagerDataDaily.objects.update_or_create(manager_id=manager.id, date=today, defaults=update_data)

        manager.rx_daily_xp = 0

        manager.rx_coin_daily_consumption = 0

        manager.bum_coin_collected_daily = 0
        manager.camp_coin_collected_daily = 0

        manager.save()

    items = StoreItem.objects.all()

    for item in items:

        ItemSaleDaily.objects.create(item=item, amount=item.sold_count_daily, date=today)

        item.sold_count_daily = 0

        item.save()

    top_comment_user = ReceptManager.objects.filter(is_active=True).order_by('-rx_xp_on_comment', 'updated_date')[:10]

    top_advice_user = ReceptManager.objects.filter(is_active=True).order_by('-rx_xp_on_advice', 'updated_date')[:10]

    top_test_user = ReceptManager.objects.filter(is_active=True).order_by('-rx_xp_on_test', 'updated_date')[:10]

    top_like_user = ReceptManager.objects.filter(is_active=True).order_by('-rx_xp_on_like', 'updated_date')[:10]

    for manager in rx_managers:

        manager.badge_comment = False
        
        manager.badge_advice = False

        manager.badge_test = False

        manager.badge_like = False

        manager.badge_share = False

        manager.save()

    for manager in top_comment_user:

        manager.badge_comment = True

        manager.save()

    for manager in top_advice_user:

        manager.badge_advice = True

        manager.save()

    for manager in top_test_user:

        manager.badge_test = True

        manager.save()

    for manager in top_like_user:

        manager.badge_like = True

        manager.save()



@task()
def summarize_monthly():

    """ summarize weekly rx data """

    rx_managers = ReceptManager.objects.all()

    today = date.today()

    current_month = 0

    current_year = 0

    if today.day == 1:

        current_month = today.month - 1

        current_year = today.year

        if current_month == 0:

            current_month = 12

            current_year -= 1

    if not current_month:

        return

    #pylint: disable=W0613
    for manager in rx_managers:

        update_data = {
            'rx_xp':manager.rx_xp,
            'rx_level':manager.rx_level,
            'rx_coin_collected':manager.rx_coin_collected,
            'rx_coin_consumed':manager.rx_coin_consumed,
            'rx_coin_balance':manager.rx_coin_balance,
        }

        update_data['rx_monthly_xp'] = manager.rx_monthly_xp

        update_data['rx_coin_monthly_consumption'] = manager.rx_coin_monthly_consumption

        ReceptManagerDataMonthly.objects.update_or_create(manager_id=manager.id, year=current_year, month=current_month, defaults=update_data)

        manager.rx_coin_monthly_consumption = 0

        manager.rx_monthly_xp = 0

        manager.bum_coin_collected_monthly = 0
        manager.camp_coin_collected_monthly = 0

        manager.save()

    items = StoreItem.objects.all()

    for item in items:

        ItemSaleMonthly.objects.create(item=item, amount=item.sold_count_monthly, year=current_year, month=current_month)

        item.sold_count_monthly = 0

        item.save()

@task()
def buman_it_every_midnight(year = None, month = None, day = None):
    users = ReceptManager.objects.values_list('email', flat=True)
    products = CampaignAxis.objects.filter(campaign__is_active=True, campaign__coin_start_date__lte=datetime.now(), campaign__coin_end_date__gte=datetime.now())
    products_ids = products.values_list('axis_product_id', flat=True)
    users = list(users)
    products = list(products.values())
    products_ids = list(products_ids)

    r = redis.Redis(connection_pool=REDISPOOL)

    if year is None and month is None and day is None:
        today = datetime.today()
        # from_date = str(today.replace(hour=0, minute=0, second=1, microsecond=0))
        # to_date = str(today.replace(hour=23, minute=23, second=59, microsecond=0))
        from_date = str(today.strftime('%Y-%m-%d'))
        to_date = str(today.strftime('%Y-%m-%d'))
        lock = r.get('%s-%s-%s' % (today.year, today.month, today.day))
        year = today.year
        month = today.month
        day = today.day
    else:
        theDate = datetime(year=year, month=month, day=day)
        # from_date = str(theDate.replace(hour=0, minute=0, second=1, microsecond=0))
        # to_date = str(theDate.replace(hour=23, minute=23, second=59, microsecond=0))
        from_date = str(theDate.strftime('%Y-%m-%d'))
        today = datetime.today()
        to_date = str(today.strftime('%Y-%m-%d'))
        lock = r.get('%s-%s-%s' % (year, month, day))

    if lock:
        return {
            'error' : 'Coins are already collected!!!, requested date : ' + from_date
        }
    else:

        # params = {
        #     'USERS' : users,
        #     'PRODUCTS' : products_ids,
        #     'FROM_DATE' : from_date,
        #     'TO_DATE' : to_date
        # }

        params = {
            "params" : {   
                'username' : 'portalPharmTrade',
                'password' : '$portalPharmTrade;',
                'from_date' : from_date,
                'to_date' : to_date,
                'prod_ids' : products_ids,
                'user_emails' : users,
            }
        }

        print('sending request')
        response = requests.post('https://ub.bumanerp.mn/moil/api/posSalesDataGets', headers={"Content-Type": "application/json; charset=utf-8"}, json=params, verify=False)

        data = response.json()

        if 'error' in data:
            data = data['error']
            data['params_'] = params
            # return data

        if 'data' in data:
            data = data['data']            

        if 'result' in data:
            data = data['result']

        if 'duplicate' in data and data['duplicate'] is not None:
            for email in data['duplicate']:
                users.remove(email)

        if 'missing' in data and data['missing'] is not None:
            for email in data['missing']:
                users.remove(email)
        
        params['user_emails'] = users
        # params['username'] = 'portalPharmTrade',
        # params['password'] = '$portalPharmTrade;'
        if(data['status'] != 'success'):
            print('re-sending request')
            response = requests.post('https://ub.bumanerp.mn/moil/api/posSalesDataGets', headers={"Content-Type": "application/json; charset=utf-8"}, json=params, verify=False)

            data = response.json()
            if 'result' in data:
                data = data['result']
            # return data


        if 'result' in data:
            data = data['result']   
            
        if data['data']['sales'] is not None:

            sales = data['data']['sales']
            sales_fail_counter = 0

            for sale in sales:
                
                print('%s - %s' % (sale['user_email'], sale['product_id']))
                product = [prod for prod in products if prod.get('axis_product_id')==sale['product_id']][0]
                if not product['axis_xp_multiply']:
                    print('#### failed for axis_xp_multiply')
                    sales_fail_counter += 1
                else:
                    incoming_coin = Decimal(sale['qty']) * Decimal(product['axis_xp_multiply'])

                    print('coin : ' + str(incoming_coin))

                    manager = ReceptManager.objects.filter(email=sale['user_email']).first()
                    if manager:

                        sales_receptmanager, is_sales_receptmanager_created = Sales.objects.get_or_create(manager=manager, campaign_id=product['campaign_id'], campaign_axis_id=product['id'], defaults={'collected_coin' : int(incoming_coin), 'quantity': Decimal(sale['qty'])})

                        if not is_sales_receptmanager_created:
                            sales_receptmanager.collected_coin = int(sales_receptmanager.collected_coin) + incoming_coin
                            sales_receptmanager.quantity = Decimal(sale['qty'])
                            sales_receptmanager.save()

                        log = SalesLog(manager=manager, campaign_axis_id=product['id'])
                        log.quantity = Decimal(sale['qty'])
                        manager.rx_coin_collected += incoming_coin
                        manager.bum_coin_collected += incoming_coin
                        manager.bum_coin_collected_daily += incoming_coin
                        manager.bum_coin_collected_weekly += incoming_coin
                        manager.bum_coin_collected_monthly += incoming_coin
                        manager.save()

                        # send_single_notification.delay(manager.id, incoming_coin)

                        log.collected_coin = Decimal(incoming_coin)
                        log.save()
                    else:
                        print('#### failed for finding manager')
                        sales_fail_counter += 1
                
            print('total sales : ' + str(len(sales)))
            print('failed : ' + str(sales_fail_counter))
            print('total manager who had coins : ' + str(len(sales) - sales_fail_counter))

            r.incr('%s-%s-%s' % (year, month, day))
            return {
                'total_manager_who_had_coins' : str(len(sales) - sales_fail_counter),
                'total_sales' : str(len(sales)),
                'total_manager_who_had_coins' : str(len(sales) - sales_fail_counter)
            }
        else:
            print('!!! NO SALES !!!')
            return '!!! NO SALES !!!'



@task()
def buman_it():
    total = CampaignAxis.objects.select_related('campaign').values('id','axis_product_id', 'campaign_id', 'campaign__coin_start_date', 'axis_xp_multiply').filter(campaign__is_active=True).all().count()
    counter = 1
    for i in range(4):
        start = counter
        end = counter + 50
        counter += 50
        if end > total:
            run_buman_it.delay(start, total)
            break
        else:
            run_buman_it.delay(start, end)

@task()
def run_buman_it(start, end):
    print('buman it running %s - %s' % (start, end))
    users = ReceptManager.objects.values_list('email', flat=True)
    response_data = list()

    users = list(users)

    params = {
        'user_emails' : users,
        'username' : 'portalPharmTrade',
        'password' : '$portalPharmTrade;'
    }

    campaign_axis = CampaignAxis.objects.select_related('campaign').values('id','axis_product_id', 'campaign_id', 'campaign__coin_start_date', 'axis_xp_multiply').filter(campaign__is_active=True).all()[start:end]
    print(campaign_axis.count())

    for product in campaign_axis:
        print(product['campaign__coin_start_date'].strftime('%Y-%m-%d %H:%M:%S'))
        params['from_date'] = product['campaign__coin_start_date'].strftime('%Y-%m-%d %H:%M:%S')
        params['prod_ids'] = [product['axis_product_id']]

        # params['username'] = 'portalPharmTrade',
        # params['password'] = '$portalPharmTrade;',
        params['params'] = params
        print('request sending...')
        response = requests.post('https://ub.bumanerp.mn/moil/api/posSalesDataGets', headers={"Content-Type": "application/json; charset=utf-8"}, json=params, verify=False)
        print('request sent')

        data = response.json()
        if 'error' in data:
            data = data['error']
            data['params_'] = params
            # return data

        if 'result' in data:
            data = data['result']

        if 'data' in data:
            data = data['data']

        if 'duplicate' in data and data['duplicate'] is not None:
            for email in data['duplicate']:
                users.remove(email)

        if 'missing' in data and data['missing'] is not None:
            for email in data['missing']:
                users.remove(email)
        
        params['user_emails'] = users

        if(data['status'] != 'success'):
            print('re-sending request')
            response = requests.post('https://ub.bumanerp.mn/moil/api/posSalesDataGets', headers={"Content-Type": "application/json; charset=utf-8"}, json=params, verify=False)

            data = response.json()
            if 'error' in data:
                data = data['error']
                data['params_'] = params
                return data

            if 'result' in data:
                data = data['result']
        # print(params)

        if data['data']['sales'] is not None:

            sales = data['data']['sales']

            for sale in sales:

                manager = ReceptManager.objects.filter(email=sale['user_email']).first()
                # product = CampaignAxis.objects.filter(axis_product_id=sale['product_id']).first()

                if manager is not None and product is not None:
                    print('manager found %s' % manager.email)
                    incoming_coin = round(sale['qty'] * product['axis_xp_multiply'])

                    sales_receptmanager = Sales.objects.filter(manager=manager, campaign_id=product['campaign_id'], campaign_axis_id=product['id']).first()

                    added_difference = 0

                    log = SalesLog(manager=manager, campaign_axis_id=product['id'])
                    print('collected : ' + str(sales_receptmanager.collected_coin))
                    print('incoming : ' + str(incoming_coin))
                    if not sales_receptmanager:
                        print('creating sale for manager')
                        added_difference = incoming_coin
                        sales_receptmanager = Sales.objects.create(manager=manager, campaign_id=product['campaign_id'], campaign_axis_id=product['id'], collected_coin=int(incoming_coin), quantity=Decimal(sale['qty']))
                        log.quantity = Decimal(sale['qty'])
                    
                    elif sales_receptmanager.collected_coin < incoming_coin:
                        print('incoming coin: %d' % incoming_coin)
                        added_difference = incoming_coin - sales_receptmanager.collected_coin

                        log.quantity = Decimal(sale['qty']) - sales_receptmanager.quantity

                        sales_receptmanager.collected_coin = int(sales_receptmanager.collected_coin) + added_difference
                        sales_receptmanager.quantity = Decimal(sale['qty'])
                        sales_receptmanager.save()

                    if added_difference > 0:
                        print('addin coin to manager')
                        manager.rx_coin_collected += added_difference

                        manager.bum_coin_collected += added_difference

                        manager.bum_coin_collected_daily += added_difference

                        manager.bum_coin_collected_weekly += added_difference

                        manager.bum_coin_collected_monthly += added_difference

                        manager.save()

                        # send_single_notification.delay(manager.id, added_difference)

                        log.collected_coin = Decimal(added_difference)
                        print('log saving')
                        log.save()

    print('Buman IT running end...')

@task()
def update_fb_image():

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

    print("facebook image updated")
