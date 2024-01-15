""" user reg """
import csv
import requests
from receptmanager.models import ReceptManager


def reg_users():
    """ register existing users """

    with open('monosbot/csv/users.csv', newline='', encoding='utf-8') as csv_file:

        reader = csv.reader(csv_file, delimiter=',')

        row = 1

        for user_info in reader:

            names = user_info[0].split(' ')

            if len(names) == 2:

                first_name = names[0]

                last_name = names[1]

            else:

                first_name = user_info[0]

                last_name = user_info[0]

            email = user_info[1]

            print(str(row) + ' - ' + email)

            row += 1

            fbid = user_info[2]

            manager = ReceptManager.objects.filter(facebook_id_messenger=fbid).first()

            if manager is None:

                user_profile_url = 'https://graph.facebook.com/v2.11/%s?fields=picture,first_name,email,last_name&access_token=DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD' % fbid

                response_msg = requests.get(user_profile_url)

                try:

                    user_data = response_msg.json()

                    if 'id' in user_data:

                        user_data['email'] = email

                        user_data['first_name'] = first_name

                        user_data['last_name'] = last_name

                        manager = ReceptManager.create_from_dict(user_data)

                except (ValueError, KeyError):

                    pass


def reg_update_users():
    """ register existing users """

    with open('monosbot/csv/users.csv', newline='', encoding='utf-8') as csv_file:

        reader = csv.reader(csv_file, delimiter=',')

        row = 1

        for user_info in reader:

            email = user_info[1]

            print(str(row) + ' - ' + email)

            row += 1

            fbid = user_info[2]

            manager = ReceptManager.objects.filter(facebook_id_messenger=fbid).first()

            if manager is not None:
                # picture,first_name,email,last_name,
                # ?fields=work&access_token=DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD

                user_profile_url = 'https://graph.facebook.com/v2.12/%s?fields=title,department&access_token=DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD' % fbid

                response_msg = requests.get(user_profile_url)

                try:

                    user_data = response_msg.json()

                    if 'id' in user_data:

                        manager.update_title_department(user_data['title'], user_data['department'])

                except (ValueError, KeyError):

                    print('NOOOO TITLEEEE')

def location_user(request):
    # """ register existings user's location and department """

    with open('monosbot/csv/location_last.csv', newline='', encoding='utf-8') as csv_file:

        reader = csv.reader(csv_file, delimiter=',')

        row = 1 

        for user_info in reader:
            

            department = user_info[1]
            location = user_info[2]

            print(str(row) + ' - ' + department)
            row += 1
            user = ReceptManager.objects.filter(username=user_info[0]).first()

            if user is not None:

                user.location = location
                user.department = department

                user.save()

    

