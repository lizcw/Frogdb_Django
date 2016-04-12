# -*- coding: UTF-8 -*-
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.forms import ModelForm, DateInput, ImageField
from .models import Permit, Frog, Operation, Transfer, Experiment, FrogAttachment


class LoginForm(AuthenticationForm):
    class Meta:
        fields = ('username', 'password')
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}),
                   'password': forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password'})
                   }


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
            'arrival_date': DateInput(format=('%Y-%m-%d'),
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


class FrogDeathForm(ModelForm):
    class Meta:
        model = Frog
        fields = ('frogid',
                  'death',
                  'death_date',
                  'death_initials'
                  )
        widgets = {
            'death_date': DateInput(format=('%Y-%m-%d'),
                                        attrs={'class': 'myDateClass',
                                               'type': 'date',
                                               'placeholder': 'Select a date'}
                                        ),
        }


class FrogDisposalForm(ModelForm):
    class Meta:
        model = Frog
        fields = ('frogid',
                  'disposed',
                  'autoclave_date',
                  'autoclave_run',
                  'incineration_date'
                  )
        widgets = {
            'autoclave_date': DateInput(format=('%Y-%m-%d'),
                                      attrs={'class': 'myDateClass',
                                             'type': 'date',
                                             'placeholder': 'Select a date'}
                                      ),
            'incineration_date': DateInput(format=('%Y-%m-%d'),
                                        attrs={'class': 'myDateClass',
                                               'type': 'date',
                                               'placeholder': 'Select a date'}
                                        ),
        }


class FrogAttachmentForm(ModelForm):
    imgfile = forms.ImageField()

    class Meta:
        model = FrogAttachment
        fields = ('frogid',
                  'imagetype',
                  'imgfile',
                  'description',
                  )
        widgets = {
            'imgfile': forms.FileInput()
        }


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
            'opdate': DateInput(format=('%Y-%m-%d'),
                                attrs={'class': 'myDateClass',
                                        'type': 'date',
                                        'placeholder': 'Select a date'}
                                ),
        }

class TransferForm(ModelForm):
    class Meta:
        model = Transfer
        fields = ('operationid',
                  'volume',
                  'transfer_date',
                  'transporter',
                  'method',
                  'transferapproval',)
        widgets = {
            'transfer_date': DateInput(format=('%Y-%m-%d'),
                    attrs={'class': 'myDateClass',
                           'type': 'date',
                           'placeholder': 'Select a date'}
                                ),
        }

class ExperimentForm(ModelForm):
    class Meta:
        model = Experiment
        waste_type = forms.SelectMultiple()
        fields = ('transferid',
                  'received',
                  'transferred',
                  'used',
                  'expt_from',
                  'expt_to',
                  'expt_location',
                  'expt_disposed',
                  'disposal_sentby',
                  'disposal_date',
                  'waste_type',
                  'waste_content',
                  'waste_qty',
                  'autoclave_indicator',
                  'autoclave_complete')
        widgets = {
            'disposal_date': DateInput(format=('%Y-%m-%d'),
                    attrs={'class': 'myDateClass',
                           'type': 'date',
                           'placeholder': 'Select a date'}
                                ),

            'expt_from': DateInput(format=('%Y-%m-%d'),
                   attrs={'class': 'myDateClass',
                          'type': 'date',
                          'placeholder': 'Select a date'}
                   ),

            'expt_to': DateInput(format=('%Y-%m-%d'),
                    attrs = {'class': 'myDateClass',
                             'type': 'date',
                             'placeholder': 'Select a date'}
                    )
            }