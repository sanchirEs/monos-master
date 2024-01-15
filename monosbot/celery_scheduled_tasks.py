"""
celery scheduled tasks for monosbot
"""
from __future__ import absolute_import
from celery import task
import redis
import requests
from django.db.models import Sum
from django.db.utils import IntegrityError
from monosbot.bot_check_users import get_user_id_redis
from post.models import Post, AdvicePost
from receptmanager.models import ReceptManager


import logging

REDISPOOL = redis.ConnectionPool(path='/tmp/redis.sock', encoding="utf-8", decode_responses=True, connection_class=redis.UnixDomainSocketConnection)

logger = logging.getLogger('APPNAME')

@task()
def testmethod(data):
    """
    test method
    """

    print('Incoming:\n' + data)


@task()
def summurize_campaign(campaign_id):
    """
    summarize campaign method
    """
    from campaign.models import Campaign, CampaignData

    fetch_post_data(campaign_id)
    #pylint: disable=W0612

    campaign, created = Campaign.objects.get_or_create(id=campaign_id)

    campaign_data_all = CampaignData.objects.filter(related_campaign=campaign_id)

    xp_total = campaign_data_all.aggregate(Sum('xp_total'))['xp_total__sum']

    campaign.xp_total = xp_total if xp_total is not None else 0

    campaign.post_count = campaign.posts.all().count()

    campaign.advice_count = campaign.advice_posts.all().count()

    campaign.top_advice = campaign.advice_posts.all().order_by('-like_count').first()

    campaign.top_post = campaign.posts.all().order_by('-like_count').first()

    campaign.save()


@task()
def fetch_post_data_lock(campaign_id):
    """
    fetch post data with lock
    """

    print('Fetching data on campaign:' + str(campaign_id))

    r = redis.Redis(connection_pool=REDISPOOL)

    if r.exists('post_fetch_status') or r.exists('each_ten_started'):

        print('Fetch exists returning.... ')

        return

    r.set('post_fetch_status', 'started', ex=120)

    group_token = r.hget('control_values', 'groupd_token')

    print('Group token : ' + group_token)

    fetch_post_data_on_group(campaign_id, group_token, r)

    summurize_campaign(campaign_id)

    print('Summarize done')

    r.delete('post_fetch_status')

    print('Fetch post Done. Deleted fetch status')


@task()
def fetch_post_data(campaign_id):
    """
    fetch post data
    """
    r = redis.Redis(connection_pool=REDISPOOL)

    group_token = r.hget('control_values', 'groupd_token')

    fetch_post_data_on_group(campaign_id, group_token, r)


@task()
def fetch_post_data_on_group(campaign_id, group_token, r):
    """
    fetch post data
    """
    from campaign.models import Campaign, CampaignData

    print('Starting fetch posts - ' + str(campaign_id))

    current_campaign = Campaign.objects.filter(id=campaign_id).first()

    if current_campaign is None:

        print('Current campaign not found')

        return

    bearer = 'Bearer ' + group_token

    headers = {'Authorization': bearer}

    posts = current_campaign.posts.all()

    print('post count - ' + str(posts.count()))

    delete_post_ids = list()

    for post in posts:

        print('Fetch Normal post - https://graph.facebook.com/v2.11/' + post.group_id + '_' + str(post.facebook_id) + '?fields=reactions.summary(true),comments.summary(true)')

        try:

            get_url = 'https://graph.facebook.com/v2.11/' + post.group_id + '_' + str(post.facebook_id) + '?fields=reactions.summary(true),comments.summary(true)'

        except:

            print('Fetch post failed ^^^')

            break

        print('Post url:' + get_url)

        response = requests.get(get_url, headers=headers)

        incoming_message = response.json()

        if 'error' in incoming_message:

            print('Error in incoming message:\n' + response.text)

            delete_post_ids.append(post.id)

            continue

        if 'reactions' in incoming_message:

            reactions_data = incoming_message['reactions']

            if 'summary' in reactions_data and 'total_count' in reactions_data['summary']:

                post.like_count = reactions_data['summary']['total_count']

            reactions_count = parse_reactions(reactions_data, campaign_id, r, str(post.facebook_id), headers)

            print('parsed :' + str(reactions_count) + ' posts')

        if 'comments' in incoming_message:

            comments_data = incoming_message['comments']

            if 'summary' in comments_data and 'total_count' in comments_data['summary']:

                post.comment_count = comments_data['summary']['total_count']

            comments_count = parse_comments(comments_data, campaign_id, r, str(post.facebook_id), headers)

            print('parsed :' + str(comments_count) + ' comments')

        post.save()

    Post.objects.filter(id__in=delete_post_ids).delete()

    advice_posts = current_campaign.advice_posts.all()

    delete_post_ids = list()

    for post in advice_posts:

        print('Fetch Advice post - https://graph.facebook.com/v2.11/' + post.group_id + '_' + str(post.facebook_id) + '?fields=reactions.summary(true),comments.summary(true)')

        try:

            get_url = 'https://graph.facebook.com/v2.11/' + post.group_id + '_' + str(post.facebook_id) + '?fields=reactions.summary(true),comments.summary(true)'

        except:

            print(' ^^^^^')

            break

        response = requests.get(get_url, headers=headers)

        incoming_message = response.json()

        if 'error' in incoming_message:

            delete_post_ids.append(post.id)

            continue

        if 'reactions' in incoming_message:

            reactions_data = incoming_message['reactions']

            if 'summary' in reactions_data and 'total_count' in reactions_data['summary']:

                post.like_count = reactions_data['summary']['total_count']

                new_xp = post.like_count
                #pylint: disable=W0612

                try:
                    campaign_data, created = CampaignData.objects.get_or_create(related_campaign_id=campaign_id, manager_id=post.related_manager_id)

                    campaign_data.increase_xp_on_advice(new_xp)

                except IntegrityError:

                    print('Advice Integrity error on campaign - ' + str(campaign_id) + ', manager - ' + str(post.related_manager_id))

        post.save()

    AdvicePost.objects.filter(id__in=delete_post_ids).delete()

    print('Post fetch done')


