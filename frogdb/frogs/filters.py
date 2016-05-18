import django_filters

from .models import Permit, Frog, Transfer, Experiment
from django import template
from datetime import date, timedelta
from django.forms import DateInput

class PermitFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='iexact')
    arrival_date = django_filters.DateFromToRangeFilter(label="Arrival Date From To",widget=django_filters.widgets.RangeWidget(attrs={'class': 'myDateClass', 'type': 'date','placeholder': 'Select a date'}), )

    class Meta:
        model = Permit
        fields = ['aqis', 'qen','arrival_date']


class FrogFilter(django_filters.FilterSet):
    condition = django_filters.CharFilter(lookup_expr=['exact', 'iexact','contains'])
    remarks = django_filters.CharFilter(lookup_expr=['exact', 'iexact', 'contains'])
    gender = django_filters.ChoiceFilter(choices=[('', '---------'),
                                                     ('female', 'Female'),
                                                     ('male', 'Male')])
    death_date = django_filters.DateFromToRangeFilter(label="Death Date From To", widget=django_filters.widgets.RangeWidget(attrs={'class': 'myDateClass','type': 'date', 'placeholder': 'Select a date'} ),)
    autoclave_date = django_filters.DateFromToRangeFilter(label="Autoclave Date From To", widget=django_filters.widgets.RangeWidget(attrs={'class': 'myDateClass','type': 'date', 'placeholder': 'Select a date'} ),)
    incineration_date = django_filters.DateFromToRangeFilter(label="Incineration Date From To", widget=django_filters.widgets.RangeWidget(attrs={'class': 'myDateClass','type': 'date', 'placeholder': 'Select a date'} ),)

    class Meta:
        model = Frog


class TransferFilter(django_filters.FilterSet):
    transfer_date = django_filters.DateFromToRangeFilter(label="Transfer Date From To", widget=django_filters.widgets.RangeWidget(attrs={'class': 'myDateClass','type': 'date', 'placeholder': 'Select a date'} ),)

    class Meta:
        model = Transfer

class ExperimentFilter(django_filters.FilterSet):
    transfer_date = django_filters.DateFromToRangeFilter(label="Transfer Date From To", widget=django_filters.widgets.RangeWidget(attrs={'class': 'myDateClass','type': 'date', 'placeholder': 'Select a date'} ),)

    class Meta:
        model = Experiment