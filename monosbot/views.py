"""
Bot Views

created by Mezorn LLC
"""
import json
import redis
import requests
from django.views import View, generic
from django.http.response import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from monosbot.celery_tasks import post_consumer, post_action_consumer, send_sms as send_sms_in_celery, testmethod


class MonosBotView(View):
    """
    Bot Generic View
    """
    #pylint: disable=W0613
    def get(self, request, *args, **kwargs):
        """
        Get Service
        """

        try:

            if self.request.GET['hub.verify_token'] == '657483':

                return HttpResponse(self.request.GET['hub.challenge'])

            else:

                return HttpResponse('Error, invalid token')

        except MultiValueDictKeyError:

            return HttpResponse('Error, invalid token, in try catch')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):

        return generic.View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Post Service
        """
        try:

            incoming_message = json.loads(self.request.body.decode('utf-8'))

            post_message_url = 'https://graph.facebook.com/v2.11/me/messages?access_token=DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD'

            for entry in incoming_message['entry']:

                for message in entry['messaging']:

                    if 'read' in message or 'delivery' in message:

                        continue

                    fbid = message['sender']['id']

                    typing_response = {"recipient":{"id":fbid}, "sender_action":"typing_on"}

                    response_data = json.dumps(typing_response)

                    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_data)

                    post_consumer.delay(fbid, post_message_url, message, incoming_message)

        except ValueError:

            pass

        return HttpResponse(status=200)


class MonosGroupBotView(View):
    """
    Bot Generic View
    """
    #pylint: disable=W0613
    def get(self, request, *args, **kwargs):
        """
        Get Service
        """
        try:

            if self.request.GET['hub.verify_token'] == '890123':

                return HttpResponse(self.request.GET['hub.challenge'])

            else:

                return HttpResponse('Error(Group), invalid token')

        except MultiValueDictKeyError:

            return HttpResponse('Error(Group), invalid token')

    def post(self, request, *args, **kwargs):
        """
        Post Service
        """

        try:

            incoming_message = json.loads(self.request.body.decode('utf-8'))

            post_action_consumer.delay(incoming_message)

        except ValueError:

            pass

        return HttpResponse(status=200)


#pylint: disable=W0613
def last_response(request):
    """Testing facebook response"""

    r = redis.Redis(unix_socket_path='/tmp/redis.sock', encoding="utf-8", decode_responses=True)

    return HttpResponse(r.get('last_response'), content_type='application/json')


#pylint: disable=W0613
def response_msg(request):
    """Testing facebook request msg"""

    r = redis.Redis(unix_socket_path='/tmp/redis.sock', encoding="utf-8", decode_responses=True)

    return HttpResponse(r.get('response_msg'), content_type='application/json')

#pylint: disable=W0613
def material_request(request):
    """Testing facebook request msg"""

    r = redis.Redis(unix_socket_path='/tmp/redis.sock', encoding="utf-8", decode_responses=True)

    return HttpResponse(r.get('current_materials'), content_type='application/json')


#pylint: disable=W0613
def send_sms(request):
    """Testing facebook request msg"""

    send_sms_in_celery.delay()

    return HttpResponse(status=200)
