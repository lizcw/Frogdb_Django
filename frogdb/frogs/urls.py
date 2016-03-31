from django.conf.urls import url


from . import views

app_name = 'frogs'
urlpatterns = [
    ##Using generic views instead
    url(r'^$', views.IndexView.as_view(), name='index'),

    ]
