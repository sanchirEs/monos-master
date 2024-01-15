""" Control Center """

from django.contrib import admin
from campaign.models import Campaign, CampaignData, CampaignAxis

class CampaignAxisAdmin(admin.TabularInline):
    model = CampaignAxis

    extra = 1

class CampaignAdmin(admin.ModelAdmin):
    """
    campaign's admin class.
    """

    empty_value_display = '-'

    list_max_show_all = 100

    list_per_page = 50

    list_display = ('id', 'product_name', 'start_date', 'end_date')

    list_display_links = ('product_name',)

    readonly_fields = ('id',)

    list_filter = ('campaign_category',)

    fieldsets = (
        (None, {
            'fields': ('id', 'product_name', 'product_desc', 'product_hash', 'campaign_category', 'is_active', 'start_date', 'end_date', 'coin_start_date', 'coin_end_date')
        }),
        ('XP бодолт', {
            'classes': ('collapse',),
            'fields': ('add_on_comment', 'add_on_like', 'add_on_test', 'add_on_advise', 'add_on_share'),
        }),
    )

    radio_fields = {"campaign_category": admin.HORIZONTAL}

    search_fields = ['product_name', 'product_desc', 'id']

    inlines = [
        CampaignAxisAdmin,
    ]

class CampaignDataAdmin(admin.ModelAdmin):
    """
    campaign data's admin class.
    """

    empty_value_display = '-'

    list_max_show_all = 100

    list_per_page = 50

    list_display = ('related_campaign', 'manager', 'xp_total')

    list_display_links = ('related_campaign', 'manager', 'xp_total')

    readonly_fields = (
        'related_campaign',
        'manager',
        'xp_total',
        'is_test_given',
        'result_on_test_pretty',
        'xp_on_comment',
        'xp_on_like',
        'xp_on_test',
        'xp_on_advise',
        'commented_posts_pretty',
        'liked_posts_pretty',
        'advise_url')

    fieldsets = (
        ('Эмийн санч/Хөтөлбөр ', {
            'fields': ('related_campaign', 'manager', 'xp_total', 'is_test_given')
        }),
        ('XP бодолт', {
            'classes': ('collapse',),
            'fields': (
                'xp_on_comment',
                'xp_on_like',
                'xp_on_test',
                'xp_on_advise',
                'liked_posts_pretty',
                'commented_posts_pretty',
                'result_on_test_pretty',
                'advise_url'
                ),
        }),
    )

    search_fields = ['related_campaign__product_name', 'manager__fullname']

    list_filter = ('manager', 'related_campaign')

admin.site.register(CampaignData, CampaignDataAdmin)
admin.site.register(Campaign, CampaignAdmin)
