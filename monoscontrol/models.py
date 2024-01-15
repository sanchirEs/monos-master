""" Control models """

from django.db import models
from django.core.validators import URLValidator
import redis
from campaign.models import Campaign
from receptmanager.models import ReceptManager, Notification
from monosbot.celery_scheduled_tasks import summurize_campaign, fetch_post_data_lock
from monosbot.views_settings import white_list_domains_service, white_list_domains_remove_service
from monos.common import clean_rx_data, set_current_campaign, clean_current_campaign, set_control_values, set_current_campaign_type


REDISPOOL = redis.ConnectionPool(path='/tmp/redis.sock', encoding="utf-8", decode_responses=True, connection_class=redis.UnixDomainSocketConnection)

def has_campaign(monoscontrol):
    """ Check if control has campaign """

    has = False

    try:

        has = (monoscontrol.current_campaign is not None)

    except Campaign.DoesNotExist:

        pass

    return has

def has_beautician_campaign(monoscontrol):
    """ Check if control has campaign """

    has = False

    try:

        has = (monoscontrol.current_campaign_beautician is not None)

    except Campaign.DoesNotExist:

        pass

    return has


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


class MonosControl(BaseModel):

    """
    Monos control's model
    """

    control_name = models.CharField(max_length=200, default='Ерөнхий удирдлага', verbose_name='Нэр')

    current_campaign = models.OneToOneField(Campaign, default=None, verbose_name='Идэвхтэй хөтөлбөр /Эмийн санч/', on_delete=models.SET_DEFAULT, blank=True, null=True, related_name='pharmacist_campaign')

    current_campaign_beautician = models.OneToOneField(Campaign, default=None, verbose_name='Идэвхтэй хөтөлбөр /Гоо сайханч/', on_delete=models.SET_DEFAULT, blank=True, null=True, related_name='beautician_campaign')

    regenerate_campaign_data = models.BooleanField(default=False, verbose_name='Хөтөлбөрийн өгөгдөл дахин үүсгэх')

    fetch_campaign_post_data = models.BooleanField(default=False, verbose_name='Хөтөлбөртэй холбоотой постын мэдээ татах')

    clean_current_campaign = models.BooleanField(default=False, verbose_name='Идэвхтэй хөтөлбөрийг арилгах')

    store_status = models.BooleanField(default=True, verbose_name='Дэлгүүрийн төлөв')

    group_id = models.CharField(max_length=100, verbose_name='Груп ID', default='154243908530765')

    group_token = models.CharField(max_length=500, verbose_name='Груп Access Token', default='DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD')

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Удирдлага'

        verbose_name_plural = 'Удирдлага'

        ordering = ['-created_date']

    def __str__(self):

        return self.control_name

    def __init__(self, *args, **kwargs):

        super(MonosControl, self).__init__(*args, **kwargs)

        if has_campaign(self):
            setattr(self, '__current_campaign', self.current_campaign.id)
        else:
            setattr(self, '__current_campaign', -1)

        if has_beautician_campaign(self):
            setattr(self, '__current_campaign_beautician', self.current_campaign_beautician.id)
        else:
            setattr(self, '__current_campaign_beautician', -1)

    def save(self, *args, **kwargs):

        set_control_values(self)

        if self.current_campaign is not None:
            set_current_campaign_type(self.current_campaign)

        if self.current_campaign_beautician is not None:
            set_current_campaign_type(self.current_campaign_beautician)

        if self.clean_current_campaign:

            self.regenerate_campaign_data = False

            if self.current_campaign is not None:

                summurize_campaign.delay(self.current_campaign.id)

                setattr(self, '__current_campaign', -1)

            clean_rx_data()

            self.clean_current_campaign = False

            self.current_campaign = None
            self.current_campaign_beautician = None

            super(MonosControl, self).save(*args, **kwargs)

            clean_current_campaign(self.campaign_category)

            return

        if self.current_campaign and getattr(self, '__current_campaign') != self.current_campaign.id:

            self.regenerate_campaign_data = False

            summurize_campaign.delay(getattr(self, '__current_campaign'))

            setattr(self, '__current_campaign', self.current_campaign.id)

            self.current_campaign.is_active = True

            self.current_campaign.calculate_total_xp()

            clean_rx_data()

            super(MonosControl, self).save(*args, **kwargs)

            set_current_campaign_type(self.current_campaign)

            return

        elif self.current_campaign is None and getattr(self, '__current_campaign') != -1:

            self.regenerate_campaign_data = False

            summurize_campaign.delay(getattr(self, '__current_campaign'))

            setattr(self, '__current_campaign', -1)

            clean_rx_data()

            super(MonosControl, self).save(*args, **kwargs)

            clean_current_campaign(self.campaign_category)

            return

        elif self.current_campaign and self.regenerate_campaign_data:

            self.regenerate_campaign_data = False

            super(MonosControl, self).save(*args, **kwargs)

            set_current_campaign_type(self.current_campaign)

            self.current_campaign.is_active = True

            self.current_campaign.set_test_xp()

        # BEAUTICIAN CAMPAIGN

        if self.current_campaign_beautician and getattr(self, '__current_campaign_beautician') != self.current_campaign_beautician.id:

            self.regenerate_campaign_data = False

            summurize_campaign.delay(getattr(self, '__current_campaign_beautician'))

            setattr(self, '__current_campaign_beautician', self.current_campaign_beautician.id)

            self.current_campaign_beautician.is_active = True

            self.current_campaign_beautician.calculate_total_xp()

            clean_rx_data()

            super(MonosControl, self).save(*args, **kwargs)

            set_current_campaign_type(self.current_campaign_beautician)

            return

        elif self.current_campaign_beautician is None and getattr(self, '__current_campaign_beautician') != -1:

            self.regenerate_campaign_data = False

            summurize_campaign.delay(getattr(self, '__current_campaign_beautician'))

            setattr(self, '__current_campaign_beautician', -1)

            clean_rx_data()

            super(MonosControl, self).save(*args, **kwargs)

            clean_current_campaign(self.campaign_category)

            return

        elif self.current_campaign_beautician and self.regenerate_campaign_data:

            self.regenerate_campaign_data = False

            super(MonosControl, self).save(*args, **kwargs)

            set_current_campaign_type(self.current_campaign_beautician)

            self.current_campaign_beautician.is_active = True

            self.current_campaign_beautician.set_test_xp()

        if self.current_campaign_beautician and self.fetch_campaign_post_data:

            fetch_post_data_lock.delay(self.current_campaign_beautician.id)

            self.fetch_campaign_post_data = False

            super(MonosControl, self).save(*args, **kwargs)

        super(MonosControl, self).save(*args, **kwargs)

    def fetch_status(self):
        """
        Fetch status
        """
        r = redis.Redis(connection_pool=REDISPOOL)

        if r.exists('post_fetch_status'):

            return 'Постын мэдээ татаж байна'

        else:

            return '-'

    fetch_status.short_description = 'Постын мэдээ шинэчлэлт'


