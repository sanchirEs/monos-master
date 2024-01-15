""" store admin """
from django.contrib import admin
from store.models import StoreCategory, StoreItem, SalesData
from django.http import HttpResponse


class StoreCategoryAdmin(admin.ModelAdmin):
    """
    Store category's admin class.
    """

    empty_value_display = '-'

    list_max_show_all = 50

    list_per_page = 20

    list_display = ('icon_tag', 'category_name', 'category_order')

    list_display_links = ('icon_tag', 'category_name', 'category_order')

    readonly_fields = ('category_url', 'dir_path', 'upload_dir_path')

    fields = ('category_icon', 'category_name', 'category_order', 'category_url', 'dir_path', 'upload_dir_path', 'is_active')

    search_fields = ['category_name']

admin.site.register(StoreCategory, StoreCategoryAdmin)

class StoreItemAdmin(admin.ModelAdmin):
    """
    StoreItem's admin class.
    """

    empty_value_display = '-'

    list_max_show_all = 100

    list_per_page = 50

    list_display = ('icon_tag', 'item_name', 'item_price')

    list_display_links = ('icon_tag', 'item_name', 'item_price')

    list_filter = ('category',)

    readonly_fields = ('id', 'item_url', 'dir_path', 'upload_dir_path')

    fieldsets = (
        (None, {
            'fields': ('id', 'category', 'item_name', 'item_icon', 'item_desc', 'item_price', 'required_level', 'is_active')
        }),
        ('Нэмэлт мэдээлэл', {
            'classes': ('collapse',),
            'fields': ('item_url', 'dir_path', 'upload_dir_path'),
        }),
    )

    search_fields = ['item_name']

admin.site.register(StoreItem, StoreItemAdmin)


def export_csv(modeladmin, request, queryset):
    import csv
    from django.utils.encoding import smart_str
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=salesdata.csv'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer.writerow([
        smart_str(u"Бараа"),
        smart_str(u"Овог"),
        smart_str(u"Нэр"),
        smart_str(u"Худалдан авагч"),
        smart_str(u"Нийт дүн"),
        smart_str(u"Төлөв"),
        smart_str(u"Огноо"),
    ])

    data = SalesData.objects.order_by('-created_date').all()
    for obj in data:
        print(obj)
        writer.writerow([
            smart_str(obj.item),
            smart_str(obj.manager.last_name),
            smart_str(obj.manager.first_name),
            smart_str(obj.manager),
            smart_str(obj.total),
            smart_str(obj._meta.get_field('status').choices[obj.status][1]),
            smart_str(obj.created_date),
        ])
    return response
export_csv.short_description = u"Export"

class SalesDataAdmin(admin.ModelAdmin):
    """
    SalesData's admin class.
    """

    def has_add_permission(self, request):

        return False

    actions = [export_csv]

    empty_value_display = '-'

    list_max_show_all = 100

    list_per_page = 50

    list_display = ('item', 'get_last_name', 'get_first_name', 'manager', 'total', 'status', 'created_date', 'get_manager_phone', 'get_manager_location')

    list_display_links = ('item', 'total', 'manager', 'status', 'created_date')

    list_filter = ('item', 'manager', 'status')

    readonly_fields = ('id', 'item', 'manager', 'amount', 'total')

    fields = ('id', 'item', 'manager', 'amount', 'total', 'status')

    search_fields = ['item__item_name', 'manager__fullname']

    def get_item_price(self, obj):
        """ get item price"""
        return obj.item.item_price

    def get_first_name(self, obj):
        return obj.manager.first_name
    def get_last_name(self, obj):
        return obj.manager.last_name
    def get_manager_phone(self, obj):
        return obj.manager.phone
    def get_manager_location(self, obj):
        return obj.manager.location

    get_first_name.short_description = 'Нэр'
    get_last_name.short_description = 'Овог'
    get_manager_phone.short_description = 'Утас'
    get_manager_location.short_description = 'Салбар'
    
    get_item_price.short_description = 'Үнэ'

    get_item_price.admin_order_field = 'item__item_price'


admin.site.register(SalesData, SalesDataAdmin)
