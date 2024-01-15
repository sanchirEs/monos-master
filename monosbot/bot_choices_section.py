""" sending choices """
import json
import requests
import redis
from receptmanager.models import ReceptManager
from monosbot.bot_check_users import set_user_status_redis
from monosbot.bot_get_buttons import (
    get_button_list, get_button_list2, get_user_reg_buttons,
    get_button_list3, get_button_cancel, get_button_list4
)

def get_manager_type_by_fbid(fbid):
    receptmanager = ReceptManager.objects.filter(facebook_id_messenger=fbid).first()
    return receptmanager.manager_type

def send_choices(post_message_url, fbid):
    """ send main choices"""

    if check_current_campaign_exists(fbid):

        response_msg_dict = dict()

        response_msg_dict["recipient"] = {"id":fbid}

        response_msg_dict["message"] = {"text":"Та сонголтоо хийнэ үү", "quick_replies":get_button_list()}

        response_msg = json.dumps(response_msg_dict)

        requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)

    else:

        response_msg_dict = dict()

        response_msg_dict["recipient"] = {"id":fbid}

        response_msg_dict["message"] = {"text":"Идэвхтэй хөтөлбөр байхгүй байна. Та өмнөх хөтөлбөрийн мэдээллийг харж агуулгыг харах боломжтой. Та сонголтоо хийнэ үү", "quick_replies":get_button_list3()}

        response_msg = json.dumps(response_msg_dict)

        requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)

def send_choices_with_name(post_message_url, fbid, campaign_name):
    """ send main choices"""

    if check_current_campaign_exists(fbid):

        response_msg_dict = dict()

        response_msg_dict["recipient"] = {"id":fbid}

        text = '"' + campaign_name + '"' + '\nТа сонголтоо хийнэ үү'

        response_msg_dict["message"] = {"text":text, "quick_replies":get_button_list()}

        response_msg = json.dumps(response_msg_dict)

        requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)

    else:

        response_msg_dict = dict()

        response_msg_dict["recipient"] = {"id":fbid}

        response_msg_dict["message"] = {"text":"Идэвхтэй хөтөлбөр байхгүй байна. Та өмнөх хөтөлбөрийн мэдээллийг харж агуулгыг харах боломжтой. Та сонголтоо хийнэ үү", "quick_replies":get_button_list3()}

        response_msg = json.dumps(response_msg_dict)

        requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)


def send_choices2(post_message_url, fbid):
    """ send main choices"""

    response_msg_dict = dict()

    response_msg_dict["recipient"] = {"id":fbid}

    response_msg_dict["message"] = {"text":"-- Өмнөх хөтөлбөрүүд --", "quick_replies":get_button_list2()}

    response_msg = json.dumps(response_msg_dict)

    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)


def send_choices2_with_text(post_message_url, fbid, text):
    """ send main choices"""

    response_msg_dict = dict()

    response_msg_dict["recipient"] = {"id":fbid}

    response_msg_dict["message"] = {"text":text, "quick_replies":get_button_list2()}

    response_msg = json.dumps(response_msg_dict)

    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)


def send_cancel_with_text(post_message_url, fbid, text, next_step):
    """ send main choices"""

    response_msg_dict = dict()

    response_msg_dict["recipient"] = {"id":fbid}

    response_msg_dict["message"] = {"text":text, "quick_replies":get_button_cancel(next_step)}

    response_msg = json.dumps(response_msg_dict)

    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)


def send_cancel_response(post_message_url, fbid, next_step):
    """ send cancel response """

    r = redis.Redis(connection_pool=REDISPOOL)

    set_user_status_redis(fbid, r, 0)

    if next_step == 2:

        send_choices2(post_message_url, fbid)


def send_user_reg_request(post_message_url, fbid):
    """ send main choices"""

    response_msg_dict = dict()

    response_msg_dict["recipient"] = {"id":fbid}

    response_msg_dict["message"] = {"text":"Хэрэглэгчийн бүртгэл байхгүй байна", "quick_replies":get_user_reg_buttons()}

    response_msg = json.dumps(response_msg_dict)

    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)


def send_text(post_message_url, fbid, text):
    """ send main choices"""

    response_msg_dict = dict()

    response_msg_dict["recipient"] = {"id":fbid}

    response_msg_dict["message"] = {"text":text}

    response_msg = json.dumps(response_msg_dict)

    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)


REDISPOOL = redis.ConnectionPool(path='/tmp/redis.sock', encoding="utf-8", decode_responses=True, connection_class=redis.UnixDomainSocketConnection)


def check_current_campaign_exists(fbid):
    """ check if current camaign exists """

    r = redis.Redis(connection_pool=REDISPOOL)

    manager_type = get_manager_type_by_fbid(fbid)

    return r.exists('current_campaing_' + str(manager_type))


def send_campaing_choices(post_message_url, fbid, campaign_hashtag, campaign_name):
    """ send other campaign choices"""

    text = '"' + campaign_name + '"\nТа сонголтоо хийнэ үү'

    response_msg_dict = dict()

    response_msg_dict["recipient"] = {"id":fbid}

    response_msg_dict["message"] = {"text":text, "quick_replies":get_button_list4(campaign_hashtag, campaign_name)}

    response_msg = json.dumps(response_msg_dict)

    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)


def send_campaing_choices_with_text(post_message_url, fbid, campaign_hashtag, campaign_name, text):
    """ send other campaign choices"""

    response_msg_dict = dict()

    response_msg_dict["recipient"] = {"id":fbid}

    response_msg_dict["message"] = {"text":text, "quick_replies":get_button_list4(campaign_hashtag, campaign_name)}

    response_msg = json.dumps(response_msg_dict)

    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
