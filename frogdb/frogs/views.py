from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from .models import Permit, Frog


class IndexView(generic.ListView):
    template_name = 'frogs/index.html'

    def get_queryset(self):
        """Return the last five published questions."""
        return Permit.objects.order_by('-arrival_date')[:5]