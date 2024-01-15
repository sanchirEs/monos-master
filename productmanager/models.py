"""
productmanager's models.

created by Mezorn LLC
"""

import os
from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import validate_email
from django.conf import settings
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


class ProductManager(BaseModel):

    """
    productmanager's model
    """

    REGULAR_MANAGER = 0

    SECURITY_MANAGER = 1

    ROLE_TYPES = (
        (REGULAR_MANAGER, 'Менежер'),
        (SECURITY_MANAGER, 'Хяналтын менежер'),
    )

    username_validator = ASCIIUsernameValidator()

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='productmanagers', default=None, null=True, blank=True)

    fullname = models.CharField(max_length=100, default='', verbose_name='Бүтэн нэр', help_text='Бүтэн нэр автоматаар үүснэ')

    first_name = models.CharField(max_length=50, verbose_name='Нэр')

    last_name = models.CharField(max_length=50, verbose_name='Овог')

    username = models.CharField(max_length=50, unique=True, verbose_name='Нэвтрэх нэр', validators=[username_validator])

    email = models.CharField(max_length=50, unique=True, validators=[validate_email], verbose_name='Имэйл')

    role = models.IntegerField(default=0, verbose_name='Төрөл', choices=ROLE_TYPES)

    phone = models.CharField(max_length=20, default='', blank=True, verbose_name='Утасны дугаар')

    address = models.TextField(max_length=200, null=True, blank=True, default='', verbose_name='Гэрийн хаяг')

    facebook = models.CharField(max_length=80, default='', blank=True, verbose_name='Фэйсбүүк хаяг')

    about = models.TextField(max_length=144, default='', blank=True, verbose_name='Тухай')

    avatar = models.CharField(default='', blank=True, null=True, verbose_name='Зураг', max_length=500)

    is_active = models.BooleanField(default=True, verbose_name='Идэвхтэй эсэх')

    manager_id = models.IntegerField(unique=True, verbose_name='Axis manager ID', default=0)

    class Meta:
        """
        Class meta
        """

        verbose_name = 'Бүтээгдэхүүний Менежер (PX)'

        verbose_name_plural = 'Бүтээгдэхүүний Менежерүүд (PX)'

        ordering = ['username']

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

        group = Group.objects.filter(name='product_managers').first()

        if group is not None:

            group.user_set.add(user)

        manager = ProductManager(username=username, email=email, user=user, first_name=first_name, last_name=last_name)

        manager.save()

        return manager

    def __str__(self):

        return self.fullname + ' (' + self.fullname + ')'

    def delete(self, *args, **kwargs):

        if ProductManager.manager_has_user(self) is True:

            user = self.user

            user.delete()

        else:

            super(ProductManager, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):

        if self.last_name and self.first_name:

            self.fullname = self.last_name.title() + ' ' + self.first_name.upper()

        else:

            self.fullname = self.first_name.title()

        # if self.user is None:

        #     password = self.username + '1231'

        #     user = User.objects.create_user(username=self.username, email=self.email, password=password, first_name=self.first_name, last_name=self.last_name, is_staff=True)

        #     group = Group.objects.filter(name='product_managers').first()

        #     if group is not None:

        #         group.user_set.add(user)

        #     self.user = user

        super(ProductManager, self).save(*args, **kwargs)

    def image_tag(self):
        """
        Avatar image tag
        """

        if self.avatar and self.dir_path:

            return mark_safe('<img src="%s" height="50" width="50"/>' % self.avatar)

        else:

            return 'Зураг байхгүй'

    image_tag.short_description = 'Oдоогийн зураг'

    image_tag.allow_tags = True
