
from celery import task

import requests
import json
from receptmanager.models import Device
from .models import Notification
from datetime import date

def convert(o):
    """date converter"""

    if isinstance(o, date):

        return o.strftime('%Y-%m-%d')

    else:

        return None


@task()
def send_notification(title, content, managers):

    devices = Device.objects.filter(manager_id__in=managers)

    for device in devices:

        badge = Notification.objects.values().filter(manager_id=device.manager_id, read=0).count()
        params = {
            'to' : 'ExponentPushToken['+device.token+']',
            'title' : title,
            'body' : content,
            'sound' : 'default',
            'data' : {
                'badge' : badge
            }
        }
        response_msg = json.dumps(params, default=convert)
        print('******************')
        print(response_msg)

        response = requests.post('https://exp.host/--/api/v2/push/send', json=response_msg)
        data = response.json()

    return None

@task()
def send_notification_by_managers(managers, title, content, notifications, url):
    from receptmanager.models import Notification

    notifications = Notification.objects.filter(manager_id__in=managers)

    for manager in managers:

        notification = Notification.objects.create(manager_id=manager, title="Шинэ мессеж", content=str(content)[:50] + '...', is_public=False, type=5, url=url)
        notification.save()
        print(notification.id)

    devices = Device.objects.filter(manager__in=managers)

    for device in devices:
        badge = notifications.filter(manager_id=device.manager_id, read=0).count()
        params = {
            'to' : 'ExponentPushToken['+device.token+']',
            'title' : title,
            'body' : str(content)[:50] + '...',
            'sound' : 'default',
            'data' : {
                'badge' : badge
            }
        }

        response = requests.post('https://exp.host/--/api/v2/push/send', json=params)
        data = response.json()

@task()
def send_single_notification(manager_id, moil):
    title="+"+ str(moil) +" мойл"
    notification = Notification(manager_id=manager_id ,is_public=False, type=1, point=moil, read=False, title=title, content="Борлуулалтаас танд "+ str(moil) +" мойл орлоо")
    notification.save()

    badge = Notification.objects.filter(manager_id=manager_id, read=0).count()

    devices = Device.objects.filter(manager_id=manager_id)

    for device in devices:

        params = {
            'to' : 'ExponentPushToken['+device.token+']',
            'title' : title,
            'body' : content,
            'sound' : 'default',
            'data' : {
                'badge' : badge
            }
        }

        response = requests.post('https://exp.host/--/api/v2/push/send', json=params)
