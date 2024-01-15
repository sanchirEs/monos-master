""" Bot tests section """

import json
import requests
import redis
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from campaign.models import CampaignData
from post.models import AdvicePost
from monos.common import rx_get_dict
from receptmanager.models import ReceptManager
from campaign.models import Campaign
from monosbot.bot_check_users import (
    get_user_status_redis, reset_current_user_status, set_user_current_tag_name_with_status,
    get_user_current_tag_name
)

from monosbot.bot_choices_section import (
    send_text, send_choices_with_name, send_campaing_choices_with_text
)

from monosbot.bot_campaign_section import (
    get_campaign_name, get_manager_type_by_fbid
)

REDISPOOL = redis.ConnectionPool(path='/tmp/redis.sock', encoding="utf-8", decode_responses=True, connection_class=redis.UnixDomainSocketConnection)

def start_advice(post_message_url, fbid):
    """ start advice method """

    r = redis.Redis(connection_pool=REDISPOOL)

    manager_status = get_user_status_redis(fbid, r)
    manager_type = get_manager_type_by_fbid(fbid)

    if manager_status is not None and manager_status == 0:

        set_user_status_redis(fbid, r, 1)

        send_text(post_message_url, fbid, "Зөвөлгөөний линкээ оруулна уу")

    else:

        send_text(post_message_url, fbid, "Хэрэглэгчийн бүртгэл байхгүй байна!")

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)


def start_prev_advice(post_message_url, fbid, campaign_data):
    """ start prev advice method """

    campaign_hash = campaign_data['hashtag']

    campaign_name = campaign_data['name']

    manager_type = get_manager_type_by_fbid(fbid)

    selected_campaign = Campaign.objects.filter(product_hash=campaign_hash, campaign_category=manager_type).first()

    if not selected_campaign:

        r = redis.Redis(connection_pool=REDISPOOL)

        reset_current_user_status(fbid, r)

        send_text(post_message_url, fbid, "Hashtag олдсонгүй")

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    r = redis.Redis(connection_pool=REDISPOOL)

    set_user_current_tag_name_with_status(fbid, r, campaign_hash, campaign_name, 6)

    question_text = '"' + campaign_name + '"\n' + 'Зөвөлгөөний линкээ оруулна уу'

    send_text(post_message_url, fbid, question_text)



