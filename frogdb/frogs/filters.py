import django_filters

from .models import Permit, Frog
from django import template
from datetime import date, timedelta


class PermitFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Permit
        fields = ['aqis', 'qen','arrival_date']


class FrogFilter(django_filters.FilterSet):
    condition = django_filters.CharFilter(lookup_expr=['exact', 'iexact','contains'])
    remarks = django_filters.CharFilter(lookup_expr=['exact', 'iexact', 'contains'])
    gender = django_filters.ChoiceFilter(choices=[('', '---------'),
                                                     ('female', 'Female'),
                                                     ('male', 'Male')])
    death_date = django_filters.DateFromToRangeFilter()
    autoclave_date = django_filters.DateFromToRangeFilter()
    incineration_date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Frog