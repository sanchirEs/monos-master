"""

Campaign models
Created by Mezorn LLC

"""
from datetime import datetime
from django.db import models
from receptmanager.models import ReceptManager, Notification
from productmanager.models import ProductManager
from receptmanager.notification import send_notification


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


class Campaign(BaseModel):

    """
    Campaigns's model
    """

    REGULAR_CAMPAIGN = 0

    TIMED_CAMPAIGN = 1

    CAMPAIGN_TYPE = (
        (REGULAR_CAMPAIGN, 'Энгийн хөтөлбөр'),
        (TIMED_CAMPAIGN, 'Хугацаат хөтөлбөр'),
    )

    PHARMACIST_CAMPAIGN = 0

    BEAUTICIAN_CAMPAIGN = 1

    CAMPAIGN_CATEGORY = (
        (PHARMACIST_CAMPAIGN, 'Эмийн санчид'),
        (BEAUTICIAN_CAMPAIGN, 'Гоо сайханчид'),
    )

    product_name = models.CharField(max_length=200, default='', verbose_name='Бүтээгдэхүүний нэр')

    product_desc = models.TextField(verbose_name='Бүтээгдэхүүний тайлбар')

    product_hash = models.CharField(max_length=200, verbose_name='Бүтээгдэхүүний #hash', default='', unique=True)

    is_active = models.BooleanField(default=True, verbose_name='Идэвхтэй эсэх')

    start_date = models.DateTimeField(default=None, verbose_name='Хөтөлбөр эхлэх огноо')

    end_date = models.DateTimeField(default=None, verbose_name='Хөтөлбөр дуусах огноо')

    add_on_comment = models.IntegerField(default=15, verbose_name='Комментод өгөх xp')

    add_on_like = models.IntegerField(default=10, verbose_name='Like-д өгөх xp')

    add_on_test = models.IntegerField(default=10, verbose_name='Тестэнд нэг зөв хариултанд өгөх xp')

    add_on_total_test = models.IntegerField(default=0, verbose_name='Нийт тестэнд өгөх xp')

    add_on_advise = models.IntegerField(default=1, verbose_name='Зөвөлгөөнд өгөх xp')

    add_on_share = models.IntegerField(default=100, verbose_name='Шэйрт өгөх xp')

    campaign_type = models.IntegerField(default=0, verbose_name='Хөтөлбөрийн төрөл', choices=CAMPAIGN_TYPE)

    add_on_total = models.IntegerField(default=0, verbose_name='Боломжит xp')

    add_on_grand_total = models.IntegerField(default=0, verbose_name='Боломжит нийт xp')

    product_manager = models.ForeignKey(ProductManager, default=None, blank=True, null=True, verbose_name='Продакт менежер', related_name='my_campaigns', on_delete=models.DO_NOTHING)

    xp_total = models.IntegerField(default=0, verbose_name='Нийт авсан xp')

    post_count = models.IntegerField(default=0, verbose_name='Нийт материалын тоо')

    advice_count = models.IntegerField(default=0, verbose_name='Нийт зөвөлгөөний тоо')

    top_advice = models.OneToOneField('post.AdvicePost', default=None, verbose_name='Топ зөвөлгөө', on_delete=models.SET_DEFAULT, blank=True, null=True)

    top_post = models.OneToOneField('post.Post', default=None, verbose_name='Топ материал', on_delete=models.SET_DEFAULT, blank=True, null=True)

    campaign_category = models.IntegerField(default=None, verbose_name='Хөтөлбөрийн хамаарал', choices=CAMPAIGN_CATEGORY)

    coin_start_date = models.DateTimeField(default=None, verbose_name='Мойл олгож эхлэх огноо', null=True)

    coin_end_date = models.DateTimeField(default=None, verbose_name='Мойл олгож дуусаг огноо', null=True)


    def __str__(self):

        return self.product_name

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Хөтөлбөр'

        verbose_name_plural = 'Хөтөлбөрүүд'

        ordering = ['-created_date']

    def save(self, *args, **kwargs):

        if self.start_date is not None:

            self.start_date = datetime(self.start_date.year, self.start_date.month, self.start_date.day, 0, 0, 1)

        if self.end_date is not None:

            self.end_date = datetime(self.end_date.year, self.end_date.month, self.end_date.day, 23, 59, 59)

        if self.coin_start_date is not None:

            self.coin_start_date = datetime(self.coin_start_date.year, self.coin_start_date.month, self.coin_start_date.day, 0, 0, 1)

        if self.coin_end_date is not None:

            self.coin_end_date = datetime(self.coin_end_date.year, self.coin_end_date.month, self.coin_end_date.day, 23, 59, 59)


        if self.id is None:

            managers = ReceptManager.objects.values_list('id', flat=True).filter(manager_type=self.campaign_category)
            for manager in managers:

                notification = Notification(manager_id=manager, title="Шинэ хөтөлбөр", content=self.product_name, is_public=True, type=2, url="http://m.me/2018267958393888")

                notification.save()

            send_notification.delay("Шинэ хөтөлбөр", self.product_name, list(managers))

        super(Campaign, self).save(*args, **kwargs)

    def set_test_xp(self):
        """ set test questions count"""
        from onlinetest.models import OnlineTest

        try:

            current_test = self.current_test

            self.add_on_total_test = current_test.questions.all().count() * self.add_on_test

        except OnlineTest.DoesNotExist:

            pass

        self.save()

    def calculate_total_xp(self):
        """ calculate total xp"""
        self.set_test_xp()

        posts_count = self.posts.all().count()

        self.add_on_total = self.add_on_total_test + posts_count*(self.add_on_like + self.add_on_comment) + self.add_on_advise

        rx_count = ReceptManager.objects.count()

        self.add_on_grand_total = self.add_on_total * rx_count

        self.save()

    def get_current_test(self):
        """ get current test """
        from onlinetest.models import OnlineTest

        current_test = None

        try:

            current_test = self.current_test

            if self.is_active is False:

                current_test = None

        except OnlineTest.DoesNotExist:

            current_test = None

        return current_test

    def get_axis_product_id_dict(self):

        campaigns = Campaign.objects.values_list('axis_product_id', flat=True).exclude(axis_product_id__isnull=True)

        campaign_data_list = list()

        for campaign in campaigns:

            campaign_data = dict()

            campaign_data['axis_product_id'] = self.axis_product_id

            campaign_data_list.append(campaign_data)

        return campaign_data_list

