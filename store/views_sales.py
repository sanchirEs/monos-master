"""
Store Sales Views

created by Mezorn LLC
"""
import json
from decimal import Decimal
from datetime import datetime, date
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from receptmanager.models import ReceptManager
from store.models import StoreItem, SalesData
from monoscontrol.models import MonosControl


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
@require_POST
def buy_and_confirm(request):
    """
    buys item index page
    """

    control = MonosControl.objects.first()

    if not control.store_status:

        data = {'response': 'Store action is disabled', 'status': 108, 'readable_response': 'Дэлгүүрээс худалдан хийх боломжгүй байна'}
        return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

    user = request.user

    if not has_related_user(user):

        return HttpResponse(json.dumps({'status': 101, 'response':'RX manager not found'}), content_type='application/json')

    manager = user.receptmanagers

    try:

        json_dict = json.loads(request.body.decode('utf-8'))

        item_id = int(json_dict['item'])

    except json.JSONDecodeError:

        data = {'response': 'JSON error', 'status': 102, 'readable_response': 'Хүсэлтэнд алдаа гарлаа'}

        return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

    except KeyError:

        data = {'response': 'Key missing', 'status': 103, 'readable_response': 'Хүсэлтэнд алдаа гарлаа'}

        return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

    except ValueError:

        data = {'response': 'Invalid value', 'status': 104, 'readable_response': 'Хүсэлтэнд алдаа гарлаа'}

        return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

    item = StoreItem.objects.filter(id=item_id, is_active=True).first()

    if item.required_level > manager.rx_level:

        data = {'response': 'Less level', 'status': 106, 'readable_response': 'Энэ барааг худалдаж авахад таны Level хүрэхгүй байна.'}

        return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')


    if item is None:

        data = {'response': 'Item not found (either deleted or non existing)', 'status': 105, 'readable_response': 'Энэ бараа байхгүй байна'}

        return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

    amount = 1

    try:

        amount = int(json_dict['amount'])

        if amount <= 0:

            data = {'response': 'Invalid amount', 'status': 105, 'readable_response': 'Тоо ширхэг буруу байна'}

            return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

    except KeyError:

        amount = 1

    except ValueError:

        data = {'response': 'Item not found (either deleted or non existing)', 'status': 106, 'readable_response': 'Тоо ширхэг буруу байна'}

        return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

    total_amount = amount*item.item_price

    if total_amount > manager.rx_coin_balance:

        data = {'response': 'Inadequate balance', 'status': 107, 'readable_response': 'Таны мойл хүрэлцэхгүй байна'}

        return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

    manager.consume_coin(total_amount)

    item.add_sold_count(amount)

    SalesData.objects.create(item=item, manager=manager, amount=amount, total=total_amount, status=1)

    data = {
        'status' : 200,
        'response' : 'Success',
        'readable_response': 'Таны хүсэлт амжилттай хийгдлээ'}

    return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')