def handle_prev_link_message(fbid, message, post_message_url):
    """ handle link """

    r = redis.Redis(connection_pool=REDISPOOL)

    manager_type = get_manager_type_by_fbid(fbid)

    campaing_data = get_user_current_tag_name(fbid, r)

    if not campaing_data or not campaing_data[0]:

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    campaign_name = campaing_data[1]

    campaign_tag = campaing_data[0]

    selected_campaign = Campaign.objects.filter(product_hash=campaign_tag, campaign_category=manager_type).first()

    if not selected_campaign:

        reset_current_user_status(fbid, r)

        send_text(post_message_url, fbid, "Hashtag олдсонгүй")

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    manager_id = get_user_id_redis(fbid, r)

    if manager_id is None:

        set_user_status_redis(fbid, r, 0)

        send_text(post_message_url, fbid, "Хэрэглэгчийн бүртгэл байхгүй байна!")

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    campaign_data, created = CampaignData.objects.get_or_create(related_campaign=selected_campaign, manager_id=manager_id)

    if campaign_data.advise_url:

        set_user_status_redis(fbid, r, 0)

        warning_text = 'Та энэ хөтөлбөрт өөрийн зөвөлгөөгөө бүртгүүлсэн байна!'

        send_campaing_choices_with_text(post_message_url, fbid, campaign_tag, campaign_name, warning_text)

        return

    if 'text' not in message:

        set_user_status_redis(fbid, r, 0)

        warning_text = 'Алдаатай линк явуулсан байна!'

        send_campaing_choices_with_text(post_message_url, fbid, campaign_tag, campaign_name, warning_text)

        return

    url_raw = message['text']

    url_validator = URLValidator()

    try:

        url_validator(url_raw)

    except ValidationError:

        set_user_status_redis(fbid, r, 0)

        warning_text = 'Алдаатай линк явуулсан байна!'

        send_campaing_choices_with_text(post_message_url, fbid, campaign_tag, campaign_name, warning_text)
        return

    group_id = '154243908530765'

    if 'https://monos.workplace.com/groups/154243908530765/permalink/' not in url_raw and 'https://monos.workplace.com/groups/1272597072788273/permalink/' not in url_raw and 'https://monos.workplace.com/groups/2149422908642584/permalink/' not in url_raw:

        set_user_status_redis(fbid, r, 0)

        warning_text = 'Алдаатай эсвэл групэд харьяалагддаггүй линк явуулсан байна!'

        send_campaing_choices_with_text(post_message_url, fbid, campaign_tag, campaign_name, warning_text)

        return

    elif 'https://monos.workplace.com/groups/1272597072788273/permalink/' in url_raw:

        group_id = '1272597072788273'
    
    elif 'https://monos.workplace.com/groups/2149422908642584/permalink/' in url_raw:

        group_id = '2149422908642584'

    replace_text = 'https://monos.workplace.com/groups/' + group_id + '/permalink/'

    post_id_raw = url_raw.replace(replace_text, '').replace('/', '')

    try:

        post_facebook_id = int(post_id_raw)

    except ValueError:

        set_user_status_redis(fbid, r, 0)

        warning_text = 'Постын ID буруу байна!'

        send_campaing_choices_with_text(post_message_url, fbid, campaign_tag, campaign_name, warning_text)

        return

    group_token = r.hget('control_values', 'groupd_token')

    bearer = 'Bearer ' + group_token

    headers = {'Authorization': bearer}

    get_url = 'https://graph.facebook.com/v2.11/' + group_id + '_' + str(post_facebook_id) + '?fields=picture,message,reactions.summary(true),attachments,comments.summary(true),from'

    response = requests.get(get_url, headers=headers)

    incoming_message = response.json()

    if 'error' in incoming_message:

        set_user_status_redis(fbid, r, 0)

        warning_text = 'Постын мэдээлэл татахад алдаа гарлаа!'

        send_campaing_choices_with_text(post_message_url, fbid, campaign_tag, campaign_name, warning_text)

        return

    if 'from' not in incoming_message:

        set_user_status_redis(fbid, r, 0)

        warning_text = 'Пост эзэмшигчийн мэдээллийг татахад алдаа гарлаа!'

        send_campaing_choices_with_text(post_message_url, fbid, campaign_tag, campaign_name, warning_text)

        return

    post_owner_id = incoming_message['from']['id']

    if post_owner_id != fbid:

        set_user_status_redis(fbid, r, 0)

        warning_text = 'Та энэ постын эзэмшигч биш байна!'

        send_campaing_choices_with_text(post_message_url, fbid, campaign_tag, campaign_name, warning_text)

        return

    check_prev_post = AdvicePost.objects.filter(facebook_id=post_facebook_id).first()

    if check_prev_post is not None:

        set_user_status_redis(fbid, r, 0)

        warning_text = 'Та энэ постыг өмнө оруулж байсан байна!'

        send_campaing_choices_with_text(post_message_url, fbid, campaign_tag, campaign_name, warning_text)

        return

    data_dict = dict()

    data_dict['post_url'] = 'https://monos.workplace.com/groups/' + group_id + '/permalink/' + str(post_facebook_id) + '/'

    if 'message' in incoming_message:

        post_name = incoming_message['message']

        current_hash = selected_campaign.product_hash

        if current_hash.lower() not in post_name.lower():

            set_user_status_redis(fbid, r, 0)

            warning_text = 'Таны пост энэ хөтөлбөртэй хамааралгүй байна!'

            send_campaing_choices_with_text(post_message_url, fbid, campaign_tag, campaign_name, warning_text)

            return

        data_dict['post_name'] = post_name

    else:

        set_user_status_redis(fbid, r, 0)

        warning_text = 'Постын мэдээлэл хоосон байна!'

        send_campaing_choices_with_text(post_message_url, fbid, campaign_tag, campaign_name, warning_text)

        return

    if 'reactions' in incoming_message and 'summary' in incoming_message['reactions'] and 'total_count' in incoming_message['reactions']['summary']:

        data_dict['like_count'] = incoming_message['reactions']['summary']['total_count']

    if 'comments' in incoming_message and 'summary' in incoming_message['comments'] and 'total_count' in incoming_message['comments']['summary']:

        data_dict['comment_count'] = incoming_message['comments']['summary']['total_count']

    if 'attachments' in incoming_message and 'data' in incoming_message['attachments']:

        datas = incoming_message['attachments']['data']

        if datas:

            data = datas[0]

            if 'media' in data and 'image' in data['media'] and 'src' in data['media']['image']:

                data_dict['image_url'] = data['media']['image']['src']

    data_dict['group_id'] = group_id

    AdvicePost.objects.update_or_create(related_manager_id=manager_id, facebook_id=post_facebook_id, related_campaing_id=selected_campaign.id, defaults=data_dict)

    campaign_data.check_advice(data_dict['post_url'])

    set_user_status_redis(fbid, r, 0)

    warning_text = '"' + campaign_name + '"' + ' хөтөлбөрт таны зөвөлгөөг бүртгэж авлаа'

    send_campaing_choices_with_text(post_message_url, fbid, campaign_tag, campaign_name, warning_text)