class CampaignAxis(BaseModel):

    campaign = models.ForeignKey(Campaign, default=None, verbose_name='Хамаарах хөтөлбөр', related_name='campaign_axis', on_delete=models.CASCADE)

    axis_product_id = models.IntegerField(verbose_name='Axis Product ID', null=True, blank=True)

    axis_xp_multiply = models.FloatField(verbose_name='XP Multiply', null=True, blank=True)

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Axis-н мэдээлэл'

        verbose_name_plural = 'Axis-н мэдээлэлүүд'

        ordering = ['-created_date']

class CampaignData(BaseModel):
    """ Campaign data model """

    related_campaign = models.ForeignKey(Campaign, default=None, verbose_name='Хамаарах хөтөлбөр', related_name='campaign_data', on_delete=models.CASCADE)

    manager = models.ForeignKey(ReceptManager, default=None, verbose_name='Эмийн санч', related_name='rx_data', on_delete=models.CASCADE)

    is_test_given = models.BooleanField(default=False, verbose_name='Тест өгсөн эсэх')

    xp_on_comment = models.IntegerField(default=0, verbose_name='Комментоос авсан xp')

    xp_on_like = models.IntegerField(default=0, verbose_name='Like-аас авсан xp')

    xp_on_test = models.IntegerField(default=0, verbose_name='Тестнээс авсан xp')

    xp_on_advise = models.IntegerField(default=0, verbose_name='Зөвөлгөөнөөс авсан xp')

    xp_on_share = models.IntegerField(default=0, verbose_name='Шэйрээс авсан xp')

    xp_total = models.IntegerField(default=0, verbose_name='Нийт авсан xp')

    result_on_test = models.CharField(max_length=500, verbose_name='Тест бөглөсөн байдал', default='', blank=True)

    advise_url = models.URLField(blank=True, null=True, verbose_name='Зөвлөгөөний линк', default='')

    liked_posts = models.TextField(blank=True, null=True, verbose_name='Лайк дарсан постууд', default='')

    commented_posts = models.TextField(blank=True, null=True, verbose_name='Коммент бичсэн постууд', default='')

    shared_posts = models.TextField(blank=True, null=True, verbose_name='Шэйрлэсэн постууд', default='')

    correct_answers_count = models.IntegerField(default=0, verbose_name='Зөв хариултын тоо')

    class Meta:
        """
        Class meta
        """

        indexes = [
            models.Index(fields=['related_campaign', 'manager']),
            models.Index(fields=['related_campaign'], name='campaign_idx'),
            models.Index(fields=['manager'], name='manager_idx'),
        ]

        verbose_name = 'Дата'

        verbose_name_plural = 'Дата'

        ordering = ['-created_date']

    def check_comment(self, commented_post_link):
        """ check comment """

        if commented_post_link not in self.commented_posts:

            if self.commented_posts:

                self.commented_posts += '#^#' + commented_post_link

            else:

                self.commented_posts = commented_post_link

            add_ond_comment = self.related_campaign.add_on_comment

            self.xp_on_comment += add_ond_comment

            self.save()

            return self.manager.increase_comment_xp_by(add_ond_comment)

        return None

    def commented_posts_pretty(self):
        """
        Commented posts pretty
        """

        pretty_posts = self.commented_posts.replace('#^#', '\n')

        return pretty_posts

    commented_posts_pretty.short_description = 'Коммент үлдээсэн постууд'

    def check_like(self, like_post_link):
        """ check like """

        if like_post_link not in self.liked_posts:

            if self.liked_posts:

                self.liked_posts += '#^#' + like_post_link

            else:

                self.liked_posts = like_post_link

            xp_on_like = self.related_campaign.add_on_like

            self.xp_on_like += xp_on_like

            self.save()

            return self.manager.increase_like_xp_by(xp_on_like)

        return None

    def liked_posts_pretty(self):
        """
        Liked posts pretty
        """

        pretty_posts = self.liked_posts.replace('#^#', '\n')

        return pretty_posts

    liked_posts_pretty.short_description = 'Лайк дарсан постууд'

    def check_share(self, share_post_link):
        """ check share """

        if share_post_link not in self.shared_posts:

            if self.shared_posts:

                self.shared_posts += '#^#' + share_post_link

            else:

                self.shared_posts = share_post_link

            self.xp_on_share += 1

            self.save()

            return self.manager.increase_xp_by(1)

        return None

    def increase_xp_on_advice(self, add_xp):
        """ increase xp on advice """

        if self.advise_url:

            add_on_advise = self.related_campaign.add_on_advise

            add_xp = add_xp*add_on_advise

            if add_xp > self.xp_on_advise:

                diff = add_xp - self.xp_on_advise

                self.xp_on_advise = add_xp

                self.manager.increase_advice_xp_by(diff)

                self.save()

    def check_advice(self, advice_post_link):
        """ check advice """

        if not self.advise_url:

            self.advise_url = advice_post_link

            self.save()

    def add_test_score(self):
        """ increase test score """

        if not self.is_test_given:

            add_on_test = self.related_campaign.add_on_test

            self.xp_on_test += add_on_test

            self.save()

            return self.manager.increase_test_xp_by(add_on_test)

    def add_test_score_with_result(self, score, result):
        """ add test score with results"""

        if not self.is_test_given:

            result_code = '#^#' + result.split('.')[0] + '.'

            if result_code in self.result_on_test:

                return (self.manager.rx_xp, self.manager.rx_level)

            now = datetime.now()

            end_date = self.related_campaign.end_date

            if end_date > now:

                add_on_test = self.related_campaign.add_on_test*score

                self.xp_on_test += add_on_test

                self.result_on_test += '#^#' + result

                self.save()

                self.correct_answers_count += score

                return self.manager.increase_test_xp_by(add_on_test)

            else:

                self.correct_answers_count += score

                self.result_on_test += '#^#' + result

                self.save()

        return (self.manager.rx_xp, self.manager.rx_level)


    def add_test_score_with_result_noxp(self, score, result):
        """ add test score with result"""

        if not self.is_test_given and score:

            self.correct_answers_count += score

            self.result_on_test += '#^#' + result

            self.save()

    def result_on_test_pretty(self):
        """ result on test pretty """

        pretty_result = self.result_on_test.replace('#^#', '\n')

        return pretty_result

    result_on_test_pretty.short_description = 'Тест бөглөсөн байдал'

    def finish_test(self):
        """ finish test result """

        if not self.is_test_given:

            self.is_test_given = True

            self.save()

        now = datetime.now()

        end_date = self.related_campaign.end_date

        if end_date > now:

            add_on_test = self.related_campaign.add_on_test

            return '"' + self.related_campaign.product_name + '"' + '\n' + str(self.related_campaign.current_test.questions.count()) + ' асуултаас ' + str(int(self.xp_on_test/add_on_test)) + '-г зөв хариулсан.'

        return '"' + self.related_campaign.product_name + '"' + '\n' + str(self.related_campaign.current_test.questions.count()) + ' асуултаас ' + str(self.correct_answers_count) + '-г зөв хариулсан.(Хөтөлбөр дууссан тул XP бодогдоогүй)'


    def finish_test_noxp(self):
        """ finish test result """

        if not self.is_test_given:

            self.is_test_given = True

            self.save()

        return '"' + self.related_campaign.product_name + '"' + '\n' + str(self.related_campaign.current_test.questions.count()) + ' асуултаас ' + str(self.correct_answers_count) + '-г зөв хариулсан.(Хөтөлбөр дууссан тул XP бодогдоогүй)'

    def add_and_finish(self):
        """ add and finish test """

        if not self.is_test_given:

            self.is_test_given = True

            add_on_test = self.related_campaign.add_on_test

            self.xp_on_test += add_on_test

            self.save()

            self.manager.increase_test_xp_by(1)

        return str(self.related_campaign.current_test.questions.count()) + ' асуултаас ' + str(self.xp_on_test/add_on_test) + '-г зөв хариулсан.'

    def add_and_finish_noxp(self):
        """ add and finish test """

        if not self.is_test_given:

            self.is_test_given = True

            self.correct_answers_count += 1

            self.save()

        return str(self.related_campaign.current_test.questions.count()) + ' асуултаас ' + str(self.correct_answers_count) + '-г зөв хариулсан.(Хөтөлбөр дууссан тул XP бодогдоогүй)'

    def save(self, *args, **kwargs):

        self.xp_total = self.xp_on_comment + self.xp_on_like + self.xp_on_test + self.xp_on_advise + self.xp_on_share

        super(CampaignData, self).save(*args, **kwargs)
