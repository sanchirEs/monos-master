""" check user related data """
import redis
from receptmanager.models import ReceptManager


REDISPOOL = redis.ConnectionPool(path='/tmp/redis.sock', encoding="utf-8", decode_responses=True, connection_class=redis.UnixDomainSocketConnection)


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


def check_manager_status(fbid):
    """ checking current status"""

    r = redis.Redis(connection_pool=REDISPOOL)

    manager_status = get_user_status_redis(fbid, r)

    if manager_status is None:

        return 0

    return manager_status


def check_user_name(fbid):
    """
    Check if user exists
    """

    r = redis.Redis(connection_pool=REDISPOOL)

    manager_key = 'rx:managers:' + fbid

    manager_name = r.hget(manager_key, 'name')

    if manager_name is None:

        manager = ReceptManager.objects.filter(facebook_id_messenger=fbid).first()

        if manager is None:

            # user_profile_url = 'https://graph.facebook.com/v2.11/%s?fields=picture,first_name,email,last_name&access_token=DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD' % fbid

            # response_msg = requests.get(user_profile_url)

            # try:

            #     user_data = response_msg.json()

            #     if 'id' in user_data:

            #         manager = ReceptManager.create_from_dict(user_data)

            #         manager_dict = rx_get_dict(manager)

            #         r.hmset(manager_key, manager_dict)

            #         manager_name = manager.first_name

            # except (ValueError, KeyError):

            return None

        else:

            manager_dict = rx_get_dict(manager)

            r.hmset(manager_key, manager_dict)

            manager_name = manager.first_name

    return manager_name


def get_user_status(fbid):
    """
    get user id redis init
    """

    r = redis.Redis(connection_pool=REDISPOOL)

    return get_user_status_redis(fbid, r)


def get_user_status_redis(fbid, r):
    """
    get user status
    """

    manager_key = 'rx:managers:' + fbid

    manager_status = r.hget(manager_key, 'status')

    if manager_status is None:

        manager = ReceptManager.objects.filter(facebook_id_messenger=fbid).first()

        if manager is None:

            # user_profile_url = 'https://graph.facebook.com/v2.11/%s?fields=picture,first_name,email,last_name&access_token=DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD' % fbid

            # response_msg = requests.get(user_profile_url)

            # try:

            #     user_data = response_msg.json()

            #     if 'id' in user_data:

            #         manager = ReceptManager.create_from_dict(user_data)

            #         manager_dict = rx_get_dict(manager)

            #         r.hmset(manager_key, manager_dict)

            #         manager_status = "0"

            # except (ValueError, KeyError):

            return None

        else:

            manager_dict = rx_get_dict(manager)

            r.hmset(manager_key, manager_dict)

            manager_status = "0"

    return int(manager_status)


def check_user_registration_request(fbid):
    """ register user registration request"""

    r = redis.Redis(connection_pool=REDISPOOL)

    return check_user_registration_request_redis(fbid, r)


def check_user_registration_request_redis(fbid, r):
    """ register user registration request"""

    r = redis.Redis(connection_pool=REDISPOOL)

    if r.hexists('rxbot:user:requests', fbid):

        return True

    return False


def register_user_request(fbid):
    """ register user request"""

    r = redis.Redis(connection_pool=REDISPOOL)

    if check_user_registration_request_redis(fbid, r):

        return (0, None)

    manager = ReceptManager.objects.filter(facebook_id_messenger=fbid).first()

    if manager:

        return (1, manager.first_name)

    r.hset('rxbot:user:requests', fbid, 1)

    return (2, None)


def get_user_id(fbid):
    """
    get user id redis init
    """

    r = redis.Redis(connection_pool=REDISPOOL)

    return get_user_id_redis(fbid, r)


def get_user_id_redis(fbid, r):
    """
    get user id
    """

    manager_key = 'rx:managers:' + fbid

    manager_id = r.hget(manager_key, 'id')

    if manager_id is None:

        manager = ReceptManager.objects.filter(facebook_id_messenger=fbid).first()

        if manager is None:

            # user_profile_url = 'https://graph.facebook.com/v2.11/%s?fields=picture,first_name,email,last_name&access_token=DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD' % fbid

            # response_msg = requests.get(user_profile_url)

            # try:

            #     user_data = response_msg.json()

            #     if 'id' in user_data:

            #         manager = ReceptManager.create_from_dict(user_data)

            #         manager_dict = rx_get_dict(manager)

            #         r.hmset(manager_key, manager_dict)

            #         manager_id = manager.id

            # except (ValueError, KeyError):

            return None

        else:

            manager_dict = rx_get_dict(manager)

            r.hmset(manager_key, manager_dict)

            manager_id = manager.id

    return int(manager_id)


def update_user_xp_level(fbid, r, xp_data):
    """
    get user id
    """

    manager_key = 'rx:managers:' + fbid

    r.hset(manager_key, 'xp', xp_data[0])

    r.hset(manager_key, 'level', xp_data[1])


def set_user_status_redis(fbid, r, status):
    """
    set user status
    """

    manager_key = 'rx:managers:' + fbid

    r.hset(manager_key, 'status', status)


def set_user_current_tag_name(fbid, r, c_tag, c_name):
    """
    set user status
    """

    manager_key = 'rx:managers:' + fbid

    r.hset(manager_key, 'status', 4)

    r.hset(manager_key, 'c_tag', c_tag)

    r.hset(manager_key, 'c_name', c_name)


def set_user_current_tag_name_with_status(fbid, r, c_tag, c_name, status):
    """
    set user status and tag and name
    """

    manager_key = 'rx:managers:' + fbid

    r.hset(manager_key, 'status', status)

    r.hset(manager_key, 'c_tag', c_tag)

    r.hset(manager_key, 'c_name', c_name)


def get_user_current_tag_name(fbid, r):
    """
    set user status
    """

    manager_key = 'rx:managers:' + fbid

    return (r.hget(manager_key, 'c_tag'), r.hget(manager_key, 'c_name'))


def reset_current_user_status_noredis(fbid):
    """
    reset
    """

    r = redis.Redis(connection_pool=REDISPOOL)

    return reset_current_user_status(fbid, r)


def reset_current_user_status(fbid, r):
    """
    set user status
    """

    manager_key = 'rx:managers:' + fbid

    r.hset(manager_key, 'status', 0)

    r.hdel(manager_key, 'c_tag')

    r.hdel(manager_key, 'c_name')
