from django.contrib import admin
from django.conf.urls import include, url

urlpatterns = [
    url(r'^$', 'home.views.home',name = 'dashboard'),
    # url(r'^edit-profile$', '../account.views.edit_profile', name = 'editProfile' ),
    # url(r'^edit-schedule$', '../account.views.edit_schedule', name= 'editSchedule'),
    # url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'login.html'}),
    # url(r'^logout$', 'django.contrib.auth.views.logout_then_login', name = 'logout'),
    # url(r'^view-profile/(?P<uname>\w+)$', '../account.views.view_profile', name = 'viewProfile'),
]