def handle_link_message(fbid, message, post_message_url):
    """ handle link """

    r = redis.Redis(connection_pool=REDISPOOL)

    manager_type = get_manager_type_by_fbid(fbid)

    current_campaign_id_raw = get_campaign_id_redis(r, manager_type)

    if current_campaign_id_raw is None:

        set_user_status_redis(fbid, r, 0)

        send_text(post_message_url, fbid, "Идэвхтэй хөтөлбөр байхгүй байна!")

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    current_campaign_id = int(current_campaign_id_raw)

    manager_id = get_user_id_redis(fbid, r)

    if manager_id is None:

        set_user_status_redis(fbid, r, 0)

        send_text(post_message_url, fbid, "Хэрэглэгчийн бүртгэл байхгүй байна!")

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    campaign_data, created = CampaignData.objects.get_or_create(related_campaign_id=current_campaign_id, manager_id=manager_id)

    if campaign_data.advise_url:

        set_user_status_redis(fbid, r, 0)

        send_text(post_message_url, fbid, "Та энэ хөтөлбөрт өөрийн зөвөлгөөгөө бүртгүүлсэн байна!")

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    if 'text' not in message:

        set_user_status_redis(fbid, r, 0)

        send_text(post_message_url, fbid, "Алдаатай линк явуулсан байна!")

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    url_raw = message['text']

    url_validator = URLValidator()

    try:

        url_validator(url_raw)

    except ValidationError:

        set_user_status_redis(fbid, r, 0)

        send_text(post_message_url, fbid, "Алдаатай линк явуулсан байна!")

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    group_id = '154243908530765'

    if 'https://monos.workplace.com/groups/154243908530765/permalink/' not in url_raw and 'https://monos.workplace.com/groups/1272597072788273/permalink/' not in url_raw and 'https://monos.workplace.com/groups/2149422908642584/permalink/' not in url_raw:

        set_user_status_redis(fbid, r, 0)

        send_text(post_message_url, fbid, "Алдаатай эсвэл групэд харьяалагддаггүй линк явуулсан байна!")

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    elif 'https://monos.workplace.com/groups/1272597072788273/permalink/' in url_raw:

        group_id = '1272597072788273'

    elif 'https://monos.workplace.com/groups/2149422908642584/permalink/' in url_raw:

        group_id = '2149422908642584'

    replace_text = 'https://monos.workplace.com/groups/' + group_id + '/permalink/'

    post_id_raw = url_raw.replace(replace_text, '').replace('/', '')

    try:

        post_facebook_id = int(post_id_raw)

    except ValueError:

        set_user_status_redis(fbid, r, 0)

        send_text(post_message_url, fbid, "Постын ID буруу байна!")

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    group_token = r.hget('control_values', 'groupd_token')

    bearer = 'Bearer ' + group_token

    headers = {'Authorization': bearer}

    get_url = 'https://graph.facebook.com/v2.11/' + group_id + '_' + str(post_facebook_id) + '?fields=picture,message,reactions.summary(true),attachments,comments.summary(true),from'

    response = requests.get(get_url, headers=headers)

    incoming_message = response.json()

    if 'error' in incoming_message:

        set_user_status_redis(fbid, r, 0)

        send_text(post_message_url, fbid, "Постын мэдээлэл татахад алдаа гарлаа!")

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    if 'from' not in incoming_message:

        set_user_status_redis(fbid, r, 0)

        send_text(post_message_url, fbid, "Пост эзэмшигчийн мэдээллийг татахад алдаа гарлаа!")

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    post_owner_id = incoming_message['from']['id']

    if post_owner_id != fbid:

        set_user_status_redis(fbid, r, 0)

        send_text(post_message_url, fbid, "Та энэ постын эзэмшигч биш байна!")

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    check_prev_post = AdvicePost.objects.filter(facebook_id=post_facebook_id).first()

    if check_prev_post is not None:

        set_user_status_redis(fbid, r, 0)

        send_text(post_message_url, fbid, "Та энэ постыг өмнө оруулж байсан байна!")

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    data_dict = dict()

    data_dict['post_url'] = 'https://monos.workplace.com/groups/' + group_id + '/permalink/' + str(post_facebook_id) + '/'

    if 'message' in incoming_message:

        post_name = incoming_message['message']

        current_hash = r.hget('current_campaing_' + str(manager_type), 'hash')

        if current_hash.lower() not in post_name.lower():

            set_user_status_redis(fbid, r, 0)

            send_text(post_message_url, fbid, "Таны пост энэ хөтөлбөртэй хамааралгүй байна!")

            campaign_name = get_campaign_name(fbid)

            send_choices_with_name(post_message_url, fbid, campaign_name)

            return

        data_dict['post_name'] = post_name

    else:

        set_user_status_redis(fbid, r, 0)

        send_text(post_message_url, fbid, "Постын мэдээлэл хоосон байна!")

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    if 'reactions' in incoming_message and 'summary' in incoming_message['reactions'] and 'total_count' in incoming_message['reactions']['summary']:

        data_dict['like_count'] = incoming_message['reactions']['summary']['total_count']

    if 'comments' in incoming_message and 'summary' in incoming_message['comments'] and 'total_count' in incoming_message['comments']['summary']:

        data_dict['comment_count'] = incoming_message['comments']['summary']['total_count']

    if 'attachments' in incoming_message and 'data' in incoming_message['attachments']:

        datas = incoming_message['attachments']['data']

        if datas:

            data = datas[0]

            if 'media' in data and 'image' in data['media'] and 'src' in data['media']['image']:

                data_dict['image_url'] = data['media']['image']['src']

    data_dict['group_id'] = group_id

    AdvicePost.objects.update_or_create(related_manager_id=manager_id, facebook_id=post_facebook_id, related_campaing_id=current_campaign_id, defaults=data_dict)

    campaign_data.check_advice(data_dict['post_url'])

    set_user_status_redis(fbid, r, 0)

    campaign_name = get_campaign_name(fbid)

    send_text_string = '"' + campaign_name + '"' + ' хөтөлбөрт таны зөвөлгөөг бүртгэж авлаа.'

    send_text(post_message_url, fbid, send_text_string)

    send_choices_with_name(post_message_url, fbid, campaign_name)


