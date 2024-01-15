"""
    common methods

    created by Mezorn LLC
"""

from datetime import datetime
import json
import redis
from onlinetest.models import OnlineTest


def my_json_converter(o):
    """
    json converter
    """

    if isinstance(o, datetime):

        return o.strftime('%Y-%m-%d %H:%M:%S')

    else:

        return o

def rx_get_dict(manager):
    """
    get rx initial dict
    """

    manager_dict = dict()

    manager_dict['id'] = manager.id

    manager_dict['messenger_id'] = manager.facebook_id_messenger

    manager_dict['name'] = manager.fullname

    manager_dict['xp'] = manager.rx_xp

    manager_dict['level'] = manager.rx_level

    manager_dict['status'] = 0

    return manager_dict


def clean_rx_data():
    """ reset rx data """

    r = redis.Redis(unix_socket_path='/tmp/redis.sock', encoding="utf-8", decode_responses=True)

    keys = r.keys("rx:managers:*")

    pipe = r.pipeline()

    for key in keys:

        pipe.hset(key, 'status', 0)

    pipe.execute()

def clean_delete_rx_data():
    """ reset rx data """

    r = redis.Redis(unix_socket_path='/tmp/redis.sock', encoding="utf-8", decode_responses=True)

    keys = r.keys("rx:managers:*")

    pipe = r.pipeline()

    for key in keys:

        pipe.delete(key)

    pipe.execute()


def has_test(current_campaign):
    """ Check if control has campaign """

    has = False

    try:

        has = (current_campaign.current_test is not None)

    except OnlineTest.DoesNotExist:

        pass

    return has

def set_control_values(current_control):
    """ set control values """

    r = redis.Redis(unix_socket_path='/tmp/redis.sock', encoding="utf-8", decode_responses=True)

    pipe = r.pipeline()

    pipe.hset('control_values', 'groupd_id', current_control.group_id)

    pipe.hset('control_values', 'groupd_token', current_control.group_token)

    pipe.execute()


def check_and_set_current_campaign(campaign):
    """ check and set current campaign """

    r = redis.Redis(unix_socket_path='/tmp/redis.sock', encoding="utf-8", decode_responses=True)

    check_current_campaing = r.hget('current_campaing_' + str(campaign.campaign_category), 'id')

    if check_current_campaing and int(check_current_campaing) == campaign.id:

        set_current_campaign_type(campaign)

def get_current_campaign_data():
    """ get current campaign data """

    r = redis.Redis(unix_socket_path='/tmp/redis.sock', encoding="utf-8", decode_responses=True)

    current_campaign_data = r.hgetall("current_campaing")

    if current_campaign_data is None:

        return {'status':404, 'response':'Current campaign does not exists'}

    current_questions_ids = r.zrange('current_questions', 0, -1)

    current_questions = list()

    for question_key in current_questions_ids:

        question_details_key = question_key + ':details'

        question_dict = r.hgetall(question_details_key)

        if question_dict is None:

            question_dict = dict()

        question_answers_key = question_key + ':answers'

        question_answers_keys = r.zrange(question_answers_key, 0, -1)

        answers = list()

        for answer_key in question_answers_keys:

            answer_dict = r.hgetall(answer_key)

            answers.append(answer_dict)

        question_dict['answers'] = answers

        current_questions.append(question_dict)

    current_campaign_data['questions'] = current_questions

    current_materials_json = r.get('current_materials')

    if current_materials_json is not None:

        current_materials = json.loads(current_materials_json)

    else:

        current_materials = dict()

    current_campaign_data['current_materials'] = current_materials

    return current_campaign_data


