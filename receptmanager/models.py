"""
receptmanager's models.

created by Mezorn LLC
"""
import requests
import redis
import datetime
import math
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import validate_email
from django.utils.safestring import mark_safe

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

class ReceptManager(BaseModel):

    """
    receptmanager's model
    """
    PHARMACIST = 0

    BEAUTICIAN = 1

    REGULAR_MANAGER = 0

    SECURITY_MANAGER = 1

    ROLE_TYPES = (
        (REGULAR_MANAGER, 'Менежер'),
        (SECURITY_MANAGER, 'Хяналтын менежер'),
    )

    MANAGER_TYPE = (
        (PHARMACIST, 'Эмийн санч'),
        (BEAUTICIAN, 'Гоо сайханч'),
    )

    username_validator = ASCIIUsernameValidator()

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='receptmanagers', default=None, null=True, blank=True)

    fullname = models.CharField(max_length=100, default='', verbose_name='Бүтэн нэр', help_text='Бүтэн нэр автоматаар үүснэ')

    first_name = models.CharField(max_length=50, verbose_name='Нэр', blank=True, null=True)

    last_name = models.CharField(max_length=50, verbose_name='Овог', blank=True, null=True)

    username = models.CharField(max_length=50, unique=True, verbose_name='Нэвтрэх нэр', validators=[username_validator], blank=True, null=True)

    title = models.CharField(max_length=150, default='', verbose_name='Албан тушаал', help_text='Албан тушаал автоматаар үүснэ')

    department = models.CharField(max_length=250, default='', verbose_name='Газар/хэлтэс', help_text='Газар хэлтэс автоматаар үүснэ')

    email = models.CharField(max_length=50, unique=True, validators=[validate_email], verbose_name='Имэйл', blank=True, null=True)

    role = models.IntegerField(default=0, verbose_name='Төрөл', choices=ROLE_TYPES)

    facebook_id = models.CharField(max_length=80, default='', blank=True, verbose_name='Фэйсбүүк ID')

    facebook_id_workspace = models.CharField(max_length=80, default='', blank=True, verbose_name='Фэйсбүүк ID(Workspace)')

    facebook_id_messenger = models.CharField(max_length=80, default='', blank=True, verbose_name='Фэйсбүүк ID(Messenger Bot)', unique=True)

    phone = models.CharField(max_length=20, default='', blank=True, verbose_name='Утасны дугаар')

    address = models.TextField(max_length=200, null=True, blank=True, default='', verbose_name='Гэрийн хаяг')

    facebook = models.CharField(max_length=80, default='', blank=True, verbose_name='Фэйсбүүк хаяг')

    about = models.TextField(max_length=144, default='', blank=True, verbose_name='Тухай')

    avatar_link = models.CharField(max_length=500, default='', blank=True, verbose_name='Зураг')

    manager_url = models.CharField(max_length=200, null=True, editable=False)

    is_active = models.BooleanField(default=True, verbose_name='Идэвхтэй эсэх')

    rx_xp = models.BigIntegerField(default=0, verbose_name='XP')

    rx_level = models.IntegerField(default=1, verbose_name='Level')

    rx_daily_xp = models.IntegerField(default=0, verbose_name='Өнөөдөр цуглуулсан XP')

    rx_weekly_xp = models.IntegerField(default=0, verbose_name='Энэ долоо хоногт цуглуулсан XP')

    rx_monthly_xp = models.IntegerField(default=0, verbose_name='Энэ сард цуглуулсан XP')

    rx_coin_collected = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн цуглуулсан зоос')

    rx_coin_consumed = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн зарцуулсан зоос')

    rx_coin_balance = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн үлдсэн зоос')

    rx_coin_daily_consumption = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн өдөрт зарцуулсан зоос')

    rx_coin_weekly_consumption = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн долоо хоногт зарцуулсан зоос')

    rx_coin_monthly_consumption = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн сард хоногт зарцуулсан зоос')

    rx_xp_on_comment = models.BigIntegerField(default=0, verbose_name='Хэрэглэгчийн комментоос цуглуулсан XP')

    rx_xp_on_advice = models.BigIntegerField(default=0, verbose_name='Хэрэглэгчийн зөвлөгөөнөөс цуглуулсан XP')

    rx_xp_on_test = models.BigIntegerField(default=0, verbose_name='Хэрэглэгчийн тестнээс цуглуулсан XP')

    rx_xp_on_like = models.BigIntegerField(default=0, verbose_name='Хэрэглэгчийн лайкаас цуглуулсан XP')

    rx_xp_on_share = models.BigIntegerField(default=0, verbose_name='Хэрэглэгчийн шэйрээс цуглуулсан XP')

    should_refetch = models.BooleanField(default=False, verbose_name='Мэдээлэл дахин татах')

    location = models.CharField(max_length=250, default='', verbose_name='Салбар', help_text='Салбар автоматаар үүснэ')

    badge_like = models.BooleanField(default=True, verbose_name='Badge like')

    badge_test = models.BooleanField(default=True, verbose_name='Badge test')

    badge_comment = models.BooleanField(default=True, verbose_name='Badge comment')

    badge_advice = models.BooleanField(default=True, verbose_name='Badge advice')

    badge_share = models.BooleanField(default=True, verbose_name='Badge share')

    bum_coin_collected = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Борлуулалтаас цуглуулсан мойл')

    bum_coin_collected_daily = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн өдөрт цуглуулсан зоос /Buman IT/')

    bum_coin_collected_weekly = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн 7 хоногт цуглуулсан зоос /Buman IT/')

    bum_coin_collected_monthly = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн сард цуглуулсан зоос /Buman IT/')

    camp_coin_collected = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Сургалтаас цуглуулсан мойл')

    camp_coin_collected_daily = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн өдөрт цуглуулсан зоос /Campaign/')

    camp_coin_collected_weekly = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн 7 хоногт цуглуулсан зоос /Campaign/')

    camp_coin_collected_monthly = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн сард цуглуулсан зоос /Campaign/')

    manager_type = models.IntegerField(default=None, verbose_name='Менежерийн төрөл', choices=MANAGER_TYPE)

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Эмийн санч (RX)'

        verbose_name_plural = 'Эмийн санчид (RX)'

        ordering = ['fullname']

    def update_title_department(self, title, department):
        """ update title department """

        self.title = title

        self.department = department

        self.save()

    def increase_xp_by(self, add_xp):
        """ increase xp by point """

        self.rx_xp += add_xp

        self.rx_daily_xp += add_xp

        self.rx_weekly_xp += add_xp

        self.rx_monthly_xp += add_xp

        self.save()

        return (self.rx_xp, self.rx_level)

    def increase_comment_xp_by(self, add_xp):
        """ increase xp on comment point """

        self.rx_xp_on_comment += add_xp

        return self.increase_xp_by(add_xp)

    def increase_advice_xp_by(self, add_xp):
        """ increase xp on advice point """

        self.rx_xp_on_advice += add_xp

        return self.increase_xp_by(add_xp)

    def increase_test_xp_by(self, add_xp):
        """ increase xp on test point """

        self.rx_xp_on_test += add_xp

        return self.increase_xp_by(add_xp)

    def increase_share_xp_by(self, add_xp):
        """ increase xp on test point """

        self.rx_xp_on_share += add_xp

        return self.increase_xp_by(add_xp)

    def increase_like_xp_by(self, add_xp):
        """ increase xp on like point """

        self.rx_xp_on_like += add_xp

        return self.increase_xp_by(add_xp)

    def consume_coin(self, coin):
        """ coin consumption """

        if coin > self.rx_coin_balance:

            return False

        self.rx_coin_consumed += coin

        self.rx_coin_daily_consumption += coin

        self.rx_coin_weekly_consumption += coin

        self.rx_coin_monthly_consumption += coin

        self.save()

        return True

    def get_xp_level(self):
        """ get xp and level point """

        return (self.rx_xp, self.rx_level)

    @classmethod
    def manager_has_user(cls, instance):
        """
        Checks if manager has related system user
        """

        has_user = False

        try:

            has_user = (instance.user is not None)

        except User.DoesNotExist:

            pass

        return has_user

    @classmethod
    def create_from_form(cls, username, email, password, first_name, last_name):
        """
        Create user from form
        """

        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name, is_staff=True)

        group = Group.objects.filter(name='recept_managers').first()

        if group is not None:

            group.user_set.add(user)

        manager = ReceptManager(username=username, email=email, user=user, first_name=first_name, last_name=last_name)

        manager.save()

        return manager

    @classmethod
    def create_from_dict(cls, facebook_user_dict):
        """
        Create user from form
        """

        facebook_messenger_id = facebook_user_dict['id']

        username = facebook_messenger_id

        password = username + '654789'

        email = facebook_user_dict['email']

        if not email:

            email = username + '@monos.mn'

        first_name = facebook_user_dict['first_name']

        last_name = facebook_user_dict['last_name']

        try:

            profile_picture = facebook_user_dict['picture']['data']['url']

        except KeyError:

            profile_picture = ''

        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name, is_staff=True)

        group = Group.objects.filter(name='recept_managers').first()

        if group is not None:

            group.user_set.add(user)

        manager = ReceptManager(username=username, email=email, user=user, first_name=first_name, last_name=last_name, facebook_id_messenger=facebook_messenger_id, avatar_link=profile_picture)

        manager.save()

        return manager

    def __str__(self):

        if self.last_name and self.first_name:

            return self.last_name[0].upper() + '.' + self.first_name.title()

        return self.fullname

    def delete(self, *args, **kwargs):

        r = redis.Redis(unix_socket_path='/tmp/redis.sock', encoding="utf-8", decode_responses=True)

        manager_key = 'rx:managers:' + self.facebook_id_messenger

        if r.exists(manager_key):

            r.delete(manager_key)

        if ReceptManager.manager_has_user(self) is True:

            user = self.user

            user.delete()

        else:

            super(ReceptManager, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):

        if not self.email or self.should_refetch:

            self.should_refetch = False

            fbid = self.facebook_id_messenger

            user_profile_url = 'https://graph.facebook.com/v2.11/%s?fields=picture,first_name,email,last_name,title,department,location&access_token=DQVJ1SWtIWlVUZA0JrNjd6UXJ0SXFuOTRYRUgwTWd3SU5aZAnkyeDNhQXR1eDJZAdWdhbGZASTUt2T0hXblhZAX0h5cVRmOEZAyU2tsZAVgwSVJGVk5lYVRVSV9WNVppa0ZAIVjRJWk9kZA1B3THVkOTVPdWNjeTd4NlFwY3ZA6a1ZApY0pDbTNEbW1wTDVWSFViVzl5UkZArWl9qWmxGN0Fia3RvdFNqVzQ1NGpFN1ZA1LTl5YzRXQVJpYW5NZATJxR1BQVkNuZAHNwYnRpLXktSkhnWXlZANkowSgZDZD' % fbid

            response_msg = requests.get(user_profile_url)

            try:

                user_data = response_msg.json()

                if 'id' in user_data:

                    self.username = fbid

                    email = None

                    try:

                        email = user_data['email']

                    except KeyError:

                        pass

                    if not email:

                        email = self.username + '@monos.mn'

                    self.email = email

                    self.first_name = user_data['first_name']

                    self.last_name = user_data['last_name']

                    try:

                        self.title = user_data['title']

                    except KeyError:

                        pass

                    try:

                        self.department = user_data['department']

                    except KeyError:

                        pass

                    try:

                        self.location = user_data['location']

                    except KeyError:

                        pass

                    try:

                        self.avatar_link = user_data['picture']['data']['url']

                    except KeyError:

                        self.avatar_link = ''

            except (ValueError, KeyError):

                return

        if self.id is None:

            super(ReceptManager, self).save(*args, **kwargs)

            r = redis.Redis(unix_socket_path='/tmp/redis.sock', encoding="utf-8", decode_responses=True)

            r.hdel('rxbot:user:requests', self.facebook_id_messenger)

        self.fullname = self.last_name.title() + ' ' + self.first_name.upper()

        if ReceptManager.manager_has_user(self) is False:

            user = User.objects.filter(Q(username=self.facebook_id_messenger) | Q(email=self.email)).first()
            
            if user is not None:

                self.user = user

            else:

                password = self.username + '654789'

                user = User.objects.create_user(username=self.username, email=self.email, password=password, first_name=self.first_name, last_name=self.last_name, is_staff=True)

                group = Group.objects.filter(name='recept_managers').first()

                if group is not None:

                    group.user_set.add(user)

                self.user = user

        if ReceptManager.manager_has_user(self):

            user = self.user
            user.email = self.email
            user.save()

        temp_rx = self.rx_xp

        #l = -1
        #s = 0
        #p = 100

        #while temp_rx >= 0:
        #    l += 1
        #    temp_rx -= p
        #    s += 1
        #    if s%5 == 0:
        #        s = 0
        #        p += 100

        # self.rx_level = int(self.rx_xp/100)
        l = math.floor(math.log(((float(temp_rx) / 100 - 1) / 2) + 1, 2) + 2)

        if self.rx_level < l:

            self.rx_coin_collected += 2**(l-2)

            self.camp_coin_collected += 2**(l-2)
            self.camp_coin_collected_daily += 2**(l-2)
            self.camp_coin_collected_weekly += 2**(l-2)
            self.camp_coin_collected_monthly += 2**(l-2)

            self.rx_level = l

            notification = Notification(manager_id=self.id ,is_public=False, type=1, point=l, read=False, title="+"+str(2**(l-2))+" мойл", content="Level "+str(self.rx_level)+" хүрч танд " + str(2**(l-2)) + " мойл орлоо")

            notification.save()
            badge = Notification.objects.filter(manager=self, read=0).count()
            send_single_notification(self, "+"+str(2**(l-2))+" мойл", "Level "+str(self.rx_level)+" хүрч танд " + str(2**(l-2)) + " мойл орлоо", badge)

        self.rx_coin_balance = self.rx_coin_collected - self.rx_coin_consumed

        super(ReceptManager, self).save(*args, **kwargs)

    def image_tag(self):
        """
        Avatar image tag
        """

        if self.avatar_link:

            return mark_safe('<img src="%s" height="50" width="50"/>' % self.avatar_link)

        else:

            return 'Зураг байхгүй'

    image_tag.short_description = 'Oдоогийн зураг'

    image_tag.allow_tags = True