class MonosMsgControl(BaseModel):

    """
    Monos control's model
    """

    CATEGORY = (
        (0, 'Эмийн санч'),
        (1, 'Гоо сайханч'),
    )

    control_name = models.CharField(max_length=200, default='Мессеж илгээх', verbose_name='Нэр')

    managers = models.ManyToManyField(ReceptManager, verbose_name='Хүлээн авагчид', blank=True)

    content = models.CharField(max_length=640, default='', verbose_name='Агуулга', blank=True, null=True)

    send_notification = models.BooleanField(default=False, verbose_name='Мэдэгдэл явуулах')

    category = models.IntegerField(default=0, verbose_name='Менежерийн төрөл', choices=CATEGORY)

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Мессеж удирдлага'

        verbose_name_plural = 'Мессеж удирдлага'

        ordering = ['-created_date']

    def __str__(self):

        return self.control_name



class MonosMsgURL(models.Model):

    """
    MonosMSG URLs
    """

    title = models.CharField(max_length=100, default='', verbose_name='Гарчиг')

    description = models.CharField(max_length=500, default='', verbose_name='Тайлбар')

    image_url = models.URLField(max_length=250, default='https://moilbot.monos.mn/media/monoso.jpeg', verbose_name='Зураг')

    url = models.URLField(max_length=250, default='', verbose_name='Линк')

    control = models.ForeignKey(MonosMsgControl, default=None, verbose_name='Мессеж удирдлага', related_name='urls', on_delete=models.CASCADE)

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Линк'

        verbose_name_plural = 'Линкүүд'


class WhiteListDomainsSet(models.QuerySet):
    """ white list manager """

    def delete(self, *args, **kwargs):

        urls = list()

        for obj in self:

            urls.append(obj.domain_url)

        white_list_domains_remove_service(urls)

        super(WhiteListDomainsSet, self).delete(*args, **kwargs)


class WhiteListDomains(models.Model):
    """
    White list urls
    """

    objects = WhiteListDomainsSet.as_manager()

    domain_url = models.CharField(max_length=250, default='', verbose_name='Линк', help_text='заавал http линк байх шаардлагатай', validators=[URLValidator])

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Цагаан линк'

        verbose_name_plural = 'Цагаан линкүүд'

    def __str__(self):

        return self.domain_url

    def save(self, *args, **kwargs):
        #pylint: disable=E1135
        if 'https' in self.domain_url:

            super(WhiteListDomains, self).save(*args, **kwargs)

            urls = list(WhiteListDomains.objects.values_list('domain_url', flat=True))

            white_list_domains_service(urls)

    def delete(self, *args, **kwargs):

        urls = [self.domain_url]

        super(WhiteListDomains, self).delete(*args, **kwargs)

        white_list_domains_remove_service(urls)
