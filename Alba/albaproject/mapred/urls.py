from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView, DetailView


urlpatterns = patterns('mapred.views',
    url(r'^$',
        RedirectView.as_view(
            url = 'auth/login/'),
        name = '2login'),
    url(r'^auth/login/$', 'login_view', name = 'login'),
    url(r'^auth/logout/$', 'logout_view', name = 'logout'),
    url(r'^home/$', 'home_view', name = 'home'),
    url(r'^job/define/$', 'define_job_view', name = 'define_job'),
    url(r'^job/(?P<job_id>\d+)/details/$',
        'job_details_view', name = 'job_details'),
    url(r'^job/(?P<job_id>\d+)/download/(?P<kind>output$|input$|mapred$)$',
        'job_download_view', name = 'job_download'),
    url(r'^job/history/$', 'job_history_view', name = 'job_history')
)