class ReceptManagerData(BaseModel):

    """
    receptmanager's data model
    """

    manager = models.ForeignKey(ReceptManager, related_name='manager_data', default=None, verbose_name='Эмийн санч', on_delete=models.CASCADE)

    date = models.DateField(default=None, verbose_name='Огноо')

    rx_xp = models.BigIntegerField(default=0, verbose_name='XP')

    rx_level = models.IntegerField(default=0, verbose_name='Level')

    rx_weekly_xp = models.IntegerField(default=0, verbose_name='Энэ долоо хоногт цуглуулсан XP')

    rx_coin_collected = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн цуглуулсан зоос')

    bum_coin_collected = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Борлуулалтаас цуглуулсан мойл')

    rx_coin_consumed = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн зарцуулсан зоос')

    rx_coin_balance = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн үлдсэн зоос')

    rx_coin_weekly_consumption = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн долоо хоногт зарцуулсан зоос')

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Эмийн санчийн дата (RX)'

        verbose_name_plural = 'Эмийн санчидын дата (RX)'

        ordering = ['manager_id', '-date']

class ReceptManagerDataDaily(BaseModel):

    """
    receptmanager's data model
    """

    manager = models.ForeignKey(ReceptManager, related_name='manager_data_daily', default=None, verbose_name='Эмийн санч', on_delete=models.CASCADE)

    date = models.DateField(default=None, verbose_name='Огноо')

    rx_xp = models.BigIntegerField(default=0, verbose_name='XP')

    rx_level = models.IntegerField(default=0, verbose_name='Level')

    rx_daily_xp = models.IntegerField(default=0, verbose_name='Өнөөдөр цуглуулсан XP')

    rx_coin_collected = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн цуглуулсан зоос')

    bum_coin_collected = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Борлуулалтаас цуглуулсан мойл')

    rx_coin_consumed = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн зарцуулсан зоос')

    rx_coin_balance = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн үлдсэн зоос')

    rx_coin_daily_consumption = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн өдөрт зарцуулсан зоос')

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Эмийн санчийн дата (RX)'

        verbose_name_plural = 'Эмийн санчидын дата (RX)'

        ordering = ['manager_id', '-date']


