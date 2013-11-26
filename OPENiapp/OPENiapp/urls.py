from django.conf.urls import patterns, include, url

from django.contrib import admin

from django.views.generic.base import TemplateView

from user_management.SignIn import facebook, twitter

from views import *

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^OPENiapp/', include('OPENiapp.foo.urls')),

                       # Home Page
                       url(r'^$', home, name='home'),

                       url(r'^admin/', include(admin.site.urls), name='admin'),

                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       url(r'^accounts/', include('allauth.urls'), name='accounts'),
                       
                       url(r'^photo/', include('OPENiapp.Objects.Photo.urls'), name='photo'),

                       #https://github.com/mpetyx/moodeet/wiki/Facebook
                       url(r'^person/signin/facebook$', facebook, name='facebook'),

                       #https://github.com/mpetyx/moodeet/wiki/Twitter
                       url(r'^person/signin/twitter$', twitter, name='twitter'),

                       url(r'^accounts/profile/$', TemplateView.as_view(template_name='profile.html'), name='profile')
)
