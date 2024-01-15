""" send bulk message """
import json
import requests
from monosbot.bot_check_users import (
    reset_current_user_status_noredis, check_manager_status
)
from monosbot.bot_get_buttons import get_button_continue

def send_bulk_message(recipents, message):
    """ sending bulk message """

    print(str(recipents) + ' - ' + message)

    post_message_url = 'https://graph.facebook.com/v2.11/me/messages?access_token=DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD'

    for psid in recipents:

        status = check_manager_status(psid)

        button_text = 'Тест үргэлжлүүлэх'

        print('current status - ' + str(status))

        if status == 0 or status == 1 or status == 3 or status == 4:

            button_text = 'Үргэлжлүүлэх'

            reset_current_user_status_noredis(psid)

        send_text(post_message_url, psid, message, button_text)


def send_bulk_message_with_urls(recipents, message, urls):
    """ sending bulk message """

    print(str(recipents) + ' - ' + message)

    post_message_url = 'https://graph.facebook.com/v2.11/me/messages?access_token=DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD'

    for psid in recipents:

        status = check_manager_status(psid)

        button_text = 'Тест үргэлжлүүлэх'

        if status == 0 or status == 1 or status == 3 or status == 4:

            button_text = 'Үргэлжлүүлэх'

            reset_current_user_status_noredis(psid)

        send_text_with_attachment(post_message_url, psid, message, urls, button_text)


def send_text(post_message_url, fbid, text, button_text):
    """ send main choices"""

    response_msg_dict = dict()

    response_msg_dict["recipient"] = {"id":fbid}

    response_msg_dict["message"] = {"text":text, 'quick_replies': get_button_continue(button_text, 2)}

    response_msg = json.dumps(response_msg_dict)

    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)


def send_text_with_attachment(post_message_url, fbid, text, urls, button_text):
    """ send main choices"""

    response_msg_dict = dict()

    response_msg_dict["recipient"] = {"id":fbid}

    response_msg_dict["messaging_type"] = 'RESPONSE'

    response_msg_dict["message"] = {"text":text}

    response_msg = json.dumps(response_msg_dict)

    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)

    attachment_dict = dict()

    attachment_dict['type'] = 'template'

    elements = list()

    for url in urls:

        element_dict = dict()

        element_dict['title'] = url[2]

        element_dict['subtitle'] = url[3]

        element_dict['image_url'] = url[0]

        default_action_dict = dict()

        default_action_dict['type'] = 'web_url'

        default_action_dict['url'] = url[1]

        default_action_dict['messenger_extensions'] = True

        default_action_dict['webview_height_ratio'] = 'compact'

        default_action_dict['fallback_url'] = 'https://monos.workplace.com/groups/154243908530765/'

        element_dict['default_action'] = default_action_dict

        element_dict['buttons'] = [{'type':'web_url', 'url':url[1], 'title':'Үзэх'}]

        elements.append(element_dict)

    attachment_dict['payload'] = {'template_type':'generic', 'elements':elements}

    response_msg_dict['message'] = {'attachment': attachment_dict, 'quick_replies': get_button_continue(button_text, 2)}

    request_body = json.dumps(response_msg_dict)

    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=request_body)