def set_current_campaign(current_campaign):
    """setting current campaign"""

    clean_current_campaign(current_campaign.campaign_category)

    r = redis.Redis(unix_socket_path='/tmp/redis.sock', encoding="utf-8", decode_responses=True)

    pipe = r.pipeline()

    pipe.hset("current_campaing", "id", current_campaign.id)

    pipe.hset("current_campaing", "name", current_campaign.product_name)

    pipe.hset("current_campaing", "description", current_campaign.product_desc)

    pipe.hset("current_campaing", "hash", current_campaign.product_hash)

    pipe.hset("current_campaing", "start_date", current_campaign.start_date.strftime('%Y-%m-%d'))

    pipe.hset("current_campaing", "end_date", current_campaign.end_date.strftime('%Y-%m-%d'))

    pipe.hset("current_campaing", "add_on_comment", current_campaign.add_on_comment)

    pipe.hset("current_campaing", "add_on_like", current_campaign.add_on_like)

    pipe.hset("current_campaing", "add_on_test", current_campaign.add_on_test)

    pipe.hset("current_campaing", "add_on_advise", current_campaign.add_on_advise)

    pipe.hset("current_campaing", "add_on_share", current_campaign.add_on_share)

    pipe.hset("current_campaing", "campaign_category", current_campaign.campaign_category)

    if has_test(current_campaign):

        current_test = current_campaign.current_test

        pipe.hset("current_campaing", "current_test_id", current_test.id)

        pipe.hset("current_campaing", "current_test_name", current_test.test_name)

        questions = current_test.questions.all()

        question_count = questions.count()

        pipe.hset("current_campaing", "current_test_question_count", question_count)

        prev_question_detail_key = None

        question_order = 1

        for question in questions:

            question_text = question.question

            question_key = 'question:' + str(question.id)

            pipe.zadd('current_questions', question_key, question_order)

            question_details_key = question_key + ':details'

            pipe.hset(question_details_key, 'question_id', question.id)

            pipe.hset(question_details_key, 'question_question', question_text)

            pipe.hset(question_details_key, 'question_order', question_order)

            pipe.hset(question_details_key, 'campaign_id', current_campaign.id)

            if prev_question_detail_key is not None:

                pipe.hset(prev_question_detail_key, 'next_question', question_key)

            prev_question_detail_key = question_details_key

            question_answers_key = question_key + ':answers'

            answers = question.answers.all()

            answer_order = 1

            full_question_text = 'Асуулт-' + str(question_order) + ' (' + str(question_count) + ')' + '\n' + question_text

            question_order += 1

            for answer in answers:

                answer_key = 'answer:' + str(answer.id)

                full_answer = answer.short_answer + '.' + answer.full_answer

                full_question_text += '\n' + full_answer

                pipe.zadd(question_answers_key, answer_key, answer_order)

                pipe.hset(answer_key, 'short_answer', answer.short_answer)

                payload = dict()

                payload['type'] = 2

                payload['choice'] = answer_order

                payload['question'] = question_key

                payload['answer'] = answer_key

                payload['campaign'] = current_campaign.id

                payload['campaign_name'] = current_campaign.product_name

                pipe.hset(answer_key, 'payload', json.dumps(payload))

                if answer.is_correct:

                    pipe.hset(question_details_key, 'correct_answer', answer_key)

                    pipe.hset(question_details_key, 'correct_answer_text', answer.short_answer)

                answer_order += 1

            pipe.hset(question_details_key, 'full_question', full_question_text)

    else:

        pipe.hset("current_campaing", "current_test_id", -1)

        pipe.hset("current_campaing", "current_test_name", "na")

    posts = current_campaign.posts.all()

    posts_count = posts.count()

    pipe.hset("current_campaing", "post_count", posts_count)

    if not posts_count:

        pipe.delete('current_materials')

        pipe.execute()

        return

    material_dict = dict()

    material_dict['recipient'] = {'id':"psid"}

    attachment_dict = dict()

    attachment_dict['type'] = 'template'

    elements = list()

    for post in posts:

        element_dict = dict()

        element_dict['title'] = current_campaign.product_name

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

        post_key = 'post:' + str(post.id)

        pipe.zadd('current_posts', post_key, posts_count)

        post_detail_key = post_key + ':detail'

        pipe.hset(post_detail_key, 'id', post.id)

        pipe.hset(post_detail_key, 'facebook_id', post.facebook_id)

        pipe.hset(post_detail_key, 'post_name', post.post_name)

        pipe.hset(post_detail_key, 'campaign_id', current_campaign.id)

        pipe.hset(post_detail_key, 'post_url', post.post_url)

        pipe.hset(post_detail_key, 'image_url', post.image_url)

        posts_count -= 1

    attachment_dict['type'] = 'template'

    attachment_dict['payload'] = {'template_type':'generic', 'elements':elements}

    material_dict['message'] = {'attachment': attachment_dict}

    pipe.set('current_materials', json.dumps(material_dict))

    pipe.execute()

