""" Bot previous tests section """

import json
import requests
import redis
from campaign.models import CampaignData, Campaign
from receptmanager.models import ReceptManager
from monosbot.bot_check_users import (
    reset_current_user_status, update_user_xp_level, get_user_id_redis
)
from monosbot.bot_campaign_section import (
    get_campaign_name
)
from monosbot.bot_choices_section import (
    send_text, send_choices_with_name, send_campaing_choices_with_text
)

REDISPOOL = redis.ConnectionPool(path='/tmp/redis.sock', encoding="utf-8", decode_responses=True, connection_class=redis.UnixDomainSocketConnection)


def start_prev_test(fbid, post_message_url, campaign_data):
    """ start previous test method """

    campaign_hash = campaign_data['hashtag']

    campaign_name = campaign_data['name']

    user = ReceptManager.objects.filter(facebook_id_messenger=fbid).first()

    selected_campaign = Campaign.objects.filter(product_hash=campaign_hash, campaign_category=user.manager_type).first()

    if not selected_campaign:

        r = redis.Redis(connection_pool=REDISPOOL)

        reset_current_user_status(fbid, r)

        send_text(post_message_url, fbid, "Hashtag олдсонгүй")

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

        return

    current_test = selected_campaign.get_current_test()

    if not current_test or current_test.is_active is False:

        text = '"' + campaign_name + '"\n' + 'Энэ хөтөлбөртэй холбоотой тест байхгүй байна.'

        send_campaing_choices_with_text(post_message_url, fbid, campaign_hash, campaign_name, text)

        return

    questions = current_test.questions.all()

    if not questions:

        text = '"' + campaign_name + '"\n' + 'Энэ хөтөлбөртэй холбоотой тест байхгүй байна.'

        send_campaing_choices_with_text(post_message_url, fbid, campaign_hash, campaign_name, text)

        return

    r = redis.Redis(connection_pool=REDISPOOL)

    manager_id = get_user_id_redis(fbid, r)

    campaign_data = CampaignData.objects.filter(related_campaign_id=selected_campaign.id, manager_id=manager_id).first()

    if campaign_data and campaign_data.is_test_given:

        text = '"' + campaign_name + '"\n' + 'Та энэ хөтөлбөрийн тестийг бөглөсөн байна'

        send_campaing_choices_with_text(post_message_url, fbid, campaign_hash, campaign_name, text)

        return

    question = questions.first()

    send_question(post_message_url, fbid, question, campaign_hash, campaign_name, questions.count(), 0)


def send_question(post_message_url, fbid, question, campaign_hash, campaign_name, total_count, question_order):
    """ send question """

    answers = question.answers.all()

    if not answers:

        send_question_with_order(post_message_url, fbid, question_order + 1, campaign_hash, campaign_name, total_count)

        return

    full_question_text = '"' + campaign_name + '"\nАсуулт-' + str(question_order+1) + ' (' + str(total_count) + ')' + '\n' + question.question

    quick_replies = list()

    for answer in answers:

        full_answer = answer.short_answer + '.' + answer.full_answer

        full_question_text += '\n' + full_answer

        payload = dict()

        payload['type'] = 20

        payload['choice'] = 4

        payload['question'] = question_order

        payload['answer'] = int(answer.is_correct)

        payload['answer_key'] = answer.short_answer

        payload['campaign'] = campaign_hash

        payload['campaign_name'] = campaign_name

        payload['total_count'] = total_count

        quick_replies.append({"content_type":"text", "title":answer.short_answer, "payload": json.dumps(payload)})

    response_msg_dict = dict()

    response_msg_dict["recipient"] = {"id":fbid}

    response_msg_dict["message"] = {"text":full_question_text, "quick_replies":quick_replies}

    response_msg = json.dumps(response_msg_dict)

    r = redis.Redis(connection_pool=REDISPOOL)

    set_user_last_question_redis(fbid, r, 5, response_msg)

    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)


def send_question_with_order(post_message_url, fbid, question_order, campaign_hash, campaign_name, total_count):
    """ send question with order"""

    user = ReceptManager.objects.filter(facebook_id_messenger=fbid).first()

    selected_campaign = Campaign.objects.filter(product_hash=campaign_hash, campaign_category=user.manager_type).first()

    questions = selected_campaign.get_current_test().questions.all()

    question = None

    if question_order < questions.count():

        question = questions[question_order]

    if not question:

        r = redis.Redis(connection_pool=REDISPOOL)

        manager_id = get_user_id_redis(fbid, r)

        campaign_data = CampaignData.objects.filter(related_campaign_id=selected_campaign.id, manager_id=manager_id).first()

        set_remove_question_redis(fbid, r)

        send_text(post_message_url, fbid, "Тест дууслаа, баярлалаа.")

        if campaign_data:

            result_string = campaign_data.finish_test()

            send_text(post_message_url, fbid, result_string)

        text = '"' + campaign_name + '"\n' + 'Та сонголтоо хийнэ үү'

        send_campaing_choices_with_text(post_message_url, fbid, campaign_hash, campaign_name, text)

    else:

        send_question(post_message_url, fbid, question, campaign_hash, campaign_name, total_count, question_order)


def submit_prev_question_answer(post_message_url, fbid, payload):
    """ submit prev question answer"""

    campaign_hash = payload['campaign']

    user = ReceptManager.objects.filter(facebook_id_messenger=fbid).first()

    selected_campaign = Campaign.objects.filter(product_hash=campaign_hash, campaign_category=user.manager_type).first()

    r = redis.Redis(connection_pool=REDISPOOL)

    manager_id = get_user_id_redis(fbid, r)

    #pylint: disable=W0612
    campaign_data, created = CampaignData.objects.get_or_create(related_campaign_id=selected_campaign.id, manager_id=manager_id)

    correct_answer = int(payload['answer'])

    question_order = int(payload['question'])

    if correct_answer:

        result = str(question_order+1) + '.Зөв-'+payload['answer_key']

        xp_data = campaign_data.add_test_score_with_result(1, result)

        if xp_data is not None:

            update_user_xp_level(fbid, r, xp_data)

        send_text(post_message_url, fbid, "Хариулт ЗӨВ!")

    else:

        result = str(question_order+1) + '.Буруу-'+payload['answer_key']

        campaign_data.add_test_score_with_result(0, result)

        send_text(post_message_url, fbid, "Хариулт БУРУУ!")

    send_question_with_order(post_message_url, fbid, question_order + 1, payload['campaign'], payload['campaign_name'], int(payload['total_count']))


def submit_prev_answer_text(post_message_url, fbid):
    """ submit answer text"""

    r = redis.Redis(connection_pool=REDISPOOL)

    submit_prev_answer_text_redis(post_message_url, fbid, r)


def submit_prev_answer_text_redis(post_message_url, fbid, r):
    """ submit answer text with redis"""
    
    send_text(post_message_url, fbid, 'Та эхлүүлсэн тестээ заавал дуусгах ёстой. Тестийн хариултаа доорх сонголтууд дээр дарж хийнэ үү')

    response_msg = get_user_last_question_redis(fbid, r)

    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)


def set_remove_question_redis(fbid, r):
    """
    set user status to 0 and remove question
    """

    manager_key = 'rx:managers:' + fbid

    r.hset(manager_key, 'status', 4)

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
