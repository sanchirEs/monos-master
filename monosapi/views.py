""" api """

import json
from datetime import datetime, timedelta
from django.views import View, generic
from oauth2_provider.views.generic import ProtectedResourceView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django.db.models import F
from django.db.utils import IntegrityError
from django.contrib.auth.models import User, Group
from productmanager.models import ProductManager
from campaign.models import Campaign

# from django.contrib.auth.decorators import login_required

def convert_date_to_string(o):
    """date converter"""

    if isinstance(o, Decimal):

        return str(o)

    elif isinstance(o, date):

        return o.strftime('%Y-%m-%d')

    else:

        return None

class AxisCampaignEndPoint(View):
    """ api for axis """
    #pylint: disable=W0613
    def get(self, request, *args, **kwargs):
        """
        Get service
        """
        px = None

        if request.GET.__contains__('manager_id'):

            try:

                manager_id = int(request.GET['manager_id'])

            except ValueError:

                data = {'response': 'Invalid product manager id', 'status': 101, 'readable_response': 'Хэрэглэгчий ID буруу байна'}

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            px = ProductManager.objects.filter(manager_id=manager_id, is_active=True).first()

            if px is None:

                data = {'response': 'Id does not exists', 'status': 121, 'readable_response': 'Хэрэглэгч олдсонгүй'}

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

        else:

            data = {'response': 'manager_id field required', 'status': 102, 'readable_response': 'Хэрэглэгчий ID байхгүй байна'}

            return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

        if request.GET.__contains__('product_id'):

            try:

                product_id = int(request.GET['product_id'])

            except ValueError:

                data = {'response': 'Invalid product_id', 'status': 110, 'readable_response': 'Хөтөлбөрийн ID буруу байна'}

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            campaign_values = [
                'id',
                'product_name',
                'product_desc',
                'product_hash',
                'created_date',
                'xp_total',
                'post_count',
                'advice_count',
                'top_advice__post_url',
                'top_post__post_url',
                'is_active'
            ]

            campaign_data = Campaign.objects.annotate(top_advice_url=F('top_advice__post_url'), top_post_url=F('top_post__post_url'), product_id=F('id')).filter(id=product_id, product_manager=px).values(*campaign_values).first()

            if campaign_data is None:

                data = {'response': 'Product not found', 'status': 111, 'readable_response': 'Хөтөлбөр байхгүй байна'}

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            else:

                campaign_data['status'] = 200

                return HttpResponse(json.dumps(campaign_data, default=convert_date_to_string), content_type='application/json')

        else:

            page = 1

            if request.GET.__contains__('page'):

                try:

                    page = int(request.GET['page'])

                    if not page:

                        page = 1

                except ValueError:

                    page = 1

            campaign_values = [
                'id',
                'product_name',
                'product_desc',
                'product_hash',
                'created_date',
                'xp_total',
                'post_count',
                'advice_count',
                'is_active'
            ]

            page_length = 12

            all_campaign = Campaign.objectsannotate(product_id=F('id')).filter(product_manager=px).values(*campaign_values).order_by('-created_date')

            start = (page - 1) * page_length

            end = page* page_length

            all_campaign_count = all_campaign.count()

            campaigns = all_campaign[start:end]

            list_campaigns = list(campaigns)

            data = dict()

            data['campaigns'] = list_campaigns

            data['count'] = all_campaign_count

            data['pagecount'] = int((all_campaign_count -1)/page_length) + 1 if all_campaign_count > 0 else 0

            data['page'] = page

            data['status'] = 200

            return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):

        return generic.View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Post Service
        """
        try:

            json_dict = json.loads(request.body.decode('utf-8'))

        except ValueError:

            data = {'response': 'JSON error', 'status': 105, 'readable_response': 'Хүсэлт буруу байна'}

            return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

        px = None

        if 'manager_id' in json_dict:

            try:

                px_id = int(json_dict['manager_id'])

            except ValueError:

                data = {'response': 'Invalid product manager id', 'status': 101, 'readable_response': 'Хэрэглэгчий ID буруу байна'}

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            px = ProductManager.objects.filter(manager_id=px_id, is_active=True).first()

            if px is None:

                data = {'response': 'ID does not exists', 'status': 121, 'readable_response': 'Хэрэглэгч олдсонгүй'}

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

        else:

            data = {'response': 'manager_id field required', 'status': 102, 'readable_response': 'Хэрэглэгчий ID байхгүй байна'}

            return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

        if 'product_id' in json_dict:

            try:

                campaign_id = int(json_dict['product_id'])

            except TypeError:

                data = {'response': 'Invalid product id', 'status': 101, 'readable_response': 'Хөтөлбөрийн ID буруу байна'}

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            campaign = Campaign.objects.filter(id=campaign_id, product_manager=px).first()

            if campaign is None:

                data = {'response': 'Product does not exists', 'status': 121, 'readable_response': 'Хөтөлбөр олдсонгүй'}

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            px_values = [
                'product_name',
                'product_desc',
            ]

            for key in px_values:

                if key in json_dict:

                    setattr(campaign, key, json_dict[key])

            campaign.save()

            data_dict = dict()

            data_dict['product_id'] = campaign.id

            data_dict['product_name'] = campaign.product_name

            data_dict['product_desc'] = campaign.product_desc

            data_dict['product_hash'] = campaign.product_hash

            data_dict['created_date'] = campaign.created_date

            data_dict['xp_total'] = campaign.xp_total

            data_dict['post_count'] = campaign.post_count

            data_dict['advice_count'] = campaign.advice_count

            data_dict['top_advice_url'] = campaign.top_advice.post_url if campaign.top_advice is not None else ''

            data_dict['top_post_url'] = campaign.top_post.post_url if campaign.top_post is not None else ''

            data_dict['status'] = 200

            return HttpResponse(json.dumps(data_dict, default=convert_date_to_string), content_type='application/json')

        else:

            required_fields = [
                'product_name',
                'product_desc',
                'product_hash'
            ]

            data_dict = dict()

            for key in required_fields:

                if key in json_dict:

                    data_dict[key] = json_dict[key]

                else:

                    data = {'response': 'Missing field (' + key + ')', 'status': 122, 'readable_response': 'Хөтөлбөр үүсгэхэд алдаа гарлаа(' + key + ')'}

                    return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            start_date = datetime.now()

            if 'start_date' in json_dict:

                try:

                    start_date = datetime.strptime(json_dict['start_date'], '%Y-%m-%d %H:%M:%S')

                except ValueError:

                    data = {'response': 'Invalid start_date', 'status': 135, 'readable_response': 'Хөтөлбөр эхлэх огноо буруу байна'}

                    return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            end_date = start_date + timedelta(days=7)

            if 'end_date' in json_dict:

                try:

                    end_date = datetime.strptime(json_dict['end_date'], '%Y-%m-%d %H:%M:%S')

                except ValueError:

                    data = {'response': 'Invalid end_date', 'status': 135, 'readable_response': 'Хөтөлбөр дуусах огноо буруу байна'}

                    return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            if end_date < start_date:

                data = {'response': 'Inproper dates', 'status': 136, 'readable_response': 'Дуусах огноо, эхлэх огнооноос өмнө байна'}

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            data_dict['start_date'] = start_date

            data_dict['end_date'] = end_date

            data_dict['is_active'] = False

            data_dict['product_manager_id'] = px.id

            try:

                campaign = Campaign.objects.create(**data_dict)

            except ValidationError:

                data = {'response': 'Campaign creation error', 'status': 123, 'readable_response': 'Хөтөлбөр үүсгэхэд алдаа гарлаа, # давхардсан'}

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            except IntegrityError:

                data = {'response': 'Campaign creation error', 'status': 124, 'readable_response': 'Хөтөлбөр үүсгэхэд алдаа гарлаа, # давхардсан'}

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            data_dict = dict()

            data_dict['product_id'] = campaign.id

            data_dict['product_name'] = campaign.product_name

            data_dict['product_desc'] = campaign.product_desc

            data_dict['product_hash'] = campaign.product_hash

            data_dict['created_date'] = campaign.created_date

            data_dict['xp_total'] = campaign.xp_total

            data_dict['post_count'] = campaign.post_count

            data_dict['advice_count'] = campaign.advice_count

            data_dict['top_advice'] = campaign.top_advice.post_url if campaign.top_advice is not None else ''

            data_dict['top_post'] = campaign.top_post.post_url if campaign.top_post is not None else ''

            data_dict['is_active'] = campaign.is_active

            data_dict['status'] = 200

            return HttpResponse(json.dumps(data_dict, default=convert_date_to_string), content_type='application/json')


class AxisProductManagerEndPoint(View):
    """ api for axis """

    #pylint: disable=W0613
    def get(self, request, *args, **kwargs):
        """
        Get service
        """
        if request.GET.__contains__('manager_id'):

            try:

                px_id = int(request.GET['manager_id'])

            except ValueError:

                data = {'response': 'Invalid manager id', 'status': 101, 'readable_response': 'Хэрэглэгчий ID буруу байна'}

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            px_values = [
                'fullname',
                'first_name',
                'last_name',
                'username',
                'email',
                'phone',
                'address',
                'facebook',
                'about',
                'avatar',
            ]

            px_data = ProductManager.objects.filter(manager_id=px_id, is_active=True).values(*px_values).first()

            if px_data is None:

                data = {'response': 'Id does not exists', 'status': 121, 'readable_response': 'Хэрэглэгч олдсонгүй'}

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            px_data['manager_id'] = px_id

            px_data['status'] = 200

            return HttpResponse(json.dumps(px_data), content_type='application/json')

        data = {'response': 'manager_id required', 'status': 102, 'readable_response': 'Хэрэглэгч ID оруулна уу'}

        return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):

        return generic.View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Post Service
        """
        try:

            json_dict = json.loads(request.body.decode('utf-8'))

        except ValueError:

            data = {'response': 'JSON error', 'status': 105, 'readable_response': 'Хүсэлт буруу байна'}

            return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

        if 'manager_id' in json_dict:

            try:

                px_id = int(json_dict['manager_id'])

            except TypeError:

                data = {'response': 'Invalid manager id', 'status': 101, 'readable_response': 'Хэрэглэгчий ID буруу байна'}

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            px = ProductManager.objects.filter(manager_id=px_id, is_active=True).first()

            if px is None:

                data = {'response': 'ID does not exists', 'status': 121, 'readable_response': 'Хэрэглэгч олдсонгүй'}

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            px_values = [
                'first_name',
                'last_name',
                'phone',
                'address',
                'facebook',
                'about',
                'avatar',
            ]

            for key in px_values:

                if key in json_dict:

                    setattr(px, key, json_dict[key])

            px.save()

            data_dict = dict()

            data_dict['manager_id'] = px.manager_id

            data_dict['username'] = px.username

            data_dict['email'] = px.email

            data_dict['fullname'] = px.fullname

            data_dict['first_name'] = px.first_name

            data_dict['last_name'] = px.last_name

            data_dict['phone'] = px.phone

            data_dict['address'] = px.address

            data_dict['address'] = px.address

            data_dict['address'] = px.address

            data_dict['facebook'] = px.facebook

            data_dict['about'] = px.about

            data_dict['avatar'] = px.avatar

            data_dict['status'] = 200

            return HttpResponse(json.dumps(data_dict), content_type='application/json')

        else:

            required_fields = [
                'username',
                'email',
                'first_name',
                'last_name',
                'manager_id'
            ]

            data_dict = dict()

            for key in required_fields:

                if key in json_dict:

                    data_dict[key] = json_dict[key]

                else:

                    data = {'response': 'Missing field (' + key + ')', 'status': 122, 'readable_response': 'Хэрэглэгч үүсгэхэд алдаа гарлаа(' + key + ')'}

                    return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            try:

                password = data_dict['username'] + '654789'

                user = User.objects.create_user(username=data_dict['username'], email=data_dict['email'], password=password, first_name=data_dict['first_name'], last_name=data_dict['last_name'], is_staff=True)

                group = Group.objects.filter(name='product_managers').first()

                if group is not None:

                    group.user_set.add(user)

            except IntegrityError as e:

                data = {'response': 'Manager creation error : ' + str(e), 'status': 124, 'readable_response': 'Хэрэглэгч үүсгэхэд алдаа гарлаа, хэрэглэгчийн нэр, имэйл давхардсан'}

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            optional_fields = [
                'phone',
                'address',
                'facebook',
                'about',
                'avatar',
            ]

            for key in optional_fields:

                if key in json_dict:

                    data_dict[key] = json_dict[key]

            data_dict['user'] = user

            try:

                px = ProductManager.objects.create(**data_dict)

            except ValidationError:

                data = {'response': 'Manager creation error', 'status': 123, 'readable_response': 'Хэрэглэгч үүсгэхэд алдаа гарлаа, хэрэглэгчийн нэр, имэйл давхардсан, manager_id'}

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            except IntegrityError:

                data = {'response': 'Manager creation error', 'status': 123, 'readable_response': 'Хэрэглэгч үүсгэхэд алдаа гарлаа, хэрэглэгчийн нэр, имэйл давхардсан, manager_id'}

                return HttpResponse(json.dumps(data, default=convert_date_to_string), content_type='application/json')

            data_dict.pop('user', None)

            data_dict['manager_id'] = px.manager_id

            data_dict['username'] = px.username

            data_dict['email'] = px.email

            data_dict['fullname'] = px.fullname

            data_dict['first_name'] = px.first_name

            data_dict['last_name'] = px.last_name

            data_dict['phone'] = px.phone

            data_dict['address'] = px.address

            data_dict['address'] = px.address

            data_dict['address'] = px.address

            data_dict['facebook'] = px.facebook

            data_dict['about'] = px.about

            data_dict['avatar'] = px.avatar

            data_dict['status'] = 200

            return HttpResponse(json.dumps(data_dict), content_type='application/json')