def set_current_campaign_type(current_campaign):
    """setting current campaign"""

    clean_current_campaign(current_campaign.campaign_category)

    r = redis.Redis(unix_socket_path='/tmp/redis.sock', encoding="utf-8", decode_responses=True)

    c_type = str(current_campaign.campaign_category)

    print('------------------------------------')
    print('setting current campaign : type - ' + c_type)
    print('setting current campaign : id - ' + str(current_campaign.id))
    print('------------------------------------')

    pipe = r.pipeline()

    print("current_campaing_" + c_type)

    pipe.hset("current_campaing_" + c_type, "id", current_campaign.id)

    pipe.hset("current_campaing_" + c_type, "name", current_campaign.product_name)

    pipe.hset("current_campaing_" + c_type, "description", current_campaign.product_desc)

    pipe.hset("current_campaing_" + c_type, "hash", current_campaign.product_hash)

    pipe.hset("current_campaing_" + c_type, "start_date", current_campaign.start_date.strftime('%Y-%m-%d'))

    pipe.hset("current_campaing_" + c_type, "end_date", current_campaign.end_date.strftime('%Y-%m-%d'))

    pipe.hset("current_campaing_" + c_type, "add_on_comment", current_campaign.add_on_comment)

    pipe.hset("current_campaing_" + c_type, "add_on_like", current_campaign.add_on_like)

    pipe.hset("current_campaing_" + c_type, "add_on_test", current_campaign.add_on_test)

    pipe.hset("current_campaing_" + c_type, "add_on_advise", current_campaign.add_on_advise)

    pipe.hset("current_campaing_" + c_type, "add_on_share", current_campaign.add_on_share)

    pipe.hset("current_campaing_" + c_type, "campaign_category", current_campaign.campaign_category)

    if has_test(current_campaign):

        current_test = current_campaign.current_test

        pipe.hset("current_campaing_" + c_type, "current_test_id", current_test.id)

        pipe.hset("current_campaing_" + c_type, "current_test_name", current_test.test_name)

        questions = current_test.questions.all()

        question_count = questions.count()

        pipe.hset("current_campaing_" + c_type, "current_test_question_count", question_count)

        prev_question_detail_key = None

        question_order = 1

        for question in questions:

            question_text = question.question

            question_key = 'question:' + str(question.id)

            pipe.zadd('current_questions_' + c_type, question_key, question_order)

            question_details_key = question_key + ':details'

            pipe.hset(question_details_key, 'question_id', question.id)

            pipe.hset(question_details_key, 'question_question', question_text)

            pipe.hset(question_details_key, 'question_order', question_order)

            pipe.hset(question_details_key, 'campaign_id', current_campaign.id)

            if prev_question_detail_key is not None:

                pipe.hset(prev_question_detail_key, 'next_question', question_key)

            prev_question_detail_key = question_details_key

            question_answers_key = question_key + ':answers'

            answers = question.answers.all()

            answer_order = 1

            full_question_text = 'Асуулт-' + str(question_order) + ' (' + str(question_count) + ')' + '\n' + question_text

            question_order += 1

            for answer in answers:

                answer_key = 'answer:' + str(answer.id)

                full_answer = answer.short_answer + '.' + answer.full_answer

                full_question_text += '\n' + full_answer

                pipe.zadd(question_answers_key, answer_key, answer_order)

                pipe.hset(answer_key, 'short_answer', answer.short_answer)

                payload = dict()

                payload['type'] = 2

                payload['choice'] = answer_order

                payload['question'] = question_key

                payload['answer'] = answer_key

                payload['campaign'] = current_campaign.id

                payload['campaign_name'] = current_campaign.product_name

                pipe.hset(answer_key, 'payload', json.dumps(payload))

                if answer.is_correct:

                    pipe.hset(question_details_key, 'correct_answer', answer_key)

                    pipe.hset(question_details_key, 'correct_answer_text', answer.short_answer)

                answer_order += 1

            pipe.hset(question_details_key, 'full_question', full_question_text)

    else:

        pipe.hset("current_campaing_" + c_type, "current_test_id", -1)

        pipe.hset("current_campaing_" + c_type, "current_test_name", "na")

    posts = current_campaign.posts.all()

    posts_count = posts.count()

    pipe.hset("current_campaing_" + c_type, "post_count", posts_count)

    if not posts_count:

        pipe.delete('current_materials_' + c_type)

        pipe.execute()

        return

    material_dict = dict()

    material_dict['recipient'] = {'id':"psid"}

    attachment_dict = dict()

    attachment_dict['type'] = 'template'

    elements = list()

    for post in posts:

        element_dict = dict()

        element_dict['title'] = current_campaign.product_name

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

        post_key = 'post:' + str(post.id)

        pipe.zadd('current_posts', post_key, posts_count)

        post_detail_key = post_key + ':detail'

        pipe.hset(post_detail_key, 'id', post.id)

        pipe.hset(post_detail_key, 'facebook_id', post.facebook_id)

        pipe.hset(post_detail_key, 'post_name', post.post_name)

        pipe.hset(post_detail_key, 'campaign_id', current_campaign.id)

        pipe.hset(post_detail_key, 'post_url', post.post_url)

        pipe.hset(post_detail_key, 'image_url', post.image_url)

        posts_count -= 1

    attachment_dict['type'] = 'template'

    attachment_dict['payload'] = {'template_type':'generic', 'elements':elements}

    material_dict['message'] = {'attachment': attachment_dict}

    pipe.set('current_materials_' + c_type, json.dumps(material_dict))

    pipe.execute()

