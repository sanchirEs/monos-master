""" campaign section """
import json
from datetime import datetime, timedelta
import requests
import redis
from django.db.models import Q
from campaign.models import Campaign
from receptmanager.models import ReceptManager
from monosbot.bot_choices_section import (
    send_choices2_with_text, send_cancel_with_text, send_campaing_choices,
    send_campaing_choices_with_text, send_choices_with_name, send_text
)
from monosbot.bot_check_users import (
    set_user_status_redis, set_user_current_tag_name, get_user_current_tag_name,
    reset_current_user_status
)

REDISPOOL = redis.ConnectionPool(path='/tmp/redis.sock', encoding="utf-8", decode_responses=True, connection_class=redis.UnixDomainSocketConnection)

def get_manager_type_by_fbid(fbid):
    receptmanager = ReceptManager.objects.filter(facebook_id_messenger=fbid).first()
    return receptmanager.manager_type

def get_campaign_id(t):
    """
    get campaign id redis init
    """

    r = redis.Redis(connection_pool=REDISPOOL)

    return get_campaign_id_redis(r, t)


def get_campaign_id_redis(r, t):
    """
    get campaign id
    """
    campaign_id = r.hget('current_campaing_' + str(t), 'id')

    print('******')
    print("campaign_type = "+str(t))
    print("campaign_id = "+str(campaign_id))
    print('******')

    if campaign_id:

        return int(campaign_id)

    return None

def check_current_campaign_exists(fbid):
    """ check if current camaign exists """

    r = redis.Redis(connection_pool=REDISPOOL)

    manager_type = get_manager_type_by_fbid(fbid)

    return r.exists('current_campaing_' + str(manager_type))


def get_campaign_id_name(t):
    """
    get campaign id and name redis init
    """

    r = redis.Redis(connection_pool=REDISPOOL)

    return get_campaign_id_name_redis(r, t)


def get_campaign_id_name_redis(r, t):
    """
    get campaign id and name
    """

    campaign_id = r.hget('current_campaing_' + str(t), 'id')

    if campaign_id:

        return (int(campaign_id), r.hget('current_campaing_' + str(t), 'name'))

    return (None, None)

def get_campaign_name(fbid):
    """
    get campaign name redis init
    """
    r = redis.Redis(connection_pool=REDISPOOL)

    manager_type = get_manager_type_by_fbid(fbid)

    return get_campaign_name_redis(r, manager_type)


def get_campaign_name_redis(r, t):
    """
    get campaign name
    """

    return r.hget('current_campaing_' + str(t), 'name')


def send_prev_campaign_hashes(post_message_url, fbid):
    """ start test method """

    manager_type = get_manager_type_by_fbid(fbid)

    current_campaing_id = get_campaign_id(manager_type)

    now = datetime.now()

    date_60_days_ago = now - timedelta(days=60)

    if current_campaing_id:

        campaign_hashes = list(Campaign.objects.filter(~Q(id=current_campaing_id), is_active=True, end_date__gt=now, start_date__gte=date_60_days_ago, campaign_category=manager_type).values_list('product_hash', flat=True)[:10])

    else:

        campaign_hashes = list(Campaign.objects.filter(is_active=True, end_date__gt=now, start_date__gte=date_60_days_ago, campaign_category=manager_type).values_list('product_hash', flat=True)[:10])

    hash_string = '\n'.join(campaign_hashes)

    campaign_hash_string = '- Жагсаалт -\n\n' + hash_string + '\n\n( Хөтөлбөр сонгох ) товчин дээр дарж, дээрх жагсаалтаас сонголтоо хийгээрэй!'

    send_choices2_with_text(post_message_url, fbid, campaign_hash_string)


def send_request_hashtag(post_message_url, fbid):
    """ send request hashtag """

    r = redis.Redis(connection_pool=REDISPOOL)

    set_user_status_redis(fbid, r, 3)

    send_cancel_with_text(post_message_url, fbid, "Хөтөлбөрийн #hashtag оруулна уу?", 2)


