"""
celery tasks for monosbot
"""
from __future__ import absolute_import
import json
from celery import task
from monosbot.bot_tests_section import start_test, submit_answer, submit_answer_text
from monosbot.bot_materials_section import start_material
from monosbot.bot_advice_section import start_advice, handle_link_message, start_prev_advice, handle_prev_link_message
from monosbot.bot_sms_section import sendsms as sendsms_in_celery
from monosbot.bot_send_message import send_bulk_message, send_bulk_message_with_urls
from monosbot.bot_check_users import (
    check_user_name, check_manager_status, register_user_request,
    check_user_registration_request
)
from monosbot.bot_choices_section import (
    send_choices, send_choices2, send_user_reg_request,
    send_text, send_choices_with_name, send_cancel_response
)
from monosbot.bot_campaign_section import (
    get_campaign_name, send_prev_campaign_hashes, send_request_hashtag,
    handle_hashtag_message, handle_status_4_message, reset_to_current_campaign,
    send_chosen_campaign_material
)
from monosbot.bot_prev_test import start_prev_test, submit_prev_question_answer, submit_prev_answer_text


@task()
def send_sms():
    """
    test method
    """
    sendsms_in_celery()

@task()
def testmethod(data):
    """
    test method
    """

    print('Incoming:\n' + data)


@task()
def send_message(recipents, message):
    """
    test method
    """
    send_bulk_message(recipents, message)


@task()
def send_message_urls(recipents, message, urls):
    """
    test method
    """
    send_bulk_message_with_urls(recipents, message, urls)


@task()
def post_consumer(fbid, post_message_url, message, incoming_message):
    """
    post_consumer method
    """

    print('Incoming Full - ' + json.dumps(incoming_message))

    if 'postback' in message:

        print('Handling postback')

        handle_postback(fbid, message, post_message_url)

    elif 'message' in message:

        inner_message = message['message']

        if 'quick_reply' in inner_message:

            print('Handling quickreplies')

            handle_quick_replies(fbid, inner_message, post_message_url)

        else:

            print('handling message')

            handle_message(fbid, inner_message, post_message_url)


@task()
def post_action_consumer(incoming_message):
    """
    post_action_consumer method
    """

    print('Incoming POST ACTION Full - ' + json.dumps(incoming_message))


#pylint: disable=W0613
def handle_message(fbid, message, post_message_url):
    """ handle message """

    manager_name = check_user_name(fbid)

    if manager_name is None:

        if check_user_registration_request(fbid):

            send_text(post_message_url, fbid, "Таны бүртгэлийн хүсэлтийг хүлээж авсан байна.")

        else:

            send_user_reg_request(post_message_url, fbid)

        return

    status = check_manager_status(fbid)

    if status == 1:

        handle_link_message(fbid, message, post_message_url)

    elif status == 2:

        submit_answer_text(post_message_url, fbid)

    elif status == 3:

        handle_hashtag_message(fbid, message, post_message_url)

    elif status == 4:

        handle_status_4_message(fbid, message, post_message_url)

    elif status == 5:

        submit_prev_answer_text(post_message_url, fbid)

    elif status == 6:

        handle_prev_link_message(fbid, message, post_message_url)

    else:

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)


def handle_postback(fbid, message, post_message_url):
    """ handle postback """

    # Payload
    payload_raw = message['postback']['payload']

    payload = json.loads(payload_raw)

    handle_payload(post_message_url, payload, fbid)


def handle_quick_replies(fbid, message, post_message_url):
    """ handle message """

    # Payload
    payload_raw = message['quick_reply']['payload']

    payload = json.loads(payload_raw)

    handle_payload(post_message_url, payload, fbid)


def handle_payload(post_message_url, payload, fbid):
    """ payload handler """

    payload_type = int(payload['type'])

    if payload_type == 0:

        manager_name = check_user_name(fbid)

        if manager_name is None:

            send_user_reg_request(post_message_url, fbid)

        else:

            campaign_name = get_campaign_name(fbid)

            send_choices_with_name(post_message_url, fbid, campaign_name)

    elif payload_type == 1:

        type_1(payload, fbid, post_message_url)

    elif payload_type == 2:

        submit_answer(post_message_url, fbid, payload)

    elif payload_type == 10:

        submit_user_request(post_message_url, fbid)

    elif payload_type == 20:

        type_2(payload, fbid, post_message_url)


def type_1(payload, fbid, post_message_url):
    """ payload handler """

    choice = int(payload['choice'])

    print('choice : ' + str(choice))

    if choice == 1:

        start_material(post_message_url, fbid)

    elif choice == 2:

        start_test(post_message_url, fbid)

    elif choice == 3:

        start_advice(post_message_url, fbid)

    elif choice == 4:

        send_choices2(post_message_url, fbid)

    elif choice == 5:

        send_choices(post_message_url, fbid)

    elif choice == 6:

        send_request_hashtag(post_message_url, fbid)

    elif choice == 7:

        send_prev_campaign_hashes(post_message_url, fbid)

    elif choice == 8:

        next_step = int(payload['text'])

        send_cancel_response(post_message_url, fbid, next_step)

    elif choice == 9:

        next_step = int(payload['text'])

        handle_continue(fbid, post_message_url, next_step)


def type_2(payload, fbid, post_message_url):
    """ 2 payload handler """

    choice = int(payload['choice'])

    if choice == 1:

        reset_to_current_campaign(fbid, post_message_url)

    elif choice == 2:

        send_chosen_campaign_material(fbid, post_message_url, payload['text'])

    elif choice == 3:

        start_prev_test(fbid, post_message_url, payload['text'])

    elif choice == 4:

        submit_prev_question_answer(post_message_url, fbid, payload)

    elif choice == 5:

        start_prev_advice(post_message_url, fbid, payload['text'])


def submit_user_request(post_message_url, fbid):
    """ submit user request """

    request_type, manager_name = register_user_request(fbid)

    if request_type == 0:

        send_text(post_message_url, fbid, "Бүртгүүлэх хүсэлтийг хүлээж авсан байна.")

    elif request_type == 1:

        text = manager_name + ' таны бүртгэл идэвхжсэн байна'

        send_text(post_message_url, fbid, text)

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)

    elif request_type == 2:

        send_text(post_message_url, fbid, "Баярлалаа таны хүсэлтийг хүлээж авлаа.")


#pylint: disable=W0613
def handle_continue(fbid, post_message_url, next_step):
    """ handle continue message """

    status = check_manager_status(fbid)

    if status == 2:

        submit_answer_text(post_message_url, fbid)

    elif status == 5:

        submit_prev_answer_text(post_message_url, fbid)

    else:

        campaign_name = get_campaign_name(fbid)

        send_choices_with_name(post_message_url, fbid, campaign_name)
