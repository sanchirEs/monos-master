""" Control Center """

from django.contrib import admin
from monoscontrol.models import MonosControl, MonosMsgControl, MonosMsgURL, WhiteListDomains
from monosbot.celery_tasks import send_message, send_message_urls
from receptmanager.notification import send_notification_by_managers
from campaign.models import Campaign

class MonosControlAdmin(admin.ModelAdmin):
    """
    control's admin class.
    """

    list_display = ('control_name', 'fetch_status',)

    list_display_links = ('control_name',)

    readonly_fields = ('control_name', 'group_id')

    fields = ('control_name', 'group_id', 'group_token', 'current_campaign', 'current_campaign_beautician', 'regenerate_campaign_data', 'fetch_campaign_post_data', 'clean_current_campaign', 'store_status')

    def has_add_permission(self, request):

        return False

    def has_delete_permission(self, request, obj=None):

        return False

    def get_actions(self, request):

        actions = super(MonosControlAdmin, self).get_actions(request)

        if 'delete_selected' in actions:

            del actions['delete_selected']

        return actions

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "current_campaign":
            kwargs["queryset"] = Campaign.objects.filter(campaign_category=0)
        if db_field.name == "current_campaign_beautician":
            kwargs["queryset"] = Campaign.objects.filter(campaign_category=1)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class MonosMsgURLAdmin(admin.StackedInline):
    """
    MonosMsgURL's admin class.
    """

    model = MonosMsgURL

    extra = 1

    list_select_related = ('control',)


class MonosMsgControlAdmin(admin.ModelAdmin):
    """
    msg control's admin class.
    """

    list_display = ('control_name',)

    list_display_links = ('control_name',)

    readonly_fields = ('control_name',)

    fields = ('control_name', 'managers', 'content', 'send_notification', 'category')

    inlines = [
        MonosMsgURLAdmin,
    ]

    radio_fields = {"category": admin.HORIZONTAL}

    def save_related(self, request, form, formsets, change):

        super(MonosMsgControlAdmin, self).save_related(request, form, formsets, change)
        # do something with the manytomany data from the admin

        all_managers = form.instance.managers.values_list('id', flat=True).filter(manager_type=form.instance.category)

        urls = list(form.instance.urls.all().values_list('image_url', 'url', 'title', 'description'))

        count = all_managers.count()

        url = ''
        if urls:
            url = urls[0][1]
        
        if form.instance.send_notification:
            send_notification_by_managers.delay(list(all_managers), 'Шинэ мессеж', str(form.instance.content)[:50]+'...', None, url)

        if form.instance.content and count:

            id_list = list(all_managers.values_list('facebook_id_messenger', flat=True))

            if urls:

                send_message_urls.delay(id_list, form.instance.content, urls)

            else:

                send_message.delay(id_list, form.instance.content)

            form.instance.content = ''

            form.instance.managers.clear()

            form.instance.urls.all().delete()

            form.instance.save()

    def has_add_permission(self, request):

        return False

    def has_delete_permission(self, request, obj=None):

        return False

    def get_actions(self, request):

        actions = super(MonosMsgControlAdmin, self).get_actions(request)

        if 'delete_selected' in actions:

            del actions['delete_selected']

        return actions


class WhiteListDomainsAdmin(admin.ModelAdmin):
    """
    WhiteListDomains's admin class.
    """

    list_display = ('domain_url',)

    list_display_links = ('domain_url',)

    fields = ('domain_url',)

admin.site.register(MonosControl, MonosControlAdmin)
admin.site.register(MonosMsgControl, MonosMsgControlAdmin)
admin.site.register(WhiteListDomains, WhiteListDomainsAdmin)
