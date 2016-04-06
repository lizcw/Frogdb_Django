from django.conf.urls import url
from django.contrib.auth.views import login
from . import views

app_name = 'frogs'
urlpatterns = [
    ##Using generic views instead
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^home/$', views.HomeView.as_view(), name='home'),
    url(r'^login/$', views.loginfrogdb, name='loginform'),
    url(r'^logout/$', views.logoutfrogdb, name='logout'),
    url(r'^permit/create/$',
        views.PermitCreate.as_view(), name="permit_create"),
    url(r'^permit/(?P<pk>\d+)/$',
        views.PermitDetail.as_view(), name="permit_detail"),
    url(r'^permit/(?P<pk>\d+)/update/$',
        views.PermitUpdate.as_view(), name="permit_update"),
    url(r'^permit/(?P<pk>\d+)/delete/$',
        views.PermitDelete.as_view(), name="permit_delete"),
    url(r'^permit/list/$', views.PermitList.as_view(), name='permit_list'),
    url(r'^frog/list/$', views.FrogList.as_view(), name='frog_list'),
    url(r'^frog/create/$',
        views.FrogCreate.as_view(), name="frog_create"),
    url(r'^frog/(?P<pk>\d+)/$',
        views.FrogDetail.as_view(), name="frog_detail"),
    url(r'^frog/(?P<pk>\d+)/update/$',
        views.FrogUpdate.as_view(), name="frog_update"),
    url(r'^frog/(?P<pk>\d+)/delete/$',
        views.FrogDelete.as_view(), name="frog_delete"),
    url(r'^frog/(?P<pk>\d+)/death/$',
        views.FrogDeath.as_view(), name="frog_death"),
    url(r'^frog/(?P<pk>\d+)/disposal/$',
        views.FrogDisposal.as_view(), name="frog_disposal"),
    url(r'^operation/summary/$', views.OperationSummary.as_view(), name='operation_summary'),
    url(r'^operation/create/(?P<frogid>\w+)/$',
        views.OperationCreate.as_view(), name="operation_create"),
    url(r'^operation/(?P<pk>\d+)/$',
        views.OperationDetail.as_view(), name="operation_detail"),
    url(r'^operation/(?P<pk>\d+)/update/$',
        views.OperationUpdate.as_view(), name="operation_update"),
    url(r'^operation/(?P<pk>\d+)/delete/$',
        views.OperationDelete.as_view(), name="operation_delete"),
    ]
