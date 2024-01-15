"""
Store Views

created by Mezorn LLC
"""
import json
from decimal import Decimal
from datetime import datetime, date
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.shortcuts import render
from django.db.models import F
from receptmanager.models import ReceptManager
from store.models import StoreCategory, StoreItem


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


#pylint: disable=W0613
@login_required
@csrf_exempt
@require_GET
def index(request):
    """
    store index page
    """

    user = request.user

    if not has_related_user(user):

        return HttpResponse(json.dumps({'status': 101, 'response':'RX manager not found'}), content_type='application/json')

    rx_manager = user.receptmanagers

    data = dict()

    data['rx_manager'] = rx_manager

    data['rx_coin_balance'] = rx_manager.rx_coin_balance

    values = [
        'id',
        'category_name',
        'category_icon'
    ]

    categories = list(StoreCategory.objects.annotate(icon=F('category_icon')).filter(is_active=True).values(*values).order_by('category_order', 'updated_date'))

    data['categories'] = categories

    return render(request, 'store.html', data)


@login_required
@csrf_exempt
@require_GET
def index_data(request):

    user = request.user

    if not has_related_user(user):

        return HttpResponse(json.dumps({'status': 101, 'response':'RX manager not found'}), content_type='application/json')

    rx_manager = user.receptmanagers

    data = dict()

    data['rx_manager'] = rx_manager.first_name

    data['rx_coin_balance'] = rx_manager.rx_coin_balance

    values = [
        'id',
        'category_name',
        'category_icon'
    ]

    categories = list(StoreCategory.objects.annotate(icon=F('category_icon')).filter(is_active=True).values(*values).order_by('category_order', 'updated_date'))

    data['categories'] = categories

    return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

@login_required
@csrf_exempt
@require_GET
def item_service(request):
    """
    store item service page
    """

    page = 1

    if request.GET.__contains__('page'):

        try:

            page = int(request.GET['page'])

            if not page:

                page = 1

        except ValueError:

            page = 1

    category = None

    if request.GET.__contains__('category'):

        try:

            category = int(request.GET['category'])

        except ValueError:

            pass

    order_string = 'created_date'

    if request.GET.__contains__('order'):

        try:

            order_string_raw = request.GET['order']

            if order_string_raw in ['item_price', 'sold_count']:

                order_string = order_string_raw

        except ValueError:

            pass

    sort_string = '-'

    if request.GET.__contains__('sort'):

        try:

            sort_value = int(request.GET['sort'])

            if not sort_value:

                sort_string = ''

        except ValueError:

            pass

    order_string_next = 'created_date'

    if request.GET.__contains__('order_next'):

        try:

            order_string_raw = request.GET['order_next']

            if order_string_raw in ['item_price', 'sold_count']:

                order_string = order_string_raw

        except ValueError:

            pass

    sort_string_next = '-'

    if request.GET.__contains__('sort_next'):

        try:

            sort_value = int(request.GET['sort_next'])

            if not sort_value:

                sort_string = ''

        except ValueError:

            pass

    order_by_string = sort_string + order_string
    order_by_string_next = sort_string_next + order_string_next

    page_length = 12

    values = [
        'id',
        'item_name',
        'item_desc',
        'item_price',
        'item_icon',
        'item_url',
        'created_date',
        'required_level'
    ]

    item_filter = dict()

    item_filter['is_active'] = True

    if request.GET.__contains__('start_price') and request.GET.__contains__('end_price'):
        item_filter['item_price__gte'] = int(request.GET['start_price'])
        item_filter['item_price__lte'] = int(request.GET['end_price'])

    if category is not None:

        item_filter['category_id'] = category

    all_items = StoreItem.objects.annotate(icon=F('item_icon')).filter(**item_filter).values(*values).order_by(order_by_string, order_by_string_next)

    start = (page - 1) * page_length

    end = page* page_length

    all_items_count = all_items.count()

    items = all_items[start:end]

    list_items = list(items)

    data = dict()

    data['items'] = list_items

    data['count'] = all_items_count

    data['pagecount'] = int((all_items_count -1)/page_length) + 1 if all_items_count > 0 else 0

    data['page'] = page

    data['status'] = 200

    return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')


@login_required
@csrf_exempt
@require_GET
def sales_data(request):
    """
    store sales service page
    """

    user = request.user

    if not has_related_user(user):

        return HttpResponse(json.dumps({'status': 101, 'response':'RX manager not found'}), content_type='application/json')

    rx_manager = user.receptmanagers

    page = 1

    if request.GET.__contains__('page'):

        try:

            page = int(request.GET['page'])

            if not page:

                page = 1

        except ValueError:

            page = 1

    page_length = 10

    values = [
        'id',
        'item__id',
        'item__item_name',
        'item__item_price',
        'amount',
        'total',
        'status',
        'created_date',
        'item__item_icon',
        'item__item_desc',
        'item__required_level',
    ]

    all_sales_data = rx_manager.sales.annotate(item_name=F('item__item_name'), item_price=F('item__item_price')).values(*values).order_by('-created_date')

    start = (page - 1) * page_length

    end = page* page_length

    all_items_count = all_sales_data.count()

    sales_data_paged = all_sales_data[start:end]

    list_data = list(sales_data_paged)

    data = dict()

    data['sales_data'] = list_data

    data['count'] = all_items_count

    data['pagecount'] = int((all_items_count -1)/page_length) + 1 if all_items_count > 0 else 0

    data['page'] = page

    data['status'] = 200

    return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')


#pylint: disable=W0613
@login_required
@csrf_exempt
@require_GET
def category_parameters(request):
    """
    parameters test
    """

    # return HttpResponse(status=200)

    categories = StoreCategory.objects.all()

    categories_list = list()

    for category in categories:

        category_dict = dict()

        category_dict['category_name'] = category.category_name

        category_dict['category_order'] = category.category_order

        category_dict['category_icon'] = category.category_icon.url

        category_dict['category_url'] = category.category_url

        category_dict['dir_path'] = category.dir_path

        category_dict['upload_dir_path'] = category.upload_dir_path

        category_dict['is_active'] = category.is_active

        items = category.items.filter(is_active=True)

        items_list = list()

        for item in items:

            item_dict = dict()

            item_dict['item_name'] = item.item_name

            item_dict['item_desc'] = item.item_desc

            item_dict['item_price'] = item.item_price

            item_dict['item_icon'] = item.item_icon.url

            item_dict['item_url'] = item.item_url

            items_list.append(item_dict)

        category_dict['items'] = items_list

        categories_list.append(category_dict)

    return HttpResponse(json.dumps(categories_list), content_type='application/json')
