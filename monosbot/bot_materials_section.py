""" Bot tests section """

import json
import requests
import redis
from monosbot.bot_choices_section import send_text, send_choices_with_name
from monosbot.bot_campaign_section import get_campaign_name, get_manager_type_by_fbid
from receptmanager.models import ReceptManager

REDISPOOL = redis.ConnectionPool(path='/tmp/redis.sock', encoding="utf-8", decode_responses=True, connection_class=redis.UnixDomainSocketConnection)

def start_material(post_message_url, fbid):
    """ start test method """

    r = redis.Redis(connection_pool=REDISPOOL)

    manager_type = get_manager_type_by_fbid(fbid)

    post_count = int(r.hget('current_campaing_' + str(manager_type), 'post_count'))

    if post_count:

        material_dict = json.loads(r.get('current_materials_' + str(manager_type)))

        material_dict['recipient'] = {'id':fbid}

        request_body = json.dumps(material_dict)

        status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=request_body)

        r.set('material_response', status.text)

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

    else:

        campaign_name = get_campaign_name(fbid)

        send_text(post_message_url, fbid, "Материал байхгүй байна. Хөтөлбөртэй холбоотой шинэ материалууд тун удахгүй орох болно.")

        send_choices_with_name(post_message_url, fbid, campaign_name)
