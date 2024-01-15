from django.urls import path
from django.conf.urls import url
from monosmobile.views import reload_sales, update_fb_image, change_password, n_token, mobilehtml, share

urlpatterns = [
    path('reload_sales', reload_sales, name='reload_sales'),
    path('update_fb_image', update_fb_image, name='test-fb-image'),
    path('n_token', n_token, name='notification'),
    path('mobilehtml', mobilehtml, name='mobilehtml'),
    path('share', share, name='share'),
    # path('fix', fix, name='fix'),
    # path('user_create_csv', user_create_csv, name='user_create_csv'),
]