"""
monos stores's URL Configuration
"""
from django.urls import path
from store.views import index as store_page, category_parameters as parameters, item_service, sales_data, index_data
from store.views_sales import buy_and_confirm

urlpatterns = [
    path('', store_page, name='store-page'),
    path('parameters', parameters, name='category-parameters'),
    path('items', item_service, name='item-service'),
    path('buy', buy_and_confirm, name='buy-confirm'),
    path('salesdata', sales_data, name='sales-data'),
    path('index_data', index_data, name='index-data'),
]
