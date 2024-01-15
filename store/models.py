"""
store's models.

created by Mezorn LLC
"""

import os
from django.db import models
from django.conf import settings
from django.utils.safestring import mark_safe
from monos.common_images import initial_setup, create_from_image
from receptmanager.models import ReceptManager, Notification
from django.core.validators import MaxValueValidator, MinValueValidator 
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


class StoreCategory(BaseModel):
    """
    storecategory's model
    """

    category_name = models.CharField(max_length=100, default='', verbose_name='Ангилал')

    category_order = models.IntegerField(default=0, verbose_name='Дараалал')

    category_icon = models.ImageField(default=None, verbose_name='Зураг')

    category_url = models.CharField(max_length=200, null=True, editable=False)

    dir_path = models.CharField(max_length=100, default="", blank=True, editable=False)

    upload_dir_path = models.CharField(max_length=100, default="", blank=True, editable=False)

    is_active = models.BooleanField(default=True, verbose_name='Идэвхтэй эсэх')

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Барааны Ангилал'

        verbose_name_plural = 'Барааны Ангилалууд'

        ordering = ['category_order']

    def __str__(self):

        return self.category_name

    def __init__(self, *args, **kwargs):

        super(StoreCategory, self).__init__(*args, **kwargs)

        if self.category_icon.name:

            setattr(self, '__original_icon', self.category_icon.name)

        else:

            setattr(self, '__original_icon', 'no_image')

    def save(self, *args, **kwargs):

        if self.id is None:

            super(StoreCategory, self).save(*args, **kwargs)

        dir_path = 'imagei/category/' + str(self.id)

        upload_path = 'tmp/cuploads/' + str(self.id)

        full_dir_path = settings.MEDIA_ROOT + dir_path

        full_upload_path = settings.MEDIA_ROOT + upload_path

        if not self.dir_path:

            os.mkdir(full_dir_path)

            self.dir_path = dir_path + '/'

            self.category_url = '/category/' + str(self.id) + '/'

        if not self.upload_dir_path:

            os.mkdir(full_upload_path)

            self.upload_dir_path = upload_path + '/'

        if self.category_icon.name and getattr(self, '__original_icon') != self.category_icon.name:

            super(StoreCategory, self).save(*args, **kwargs)

            initial_setup(self, 'category_icon', self.dir_path, check_size=(220, 220))

            create_from_image(self, 'category_icon', 'thumb', self.dir_path, (50, 50))

            setattr(self, '__original_icon', self.category_icon.name)

        super(StoreCategory, self).save(*args, **kwargs)

    def icon_tag(self):
        """
        Category icon tag
        """

        if self.category_icon.name and self.dir_path:

            thumb_path = self.dir_path + 'thumb.jpeg'

            return mark_safe('<img src="/media/%s" height="50" width="50"/>' % thumb_path)

        else:

            return 'Зураг байхгүй'

    icon_tag.short_description = 'Oдоогийн зураг'

    icon_tag.allow_tags = True


class StoreItem(BaseModel):

    """
    storeitems's model
    """

    category = models.ForeignKey(StoreCategory, on_delete=models.CASCADE, related_name='items', default=None)

    item_name = models.CharField(max_length=200, default='', verbose_name='Барааны нэр')

    item_desc = models.CharField(max_length=600, default='', verbose_name='Барааны тайлбар')

    item_price = models.BigIntegerField(default=0, verbose_name='Барааны үнэ')

    item_icon = models.ImageField(default=None, verbose_name='Зураг')

    item_url = models.CharField(max_length=200, null=True, editable=False)

    dir_path = models.CharField(max_length=100, default="", blank=True, editable=False)

    upload_dir_path = models.CharField(max_length=100, default="", blank=True, editable=False)

    is_active = models.BooleanField(default=True, verbose_name='Идэвхтэй эсэх')

    sold_count = models.BigIntegerField(default=0, verbose_name='Зарагдсан тоо')

    sold_count_daily = models.BigIntegerField(default=0, verbose_name='Зарагдсан тоо Өдрөөр')

    sold_count_weekly = models.BigIntegerField(default=0, verbose_name='Зарагдсан тоо долоо хоногоор')

    sold_count_monthly = models.BigIntegerField(default=0, verbose_name='Зарагдсан тоо сараар')

    required_level = models.IntegerField(default=1, null=False, verbose_name='Зарагдах Level', validators=[MinValueValidator(1)])

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Бараа'

        verbose_name_plural = 'Бараанууд'

        ordering = ['item_name']

    def __str__(self):

        return self.item_name

    def __init__(self, *args, **kwargs):

        super(StoreItem, self).__init__(*args, **kwargs)

        if self.item_icon.name:

            setattr(self, '__original_icon', self.item_icon.name)

        else:

            setattr(self, '__original_icon', 'no_image')

    def save(self, *args, **kwargs):

        if self.id is None:

            managers = ReceptManager.objects.values_list('id', flat=True).all()

            for manager in managers:

                notification = Notification(manager_id=manager, title="Шинэ бараа", content=self.item_name, is_public=True, type=4)

                notification.save()
            
            send_notification.delay("Шинэ бараа", self.item_name, list(managers))

            super(StoreItem, self).save(*args, **kwargs)

        dir_path = 'imagei/item/' + str(self.id)

        upload_path = 'tmp/uploads/' + str(self.id)

        full_dir_path = settings.MEDIA_ROOT + dir_path

        full_upload_path = settings.MEDIA_ROOT + upload_path

        if os.path.isdir(full_dir_path) is False:

            os.mkdir(full_dir_path)

            self.dir_path = dir_path + '/'

            self.item_url = '/item/' + str(self.id) + '/'

        if os.path.isdir(full_upload_path) is False:

            os.mkdir(full_upload_path)

            self.upload_dir_path = upload_path + '/'

        if self.item_icon.name and getattr(self, '__original_icon') != self.item_icon.name:

            super(StoreItem, self).save(*args, **kwargs)

            initial_setup(self, 'item_icon', self.dir_path, check_size=(300, 390))

            create_from_image(self, 'item_icon', 'thumb', self.dir_path, (300, 390))

            setattr(self, '__original_icon', self.item_icon.name)

        super(StoreItem, self).save(*args, **kwargs)

    def icon_tag(self):
        """
        Icon image tag
        """

        if self.item_icon.name and self.dir_path:

            thumb_path = self.dir_path + 'thumb.jpeg'

            return mark_safe('<img src="/media/%s" height="50" width="50"/>' % thumb_path)

        else:

            return 'Зураг байхгүй'

    icon_tag.short_description = 'Oдоогийн зураг'

    icon_tag.allow_tags = True

    def add_sold_count(self, count):
        """ increase sold count """

        self.sold_count += count

        self.sold_count_daily += count

        self.sold_count_weekly += count

        self.sold_count_monthly += count

        self.save()


