""" Bot tests section """

import json
import requests
import redis
from campaign.models import CampaignData
from onlinetest.models import OnlineTest
from receptmanager.models import ReceptManager
from monosbot.bot_check_users import get_user_id_redis, update_user_xp_level
from monosbot.bot_campaign_section import get_campaign_id_name_redis, get_campaign_id_redis, get_manager_type_by_fbid
from monosbot.bot_choices_section import send_choices, send_text, send_user_reg_request, send_choices_with_name

REDISPOOL = redis.ConnectionPool(path='/tmp/redis.sock', encoding="utf-8", decode_responses=True, connection_class=redis.UnixDomainSocketConnection)

def start_test(post_message_url, fbid):
    """ start test method """

    r = redis.Redis(connection_pool=REDISPOOL)

    manager_id = get_user_id_redis(fbid, r)
    manager_type = get_manager_type_by_fbid(fbid)

    campaign_id, campaign_name = get_campaign_id_name_redis(r, manager_type)

    if not campaign_id:

        send_choices(post_message_url, fbid)

        return

    if not manager_id:

        send_user_reg_request(post_message_url, fbid)

        return

    manager_type = get_manager_type_by_fbid(fbid)
    
    question_keys = r.zrange('current_questions_' + str(manager_type), 0, -1)

    onlinetest = OnlineTest.objects.filter(related_campaign_id=campaign_id).first()
    
    if question_keys and onlinetest is not None and onlinetest.is_active is True:

        campaign_data = CampaignData.objects.filter(related_campaign_id=campaign_id, manager_id=manager_id).first()

        if campaign_data and campaign_data.is_test_given:

            test_result = "Та энэ хөтөлбөрийн тестийг бөглөсөн байна.\n" + campaign_data.finish_test()

            send_text(post_message_url, fbid, test_result)

            send_choices_with_name(post_message_url, fbid, campaign_name)

        else:
            
            send_question_redis(post_message_url, fbid, question_keys[0], r)

    else:

        send_text(post_message_url, fbid, "Энэхүү хөтөлбөрийн тест ороогүй байна.")

        send_choices_with_name(post_message_url, fbid, campaign_name)


def submit_answer(post_message_url, fbid, payload):
    """ submit answer"""

    print('submitting answers')

    r = redis.Redis(connection_pool=REDISPOOL)

    campaign_id = int(payload['campaign'])

    manager_type = get_manager_type_by_fbid(fbid)

    current_campaing, campaign_name = get_campaign_id_name_redis(r, manager_type)

    manager_id = get_user_id_redis(fbid, r)

    if not current_campaing or current_campaing != campaign_id:

        send_text(post_message_url, fbid, "Өмнөх тест дууссан байна!")

        if manager_id is not None:

            campaign_data = CampaignData.objects.filter(related_campaign_id=campaign_id, manager_id=manager_id).first()

            if campaign_data:

                result_string = campaign_data.finish_test()

                send_text(post_message_url, fbid, result_string)

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    else:

        question_key = payload['question']

        answer_key = payload['answer']

        campaign_name = payload['campaign_name']

        question_details_key = question_key + ':details'

        correct_answer = r.hget(question_details_key, 'correct_answer')

        next_question = r.hget(question_details_key, 'next_question')

        question_order = r.hget(question_details_key, 'question_order')

        print('campaign id - ' + str(campaign_id) + '\n' + 'manager id - ' + str(manager_id))

        if manager_id is not None:
            #pylint: disable=W0612
            campaign_data, created = CampaignData.objects.get_or_create(related_campaign_id=campaign_id, manager_id=manager_id)

        else:

            send_text(post_message_url, fbid, "Бүртгэлгүй эмийн санч байна!")

            send_user_reg_request(post_message_url, fbid)

            return

        if correct_answer == answer_key:

            result = question_order + '.Зөв-'+ r.hget(answer_key, 'short_answer')

            xp_data = campaign_data.add_test_score_with_result(1, result)

            if xp_data is not None:

                update_user_xp_level(fbid, r, xp_data)

            send_text(post_message_url, fbid, "Хариулт ЗӨВ!")

        else:

            result = question_order + '.Буруу-'+ r.hget(answer_key, 'short_answer')

            campaign_data.add_test_score_with_result(0, result)

            send_text(post_message_url, fbid, "Хариулт БУРУУ!")

        send_question_redis(post_message_url, fbid, next_question, r)


def send_question(post_message_url, fbid, question_key):
    """ send question redis init"""

    r = redis.Redis(connection_pool=REDISPOOL)

    send_question_redis(post_message_url, fbid, question_key, r)


def send_question_redis(post_message_url, fbid, question_key, r):
    """ send question"""

    if question_key is None:

        manager_id = get_user_id_redis(fbid, r)
        manager_type = get_manager_type_by_fbid(fbid)

        campaign_id, campaign_name = get_campaign_id_name_redis(r, manager_type)

        campaign_data = CampaignData.objects.filter(related_campaign_id=campaign_id, manager_id=manager_id).first()

        set_remove_question_redis(fbid, r)

        send_text(post_message_url, fbid, "Тест дууслаа, баярлалаа.")

        if campaign_data:

            result_string = campaign_data.finish_test()

            send_text(post_message_url, fbid, result_string)

            send_choices_with_name(post_message_url, fbid, campaign_name)

        else:

            send_choices_with_name(post_message_url, fbid, campaign_name)

    else:

        question_details_key = question_key + ':details'

        question_answers_key = question_key + ':answers'

        quick_replies = list()

        answers = r.zrange(question_answers_key, 0, -1)

        for answer_key in answers:

            title = r.hget(answer_key, 'short_answer')

            payload = r.hget(answer_key, 'payload')

            quick_replies.append({"content_type":"text", "title":title, "payload": payload})

        response_msg_dict = dict()

        response_msg_dict["recipient"] = {"id":fbid}

        response_msg_dict["message"] = {"text":r.hget(question_details_key, 'full_question'), "quick_replies":quick_replies}

        response_msg = json.dumps(response_msg_dict)

        set_user_last_question_redis(fbid, r, 2, response_msg)

        requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)


def submit_answer_text(post_message_url, fbid):
    """ submit answer text"""

    r = redis.Redis(connection_pool=REDISPOOL)

    submit_answer_text_redis(post_message_url, fbid, r)


def submit_answer_text_redis(post_message_url, fbid, r):
    """ submit answer text with redis"""

    send_text(post_message_url, fbid, 'Та эхлүүлсэн тестээ заавал дуусгах ёстой. Тестийн хариултаа доорх сонголтууд дээр дарж хийнэ үү')

    response_msg = get_user_last_question_redis(fbid, r)

    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)


def set_remove_question_redis(fbid, r):
    """
    set user status to 0 and remove question
    """

    manager_key = 'rx:managers:' + fbid

    r.hset(manager_key, 'status', 0)

    r.hdel(manager_key, 'last_question')


def set_user_last_question_redis(fbid, r, status, last_question):
    """
    set user status and last_question
    """

    manager_key = 'rx:managers:' + fbid

    r.hset(manager_key, 'status', status)

    r.hset(manager_key, 'last_question', last_question)


def get_user_last_question_redis(fbid, r):
    """
    get user status and last_question
    """

    manager_key = 'rx:managers:' + fbid

    return r.hget(manager_key, 'last_question')