def handle_hashtag_message(fbid, message, post_message_url):
    """ handle hashtag """

    r = redis.Redis(connection_pool=REDISPOOL)

    manager_type = get_manager_type_by_fbid(fbid)

    if 'text' not in message:

        set_user_status_redis(fbid, r, 0)

        response_text = 'Hashtag буруу байна. Та (Жагсаалт) товчин дээр дарж хөтөлбөрүүдийн hashtag-г хараарай'

        send_choices2_with_text(post_message_url, fbid, response_text)

        return

    hash_tag = message['text']

    selected_campaign = Campaign.objects.filter(product_hash=hash_tag, campaign_category=manager_type).first()

    if not selected_campaign:

        set_user_status_redis(fbid, r, 0)

        response_text = 'Hashtag буруу эсвэл таны оруулсан hashtag бүхий хөтөлбөрийн идэвхтэй хугацааа дууссан байна. Та (Жагсаалт) товчин дээр дарж идэвхтэй хөтөлбөрүүдийн hashtag-г хараарай'

        send_choices2_with_text(post_message_url, fbid, response_text)

        return

    set_user_current_tag_name(fbid, r, selected_campaign.product_hash, selected_campaign.product_name)

    send_campaing_choices(post_message_url, fbid, selected_campaign.product_hash, selected_campaign.product_name)


def handle_status_4_message(fbid, message, post_message_url):
    """ handle status 4 message """

    r = redis.Redis(connection_pool=REDISPOOL)

    campaing_data = get_user_current_tag_name(fbid, r)
    manager_type = get_manager_type_by_fbid(fbid)

    if not campaing_data or not campaing_data[0]:

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    campaign_name = campaing_data[1]

    campaign_tag = campaing_data[0]

    text = '"' + campaign_name + '"\nТа сонголтоо доорх товчнууд дээр дарж хийнэ үү.'

    send_campaing_choices_with_text(post_message_url, fbid, campaign_tag, campaign_name, text)


def reset_to_current_campaign(fbid, post_message_url):
    """ reset to current campaign """

    r = redis.Redis(connection_pool=REDISPOOL)

    reset_current_user_status(fbid, r)

    manager_type = get_manager_type_by_fbid(fbid)

    campaign_name = get_campaign_name(fbid)

    send_choices_with_name(post_message_url, fbid, campaign_name)


def send_chosen_campaign_material(fbid, post_message_url, campaign_data):
    """ chosen campaign material """

    manager_type = get_manager_type_by_fbid(fbid)

    campaign_hash = campaign_data['hashtag']

    campaign_name = campaign_data['name']

    selected_campaign = Campaign.objects.filter(product_hash=campaign_hash, campaign_category=manager_type).first()

    if not selected_campaign:

        r = redis.Redis(connection_pool=REDISPOOL)

        reset_current_user_status(fbid, r)

        send_text(post_message_url, fbid, "Hashtag олдсонгүй")

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    posts = selected_campaign.posts.all()

    posts_count = posts.count()

    if not posts_count:

        text = '"' + campaign_name + '"\n' + 'Энэ хөтөлбөртэй холбоотой материал байхгүй байна.'

        send_campaing_choices_with_text(post_message_url, fbid, campaign_hash, campaign_name, text)

    else:

        material_dict = dict()

        material_dict['recipient'] = {'id':fbid}

        attachment_dict = dict()

        attachment_dict['type'] = 'template'

        elements = list()

        for post in posts:

            element_dict = dict()

            element_dict['title'] = campaign_name

            if post.image_url:

                element_dict['image_url'] = post.image_url

            else:

                element_dict['image_url'] = 'https://moilbot.monos.mn/media/monoso.jpeg'

            element_dict['subtitle'] = post.post_name

            default_action_dict = dict()

            default_action_dict['type'] = 'web_url'

            default_action_dict['url'] = post.post_url

            default_action_dict['messenger_extensions'] = True

            default_action_dict['webview_height_ratio'] = 'compact'

            default_action_dict['fallback_url'] = 'https://monos.workplace.com/groups/154243908530765/'

            element_dict['default_action'] = default_action_dict

            element_dict['buttons'] = [{'type':'web_url', 'url':post.post_url, 'title':'Үзэх'}]

            elements.append(element_dict)

        attachment_dict['payload'] = {'template_type':'generic', 'elements':elements}

        material_dict['message'] = {'attachment': attachment_dict}

        request_body = json.dumps(material_dict)

        requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=request_body)

        send_campaing_choices(post_message_url, fbid, campaign_hash, campaign_name)