class SalesData(BaseModel):
    """ Sale's data model """

    CREATED = 0

    SOLD = 1

    DELIVERED = 2

    SALES_STATUS = (
        (CREATED, 'Үүссэн'),
        (SOLD, 'Зарагдсан'),
        (DELIVERED, 'Хүргэгдсэн'),
    )

    item = models.ForeignKey(StoreItem, default=None, verbose_name='Бараа', related_name='sales', on_delete=models.CASCADE)

    manager = models.ForeignKey(ReceptManager, default=None, verbose_name='Худалдан авагч', related_name='sales', on_delete=models.CASCADE)

    amount = models.IntegerField(default=0, verbose_name='Тоо ширхэг')

    total = models.BigIntegerField(default=0, verbose_name='Нийт дүн')

    status = models.SmallIntegerField(default=0, verbose_name='Худалдан авалтын статус', choices=SALES_STATUS)

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Худалдан авалтын мэдээ'

        verbose_name_plural = 'Худалдан авалтын мэдээнүүд'

        ordering = ['-created_date']

    # def save(self, *args, **kwargs):

    #     self.xp_total = self.xp_on_comment + self.xp_on_like + self.xp_on_test + self.xp_on_advise + self.xp_on_share

    #     super(CampaignData, self).save(*args, **kwargs)


class ItemSaleWeekly(BaseModel):

    """
    item sale weekly data model
    """

    item = models.ForeignKey(StoreItem, related_name='weekly_sales', default=None, verbose_name='Бараа', on_delete=models.CASCADE)

    date = models.DateField(default=None, verbose_name='Огноо')

    amount = models.BigIntegerField(default=0, verbose_name='Тоо ширхэг')

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Долоо хоногийн барааны борлуулалт'

        verbose_name_plural = 'Долоо хоногийн барааны борлуулалт'

        ordering = ['-date', '-amount']


class ItemSaleDaily(BaseModel):

    """
    item sale daily data model
    """

    item = models.ForeignKey(StoreItem, related_name='daily_sales', default=None, verbose_name='Бараа', on_delete=models.CASCADE)

    date = models.DateField(default=None, verbose_name='Огноо')

    amount = models.BigIntegerField(default=0, verbose_name='Тоо ширхэг')

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Өдрийн барааны борлуулалт'

        verbose_name_plural = 'Өдрийн барааны борлуулалт'

        ordering = ['-date', '-amount']




class ItemSaleMonthly(BaseModel):

    """
    item sale monthly data model
    """

    item = models.ForeignKey(StoreItem, related_name='monthly_sales', default=None, verbose_name='Бараа', on_delete=models.CASCADE)

    year = models.IntegerField(default=2017, verbose_name='Он')

    month = models.IntegerField(default=2, verbose_name='Сар')

    amount = models.BigIntegerField(default=0, verbose_name='Тоо ширхэг')

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Сарын барааны борлуулалт'

        verbose_name_plural = 'Сарын барааны борлуулалт'

        ordering = ['-year', '-month', 'amount']
