"""
Sending sms
"""

import csv
import json
from django.http.response import JsonResponse
import redis
import httplib2


def sendsms():
    """ sending sms """

    r = redis.Redis(unix_socket_path='/tmp/redis.sock', encoding="utf-8", decode_responses=True)

    if r.exists('sending_sms'):

        return

    r.set('sending_sms', '1')

    print('send sms started')

    with open('monosbot/csv/numbers.csv', newline='') as csv_file:

        reader = csv.reader(csv_file, delimiter=',')

        row = 0

        message = "7780-7780 Utsaar duudlagiin joloochoo duud 10.000 tugrug 24/7 tsagaar ajilladag tsor gants company.  MORIN JOLOOCH LLC 100,000,000 tugrugiin daatgaltai"

        message = message.replace(' ', '+')

        for item in reader:

            if item[0]:

                url = 'http://sms.unitel.mn/sendSMS.php?uname=morin+jolooch&upass=daVOUr6efB&sms='+message+'&from=157780&mobile='+item[0]

                print('url - ' + url)

                h = httplib2.Http()

                resp, content = h.request(url)

                row += 1

                print('row - ' + str(row) + ' content\n - ' + content.decode('utf-8'))

                print(json.dumps(resp))

    r.delete('sending_sms')

    print('sending sms finished')

    return JsonResponse(row, safe=False)
