"""
Online test's admin.

created by Mezorn LLC
"""

from django.contrib import admin
from onlinetest.models import OnlineTest, OnlineTestQuestion, OnlineTestAnswer

class OnlineTestAnswerAdmin(admin.TabularInline):
    """
    onlinetest answer's admin class.
    """

    model = OnlineTestAnswer

    extra = 1

    list_select_related = ('question',)

    # def get_queryset(self, request):

    #     qs = super().get_queryset(request)

    #     return qs.filter(owner=request.user)

class OnlineTestQuestionAdmin(admin.ModelAdmin):
    """
    onlinetest's admin class.
    """

    empty_value_display = '-'

    list_max_show_all = 100

    list_per_page = 50

    list_display = ('question',)

    list_display_links = ('question',)

    readonly_fields = ('order',)

    fields = ('order', 'question', 'related_test')

    search_fields = ['question']

    list_filter = ('related_test__test_name', 'related_test__related_campaign__is_active')

    inlines = [
        OnlineTestAnswerAdmin,
    ]


class OnlineTestQuestionAdminTabular(admin.TabularInline):
    """
    onlinetest question's tabular admin class.
    """

    model = OnlineTestQuestion

    extra = 1

    list_select_related = ('related_test',)

    fields = ('question',)

    show_change_link = True

    inlines = [
        OnlineTestAnswerAdmin,
    ]


class OnlineTestAdmin(admin.ModelAdmin):
    """
    onlinetest's admin class.
    """

    empty_value_display = '-'

    list_max_show_all = 100

    list_per_page = 50

    list_display = ('test_name',)

    list_display_links = ('test_name',)

    fields = ('test_name', 'related_campaign', 'is_active')

    search_fields = ['test_name']

    list_filter = ('related_campaign', )

    inlines = [
        OnlineTestQuestionAdminTabular,
    ]



admin.site.register(OnlineTest, OnlineTestAdmin)

admin.site.register(OnlineTestQuestion, OnlineTestQuestionAdmin)
