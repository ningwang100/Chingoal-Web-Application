from django.conf.urls import include, url
from forms import MyAuthenticationForm

urlpatterns = [

    url(r'^fb-login', 'account.views.fb_login'),
    url(r'^$', 'home.views.home', name='home'),
    url(r'^login$', 'account.views.login_user', name='login'),
    url(r'^logout$', 'django.contrib.auth.views.logout_then_login', name = 'logout'),
    url(r'^register/(?P<flag>\w+)$', 'account.views.register', name = 'register'),
    url(r'^edit-profile$', 'account.views.edit_profile', name= 'editProfile'),
    url(r'^view-profile/(?P<uname>\w+)$', 'account.views.view_profile', name = 'viewProfile'),
    url(r'^reset-password$', 'account.views.reset_password', name = 'resetPassword'),
    url(r'^new-password/(?P<token>.*)$', 'account.views.new_password', name = 'newPassword'),
    url(r'^edit-schedule$', 'account.views.edit_schedule', name= 'editSchedule'),
    url(r'^follow/(?P<uname>\w+)/(?P<isFollowing>\w+)/(?P<isLearner>\w+)$', 'account.views.follow', name = 'follow'),
    url(r'^post-question$', 'account.views.post_question',name='post'),
    url(r'^reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
            'account.views.reset_confirm', name='reset_confirm'),
    url(r'^reset/$', 'account.views.reset', name='reset'),
    url(r'^confirm/(?P<activation_key>\w+)/', ('account.views.register_confirm')),
    url(r'^get_photo/(?P<username>.*)$', 'account.views.get_photo', name = 'get_photo'),
    url(r'^send/(?P<receiver_name>\w+)/(?P<sender_name>\w+)$', 'account.views.send', name = 'send'),
    url(r'^reply/(?P<receiver_name>\w+)/(?P<sender_name>\w+)/(?P<replyid>\d+)$', 'account.views.reply', name = 'reply'),
    url(r'^dismiss/(?P<replyid>\d+)$', 'account.views.dismiss', name = 'dismiss'),
]