def clean_current_campaign(t):
    """delete current campaign"""
    campaign_type = str(t)
    r = redis.Redis(unix_socket_path='/tmp/redis.sock', encoding="utf-8", decode_responses=True)

    pipe = r.pipeline()

    question_keys = r.zrange('current_questions_' + campaign_type, 0, -1)

    for question_key in question_keys:

        question_answers_key = question_key + ':answers'

        question_details_key = question_key + ':details'

        answer_keys = r.zrange(question_answers_key, 0, -1)

        for answer_key in answer_keys:

            pipe.delete(answer_key)

        pipe.delete(question_answers_key)

        pipe.delete(question_details_key)

    post_keys = r.zrange('current_posts_' + campaign_type, 0, -1)

    for post_key in post_keys:

        post_detail_key = post_key + ':detail'

        pipe.delete(post_detail_key)

    pipe.delete('current_posts_' + campaign_type)

    pipe.delete('current_materials_' + campaign_type)

    pipe.delete('current_questions_' + campaign_type)

    pipe.delete('current_campaing_' + campaign_type)

    pipe.execute()


def delete_managers_key():
    """ delete managers key """

    r = redis.Redis(unix_socket_path='/tmp/redis.sock', encoding="utf-8", decode_responses=True)

    pipe = r.pipeline()

    keys = r.keys('rx:managers:*')

    for key in keys:

        pipe.delete(key)

    pipe.execute()