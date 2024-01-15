"""
productmanager's admin.

created by Mezorn LLC
"""

from django.contrib import admin
from productmanager.models import ProductManager

class ProductManagerAdmin(admin.ModelAdmin):
    """
    productmanager's admin class.
    """

    empty_value_display = '-'

    list_max_show_all = 100

    list_per_page = 50

    list_display = ('image_tag', 'username', 'fullname', 'phone')

    list_display_links = ('image_tag', 'username', 'fullname')

    list_filter = ('role',)

    readonly_fields = ('image_tag',)

    fieldsets = (
        (None, {
            'fields': ('user', 'username', 'email', 'last_name', 'first_name', 'role', 'is_active')
        }),
        ('Нэмэлт мэдээлэл', {
            'classes': ('collapse',),
            'fields': ('image_tag', 'avatar', 'phone', 'address', 'facebook', 'about'),
        }),
    )

    radio_fields = {"role": admin.HORIZONTAL}

    search_fields = ['username', 'fullname']

admin.site.register(ProductManager, ProductManagerAdmin)