class ReceptManagerDataMonthly(BaseModel):

    """
    receptmanager's data model
    """

    manager = models.ForeignKey(ReceptManager, related_name='manager_data_monthly', default=None, verbose_name='Эмийн санч', on_delete=models.CASCADE)

    year = models.IntegerField(default=2017, verbose_name='Он')

    month = models.IntegerField(default=2, verbose_name='Сар')

    rx_xp = models.BigIntegerField(default=0, verbose_name='XP')

    rx_level = models.IntegerField(default=0, verbose_name='Level')

    rx_monthly_xp = models.IntegerField(default=0, verbose_name='Энэ долоо хоногт цуглуулсан XP')

    rx_coin_collected = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн цуглуулсан зоос')

    bum_coin_collected = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Борлуулалтаас цуглуулсан мойл')

    rx_coin_consumed = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн зарцуулсан зоос')

    rx_coin_balance = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн үлдсэн зоос')

    rx_coin_monthly_consumption = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн долоо хоногт зарцуулсан зоос')

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Эмийн санчийн дата (RX)'

        verbose_name_plural = 'Эмийн санчидын дата (RX)'

        ordering = ['manager_id', '-year', '-month']


class Notification(BaseModel):

    manager = models.ForeignKey(ReceptManager, related_name='manager_data_notification', default=None, verbose_name='Эмийн санч', on_delete=models.CASCADE)

    is_public = models.BooleanField(default=False, verbose_name='Broadcast')

    type = models.IntegerField(default=0, verbose_name='Төрөл')

    point = models.BigIntegerField(default=0, verbose_name='Тоон утга')

    read = models.BooleanField(default=False, verbose_name='Уншсан эсэх')

    title = models.CharField(max_length=500, default='', verbose_name='Title')

    content = models.CharField(max_length=500, default='', verbose_name='Content')

    url = models.CharField(max_length=500, default="https://monos.workplace.com/chat/t/2018267958393888", verbose_name="Redirect URL")

    is_shared = models.BooleanField(default=False, verbose_name='is shared?')

