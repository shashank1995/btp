from django.conf.urls import url

from . import views

urlpatterns = [
url(r'^$', views.index, name='index'),
url(r'^(?P<related_string>[\w\s\-]+)/$', views.related, name='related'),
]