# -*- coding: UTF-8 -*-
from django.forms import ModelForm, DateInput
from .models import Permit, Frog, Operation


class PermitForm(ModelForm):
    class Meta:
        model = Permit
        fields = ('aqis',
                  'qen',
                  'arrival_date',
                  'species',
                  'females',
                  'males',
                  'supplier',
                  'country')
        widgets = {
            'arrival_date': DateInput(format=('%d-%m-%Y'),
                                      attrs={'class': 'myDateClass',
                                             'type':'date',
                                             'placeholder': 'Select a date'}
                                      ),
        }


class FrogForm(ModelForm):
    class Meta:
        model = Frog
        fields = ('frogid',
                  'qen',
                  'tankid',
                  'species',
                  'gender',
                  'current_location',
                  'condition',
                  'remarks',
                  'aec',
                  )


class OperationForm(ModelForm):
    class Meta:
        model = Operation
        fields = ('frogid',
                  'opnum',
                  'opdate',
                  'anesthetic',
                  'volume',
                  'comments',
                  'initials')
        widgets = {
            'opdate': DateInput(format=('%d-%m-%Y'),
                                attrs={'class': 'myDateClass',
                                        'type': 'date',
                                        'placeholder': 'Select a date'}
                                ),
        }