def parse_reactions(reactions_data, campaign_id, r, post_fbid, headers):
    """ parsing reactions """

    from campaign.models import CampaignData

    if 'data' not in reactions_data:

        return 0

    for data in reactions_data['data']:

        fbid = data['id']

        manager_id = get_user_id_redis(fbid, r)

        if manager_id:
            #pylint: disable=W0612

            try:
                campaign_data, created = CampaignData.objects.get_or_create(related_campaign_id=campaign_id, manager_id=manager_id)

                campaign_data.check_like(post_fbid)

            except (Exception, IntegrityError) as e:
                print(e)
                print('Integrity error on campaign - ' + str(campaign_id) + ', manager - ' + str(manager_id))

    if 'paging' in reactions_data and 'next' in reactions_data['paging']:

        get_url = reactions_data['paging']['next']

        response = requests.get(get_url, headers=headers)

        return len(reactions_data['data']) + parse_reactions(response.json(), campaign_id, r, post_fbid, headers)

    else:

        return len(reactions_data['data'])


def parse_comments(comments_data, campaign_id, r, post_fbid, headers):
    """ parsing comments """

    from campaign.models import CampaignData

    if 'data' not in comments_data:

        return 0

    for data in comments_data['data']:

        fbid = data['from']['id']

        manager_id = get_user_id_redis(fbid, r)

        if manager_id:
            #pylint: disable=W0612

            try:

                campaign_data, created = CampaignData.objects.get_or_create(related_campaign_id=campaign_id, manager_id=manager_id)

                campaign_data.check_comment(post_fbid)

            except IntegrityError:

                print('Integrity error on campaign - ' + str(campaign_id) + ', manager - ' + str(manager_id))


    if 'paging' in comments_data and 'next' in comments_data['paging']:

        get_url = comments_data['paging']['next']

        response = requests.get(get_url, headers=headers)

        return len(comments_data['data']) + parse_comments(response.json(), campaign_id, r, post_fbid, headers)

    else:

        return len(comments_data['data'])