def send_text(post_message_url, fbid, text):
    """ send main choices"""

    response_msg_dict = dict()

    response_msg_dict["recipient"] = {"id":fbid}

    response_msg_dict["message"] = {"text":text}

    response_msg = json.dumps(response_msg_dict)

    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)


def get_button_list():
    """
    get button list
    """

    button_list = list()

    button_list.append({"content_type":"text", "title":"Материал", "payload": '{"type": 1, "choice": 1, "text": "monos"}'})

    button_list.append({"content_type":"text", "title":"Тест", "payload": '{"type": 1, "choice": 2, "text": "monos"}'})

    button_list.append({"content_type":"text", "title":"Зөвлөмж", "payload": '{"type": 1, "choice": 3, "text": "monos"}'})

    return button_list

def get_user_id(fbid):
    """
    get user id redis init
    """

    r = redis.Redis(connection_pool=REDISPOOL)

    return get_user_id_redis(fbid, r)


def get_user_id_redis(fbid, r):
    """
    get user id
    """

    manager_key = 'rx:managers:' + fbid

    manager_id = r.hget(manager_key, 'id')

    if manager_id is None:

        manager = ReceptManager.objects.filter(facebook_id_messenger=fbid).first()

        if manager is None:

            user_profile_url = 'https://graph.facebook.com/v2.11/%s?fields=picture,first_name,email,last_name&access_token=DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD' % fbid

            response_msg = requests.get(user_profile_url)

            try:

                user_data = response_msg.json()

                if 'id' in user_data:

                    manager = ReceptManager.create_from_dict(user_data)

                    manager_dict = rx_get_dict(manager)

                    r.hmset(manager_key, manager_dict)

                    manager_id = manager.id

            except (ValueError, KeyError):

                return None

        else:

            manager_dict = rx_get_dict(manager)

            r.hmset(manager_key, manager_dict)

            manager_id = manager.id


    return int(manager_id)


def get_campaign_id():
    """
    get campaign id redis init
    """

    r = redis.Redis(connection_pool=REDISPOOL)

    return get_campaign_id_redis(r)


def get_campaign_id_redis(r, t):
    """
    get campaign id
    """

    campaign_id = r.hget('current_campaing_' + str(t), 'id')

    if campaign_id:

        return int(campaign_id)

    return None


def update_user_xp_level(fbid, r, xp_data):
    """
    get user id
    """

    manager_key = 'rx:managers:' + fbid

    r.hset(manager_key, 'xp', xp_data[0])

    r.hset(manager_key, 'level', xp_data[1])


def set_user_status_redis(fbid, r, status):
    """
    set user status
    """

    manager_key = 'rx:managers:' + fbid

    r.hset(manager_key, 'status', status)
