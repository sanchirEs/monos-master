"""
Post's models.

created by Mezorn LLC
"""

import logging
from django.db import models
from django.template.defaultfilters import truncatechars
from campaign.models import Campaign
from receptmanager.models import ReceptManager, Notification
from monos.common import check_and_set_current_campaign
from receptmanager.notification import send_notification

logger = logging.getLogger('APPNAME')

class BaseModel(models.Model):

    """
    Base model
    """

    created_date = models.DateTimeField(auto_now_add=True)

    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Class meta
        """
        abstract = True


ALLOWED_URLS = ['154243908530765', '1272597072788273', '2149422908642584']

class PostSet(models.QuerySet):
    """ white list manager """

    def delete(self, *args, **kwargs):

        campaings = list()

        for obj in self:

            campaings.append(obj.related_campaing)

        super(PostSet, self).delete(*args, **kwargs)

        for campaign in campaings:

            check_and_set_current_campaign(campaign)

class Post(BaseModel):

    """
    Post's model
    """

    objects = PostSet.as_manager()

    post_url = models.URLField(max_length=500, verbose_name='Постын URL')

    post_name = models.TextField(default='', verbose_name='Гарчиг', blank=True)

    facebook_id = models.BigIntegerField(default=0, verbose_name='Фэйсбүүк ID', unique=True, blank=True)

    related_campaing = models.ForeignKey(Campaign, default=None, verbose_name='Хамааралтай хөтөлбөр', on_delete=models.CASCADE, related_name='posts')

    like_count = models.IntegerField(default=0, verbose_name='Лайкын тоо')

    comment_count = models.IntegerField(default=0, verbose_name='Комментын тоо')

    image_url = models.URLField(max_length=500, verbose_name='Постын зургийн URL', default='')

    refetch_data = models.BooleanField(default=False, verbose_name='Постын мэдээ дахин татах')

    group_id = models.CharField(default='154243908530765', verbose_name='Груп ID', max_length=50)

    def short_description(self):
        """short description"""
        if self.post_name:

            return truncatechars(self.post_name, 50)

        else:

            return 'Постын мэдээлэл байхгүй байна'

    short_description.short_description = 'Пост'

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Пост'

        verbose_name_plural = '1. Постууд'

        ordering = ['-related_campaing_id', '-like_count']

    def __str__(self):

        return str(self.facebook_id) + '-' + self.short_description()

    def __init__(self, *args, **kwargs):

        super(Post, self).__init__(*args, **kwargs)

        setattr(self, '__current_post_url', self.post_url)

    def save(self, *args, **kwargs):

        fetch = False

        if self.id is None or self.refetch_data or self.post_url != getattr(self, '__current_post_url'):

            fetch = True

            setattr(self, '__current_post_url', self.post_url)

        if fetch:

            group_id = ''

            for g_id in ALLOWED_URLS:

                if g_id in str(self.post_url):

                    group_id = g_id

                    break

            if not group_id:
                logger.error('returned, group_id')
                return

            initial_url = 'https://monos.workplace.com/groups/' + group_id + '/permalink/'

            try:

                facebook_id = int(self.post_url.replace(initial_url, '').replace('/', ''))

            except ValueError:
                logger.error('returned, value error')
                return

            from monosbot.celery_scheduled_tasks import fetch_post_meta_data_sync_onform

            post_data = fetch_post_meta_data_sync_onform(str(facebook_id), group_id)

            if post_data is None:
                logger.error('returned, post_data')
                return

            self.group_id = group_id

            self.facebook_id = facebook_id

            self.post_name = post_data['post_name']

            self.like_count = post_data['like_count']

            self.comment_count = post_data['comment_count']

            self.image_url = post_data['image_url'] if 'image_url' in post_data else ''

            self.refetch_data = False

        self.related_campaing.calculate_total_xp()

        if self.id is None:

            managers = ReceptManager.objects.values_list('id', flat=True).filter(manager_type=self.related_campaing.campaign_category)
            for manager in managers:

                notification = Notification(manager_id=manager, title="Шинэ пост", content=str(self.post_name)[:50] + '...', is_public=True, type=3, url=self.post_url)

                notification.save()

            send_notification.delay("Шинэ пост", str(self.post_name)[:50] + '...', list(managers))

        super(Post, self).save(*args, **kwargs)

        check_and_set_current_campaign(self.related_campaing)

    def delete(self, *args, **kwargs):

        related_campaign = self.related_campaing

        super(Post, self).delete(*args, **kwargs)

        check_and_set_current_campaign(related_campaign)


class AdvicePost(BaseModel):

    """
    Advice Post's model
    """

    related_manager = models.ForeignKey(ReceptManager, default=None, verbose_name='Зөвөлгөөг оруулсан менежер', on_delete=models.CASCADE, related_name='advice_posts')

    post_name = models.TextField(default='', verbose_name='Гарчиг', blank=True)

    facebook_id = models.BigIntegerField(default=0, verbose_name='Фэйсбүүк ID', unique=True)

    group_id = models.CharField(default='154243908530765', verbose_name='Груп ID', max_length=50)

    related_campaing = models.ForeignKey(Campaign, default=None, verbose_name='Хамааралтай хөтөлбөр', on_delete=models.CASCADE, related_name='advice_posts')

    like_count = models.IntegerField(default=0, verbose_name='Лайкын тоо')

    comment_count = models.IntegerField(default=0, verbose_name='Комментын тоо')

    post_url = models.URLField(max_length=500, verbose_name='Постын URL', default='')

    image_url = models.URLField(max_length=500, verbose_name='Постын зургийн URL', default='')

    def short_description(self):
        """short description"""
        if self.post_name:

            return truncatechars(self.post_name, 50)

        else:

            return 'Постын мэдээлэл байхгүй байна'

    short_description.short_description = 'Зөвөлгөө'

    def manager_name(self):
        """manager_name"""
        if self.related_manager:

            return self.related_manager.fullname

        else:

            return '-'

    manager_name.short_description = 'Зөвөлгөө оруулсан'

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Зөвөлгөө'

        verbose_name_plural = '2. Зөвөлгөөнүүд'

        ordering = ['-related_campaing_id', '-like_count']

    def __str__(self):

        return str(self.facebook_id) + '-' + self.short_description()
