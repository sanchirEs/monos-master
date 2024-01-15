"""
productmanager's admin.

created by Mezorn LLC
"""

from django.contrib import admin
from receptmanager.models import ReceptManager

class ReceptManagerAdmin(admin.ModelAdmin):
    """
    productmanager's admin class.
    """

    empty_value_display = '-'

    list_max_show_all = 100

    list_per_page = 50

    list_display = ('image_tag', 'username', 'fullname', 'email', 'rx_xp', 'rx_level', 'rx_coin_balance', 'camp_coin_collected', 'bum_coin_collected')

    list_display_links = ('image_tag', 'username', 'fullname')

    list_filter = ('role',)

    readonly_fields = ('user', 'id', 'username', 'last_name', 'first_name', 'image_tag', 'facebook_id', 'facebook_id_workspace', 'rx_coin_collected', 'rx_coin_consumed', 'rx_coin_balance', 'rx_level', 'camp_coin_collected', 'bum_coin_collected')

    def get_readonly_fields(self, request, obj=None):

        if obj: # editing an existing object

            return self.readonly_fields + ('facebook_id_messenger',)

        return self.readonly_fields

    fieldsets = (
        (None, {
            'fields': ('user', 'id', 'facebook_id_messenger', 'username', 'email', 'last_name', 'first_name', 'role', 'title', 'department', 'location', 'is_active', 'rx_xp', 'rx_coin_collected', 'rx_coin_consumed', 'rx_coin_balance', 'rx_level', 'should_refetch', 'camp_coin_collected', 'bum_coin_collected')
        }),
        ('Нэмэлт мэдээлэл', {
            'classes': ('collapse',),
            'fields': ('image_tag', 'phone', 'address', 'facebook', 'about', 'facebook_id', 'facebook_id_workspace'),
        }),
    )

    radio_fields = {"role": admin.HORIZONTAL}

    search_fields = ['username', 'fullname', 'email']

    def get_queryset(self, request):
        qs = super(ReceptManagerAdmin, self).get_queryset(request)
        return qs.filter(manager_type=0)

    def save_model(self, request, obj, form, change):
        obj.manager_type = 0
        super().save_model(request, obj, form, change)

admin.site.register(ReceptManager, ReceptManagerAdmin)


class BeauticianManager(ReceptManager):
    
    class Meta:

        proxy = True

        verbose_name = 'Гоо сайханч (RX)'

        verbose_name_plural = 'Гоо сайханчид (RX)'

        ordering = ['fullname']

class BeauticianManagerAdmin(admin.ModelAdmin):
    """
    productmanager's admin class.
    """

    empty_value_display = '-'

    list_max_show_all = 100

    list_per_page = 50

    list_display = ('image_tag', 'username', 'fullname', 'email', 'rx_xp', 'rx_level', 'rx_coin_balance', 'camp_coin_collected', 'bum_coin_collected')

    list_display_links = ('image_tag', 'username', 'fullname')

    list_filter = ('role',)

    readonly_fields = ('user', 'id', 'username', 'last_name', 'first_name', 'image_tag', 'facebook_id', 'facebook_id_workspace', 'rx_coin_collected', 'rx_coin_consumed', 'rx_coin_balance', 'rx_level', 'camp_coin_collected', 'bum_coin_collected')

    def get_readonly_fields(self, request, obj=None):

        if obj: # editing an existing object

            return self.readonly_fields + ('facebook_id_messenger',)

        return self.readonly_fields

    fieldsets = (
        (None, {
            'fields': ('user', 'id', 'facebook_id_messenger', 'username', 'email', 'last_name', 'first_name', 'role', 'title', 'department', 'location', 'is_active', 'rx_xp', 'rx_coin_collected', 'rx_coin_consumed', 'rx_coin_balance', 'rx_level', 'should_refetch', 'camp_coin_collected', 'bum_coin_collected')
        }),
        ('Нэмэлт мэдээлэл', {
            'classes': ('collapse',),
            'fields': ('image_tag', 'phone', 'address', 'facebook', 'about', 'facebook_id', 'facebook_id_workspace'),
        }),
    )

    radio_fields = {"role": admin.HORIZONTAL}

    search_fields = ['username', 'fullname', 'email']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(manager_type=1)

    def save_model(self, request, obj, form, change):
        obj.manager_type = 1
        super().save_model(request, obj, form, change)

admin.site.register(BeauticianManager, BeauticianManagerAdmin)