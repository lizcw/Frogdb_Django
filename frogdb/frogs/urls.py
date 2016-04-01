from django.conf.urls import url


from . import views

app_name = 'frogs'
urlpatterns = [
    ##Using generic views instead
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^permit/create/$', views.create_permit, name='permitcreate'),
    url(r'^permit/list/$', views.PermitList.as_view(), name='permitlist'),
    url(r'^(?P<pk>[0-9]+)/permit/view/$', views.PermitView.as_view(), name='permitview'),
    url(r'^(?P<pk>[0-9]+)/permit/edit/$', views.edit_permit, name='permitedit'),
    url(r'^frog/create/$', views.create_frog, name='frogcreate'),
    url(r'^frog/list/$', views.FrogList.as_view(), name='froglist'),
    url(r'^operation/create/$', views.create_frog, name='operationcreate'),

    ]