@task()
def fetch_post_meta_data(post_id, facebook_id):
    """
    fetch post data
    """

    r = redis.Redis(connection_pool=REDISPOOL)

    post_meta_key = 'post_meta:' + str(post_id) + ':key'

    if r.exists(post_meta_key):

        return

    r.set(post_meta_key, 'fetching_data')

    group_id = r.hget('control_values', 'groupd_id')

    group_token = r.hget('control_values', 'groupd_token')

    bearer = 'Bearer ' + group_token

    headers = {'Authorization': bearer}

    get_url = 'https://graph.facebook.com/v2.11/' + group_id + '_' + str(facebook_id) + '?fields=picture,message,reactions.summary(true),attachments,comments.summary(true)'

    response = requests.get(get_url, headers=headers)

    incoming_message = response.json()

    r.set('post_response', response.text)

    if 'error' in incoming_message:

        r.delete(post_meta_key)

        return

    data_dict = dict()

    if 'message' in incoming_message:

        data_dict['post_name'] = incoming_message['message']

    if 'reactions' in incoming_message and 'summary' in incoming_message['reactions'] and 'total_count' in incoming_message['reactions']['summary']:

        data_dict['like_count'] = incoming_message['reactions']['summary']['total_count']

    if 'comments' in incoming_message and 'summary' in incoming_message['comments'] and 'total_count' in incoming_message['comments']['summary']:

        data_dict['comment_count'] = incoming_message['comments']['summary']['total_count']

    if 'attachments' in incoming_message and 'data' in incoming_message['attachments']:

        datas = incoming_message['attachments']['data']

        if datas:

            data = datas[0]

            if 'media' in data and 'image' in data['media'] and 'src' in data['media']['image']:

                data_dict['image_url'] = data['media']['image']['src']

    Post.objects.filter(id=post_id).update(**data_dict)


def fetch_post_meta_data_sync(post):
    """
    fetch post data
    """

    r = redis.Redis(connection_pool=REDISPOOL)

    post_meta_key = 'post_meta:' + str(post.id) + ':key'

    if r.exists(post_meta_key):

        return

    r.set(post_meta_key, 'fetching_data')

    group_token = r.hget('control_values', 'groupd_token')

    bearer = 'Bearer ' + group_token

    headers = {'Authorization': bearer}

    get_url = 'https://graph.facebook.com/v2.11/' + post.group_id + '_' + str(post.facebook_id) + '?fields=picture,message,reactions.summary(true),attachments,comments.summary(true)'

    response = requests.get(get_url, headers=headers)

    incoming_message = response.json()

    r.set('post_response', response.text)

    if 'error' in incoming_message:

        r.delete(post_meta_key)

        return

    if 'message' in incoming_message:

        post.post_name = incoming_message['message']

    if 'reactions' in incoming_message and 'summary' in incoming_message['reactions'] and 'total_count' in incoming_message['reactions']['summary']:

        post.like_count = incoming_message['reactions']['summary']['total_count']

    if 'comments' in incoming_message and 'summary' in incoming_message['comments'] and 'total_count' in incoming_message['comments']['summary']:

        post.comment_count = incoming_message['comments']['summary']['total_count']

    if 'attachments' in incoming_message and 'data' in incoming_message['attachments']:

        datas = incoming_message['attachments']['data']

        if datas:

            data = datas[0]

            if 'media' in data and 'image' in data['media'] and 'src' in data['media']['image']:

                post.image_url = data['media']['image']['src']

    r.delete(post_meta_key)


def fetch_post_meta_data_sync_onform(fbid, group_id):
    """
    fetch post data
    """

    r = redis.Redis(connection_pool=REDISPOOL)

    post_meta_key = 'post_meta:' + str(fbid) + ':key'

    if r.exists(post_meta_key):
        logger.error('returned, post_meta_key')
        return

    r.set(post_meta_key, 'fetching_data')

    group_token = r.hget('control_values', 'groupd_token')

    logger.error(group_token)

    bearer = 'Bearer ' + group_token

    headers = {'Authorization': bearer}

    get_url = 'https://graph.facebook.com/v2.11/' + group_id + '_' + fbid + '?fields=picture,message,reactions.summary(true),attachments,comments.summary(true)'

    response = requests.get(get_url, headers=headers)

    incoming_message = response.json()


    r.set('post_response', response.text)

    if 'error' in incoming_message:

        r.delete(post_meta_key)
        logger.error('returned, error on post_meta_key')
        logger.error(incoming_message)
        return None

    post_data = dict()

    if 'message' in incoming_message:

        post_data['post_name'] = incoming_message['message']

    if 'reactions' in incoming_message and 'summary' in incoming_message['reactions'] and 'total_count' in incoming_message['reactions']['summary']:

        post_data['like_count'] = incoming_message['reactions']['summary']['total_count']

    if 'comments' in incoming_message and 'summary' in incoming_message['comments'] and 'total_count' in incoming_message['comments']['summary']:

        post_data['comment_count'] = incoming_message['comments']['summary']['total_count']
 
    if 'attachments' in incoming_message and 'data' in incoming_message['attachments']:

        datas = incoming_message['attachments']['data']

        if datas:

            data = datas[0]

            if 'media' in data and 'image' in data['media'] and 'src' in data['media']['image']:

                post_data['image_url'] = data['media']['image']['src']

    r.delete(post_meta_key)

    return post_data