class Device(BaseModel):

    manager = models.ForeignKey(ReceptManager, related_name='manager_device', default=None, verbose_name='Эмийн санч', on_delete=models.CASCADE)

    token = models.CharField(max_length=100, default='', verbose_name='Token', unique=True)

class Sales(BaseModel):

    from campaign.models import Campaign, CampaignAxis

    manager = models.ForeignKey(ReceptManager, related_name='manager_sales', default=None, verbose_name='Эмийн санч', on_delete=models.CASCADE)

    collected_coin = models.DecimalField(default=0, max_digits=65, decimal_places=2, verbose_name='Хэрэглэгчийн цуглуулсан зоос')

    collected_date = models.DateTimeField(auto_now=True)

    campaign = models.ForeignKey(Campaign, related_name='campaign_sales', default=None, on_delete=models.CASCADE)

    campaign_axis = models.ForeignKey(CampaignAxis, related_name='campaign_axis_sales', default=None, on_delete=models.CASCADE)

    quantity = models.DecimalField(max_digits=65, decimal_places=2, default=None, verbose_name='Борлуулалтын тоо ширхэг')

class SalesLog(BaseModel):

    from campaign.models import CampaignAxis

    manager = models.ForeignKey(ReceptManager, related_name='manager_sales_log', default=None, verbose_name='Эмийн санч', on_delete=models.CASCADE)

    collected_coin = models.DecimalField(max_digits=65, decimal_places=2, default=None, verbose_name='Хэрэглэгчийн цуглуулсан зоос')

    collected_date = models.DateTimeField(auto_now=False, auto_now_add=False, default=datetime.datetime.now)

    quantity = models.DecimalField(max_digits=65, decimal_places=2, default=None, verbose_name='Борлуулалтын тоо ширхэг')

    campaign_axis = models.ForeignKey(CampaignAxis, related_name='campaign_axis_sales_log', default=None, on_delete=models.CASCADE)

def send_single_notification(manager, title, content, badge):

    devices = Device.objects.filter(manager=manager)

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

