"""
Bot settings
"""

import json
import pprint
import requests
from django.http.response import HttpResponse

#pylint: disable=W0613
def set_get_started(request):
    """Set get started text of bot"""

    post_message_url = 'https://graph.facebook.com/v2.11/me/messenger_profile?access_token=DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD'

    get_started_request = {"get_started": {"payload": '{"type": 0, "choice": 1, "text": "monos"}'}}

    request_msg = json.dumps(get_started_request)

    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=request_msg)

    return HttpResponse(json.dumps(status.json()), content_type='application/json')


#pylint: disable=W0613
def set_hello_text(request):
    """Set hello text of bot"""

    post_message_url = 'https://graph.facebook.com/v2.11/me/messenger_profile?access_token=DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD'

    hello_text_request = {"greeting":[{"locale":"default", "text":"Сайн уу {{user_first_name}}!"}]}

    request_msg = json.dumps(hello_text_request)

    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=request_msg)

    return HttpResponse(json.dumps(status.json()), content_type='application/json')


#pylint: disable=W0613
def white_list_domains(request):
    """Set hello text of bot"""

    post_message_url = 'https://graph.facebook.com/v2.11/me/thread_settings?access_token=DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD'

    domain_request = {"setting_type":"domain_whitelisting", "whitelisted_domains":["https://www.facebook.com", "https://rxbot.monos.mn", "https://monos.workplace.com"], "domain_action_type":"add"}

    request_msg = json.dumps(domain_request)

    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=request_msg)

    return HttpResponse(json.dumps(status.json()), content_type='application/json')


def white_list_domains_service(domains):
    """white_list_domains_service"""

    pprint.pprint(domains)

    post_message_url = 'https://graph.facebook.com/v2.11/me/thread_settings?access_token=DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD'

    domain_request = {"setting_type":"domain_whitelisting", "whitelisted_domains":domains, "domain_action_type":"add"}

    request_msg = json.dumps(domain_request)

    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=request_msg)

    print(status.text)

    return HttpResponse(json.dumps(status.json()), content_type='application/json')


def white_list_domains_remove_service(domains):
    """white_list_domains_service"""

    post_message_url = 'https://graph.facebook.com/v2.11/me/thread_settings?access_token=DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD'

    domain_request = {"setting_type":"domain_whitelisting", "whitelisted_domains":domains, "domain_action_type":"remove"}

    request_msg = json.dumps(domain_request)

    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=request_msg)

    return HttpResponse(json.dumps(status.json()), content_type='application/json')
