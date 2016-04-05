from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.utils import timezone
from .models import Permit, Frog, Operation
from .forms import PermitForm, FrogForm, FrogDeathForm, FrogDisposalForm,OperationForm, LoginForm

## Index page
class IndexView(generic.ListView):
    template_name = 'frogs/index.html'
    context_object_name = 'shipment_list'
    def get_queryset(self):
        """Return the last five published questions."""
        return Permit.objects.order_by('-arrival_date')[:5]

## Home page - Landing page on login
class HomeView(generic.ListView):
    template_name = 'frogs/home.html'
    context_object_name = 'shipment_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Permit.objects.order_by('-arrival_date')[:5]
## Login
def logoutfrogdb(request):
    logout(request)
    return redirect('/frogs')
    # Redirect to a success page.

def loginfrogdb(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    print('DEBUG: user=', user)
    message = None
    if user is not None:
        if user.is_active:
            login(request, user)
            # Redirect to a success page.
        else:
            # Return a 'disabled account' error message
            message = 'Your account has been disabled. Please contact admin.'
    else:
        # Return an 'invalid login' error message.
        message = 'Login credentials are invalid. Please try again'
    return render(request, "frogs/home.html", {'errors': message, 'user': user})

#### PERMITS/SHIPMENTS
class PermitList(generic.ListView):
    template_name = 'frogs/shipmentlist.html'
    context_object_name = 'shipment_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Permit.objects.order_by('-arrival_date')

class PermitDetail(generic.DetailView):
    model = Permit
    context_object_name = 'shipment'
    template_name = 'frogs/shipmentview.html'


class PermitCreate(generic.CreateView):
    model = Permit
    template_name = 'frogs/permitcreate.html'
    form_class = PermitForm
    success_url = reverse_lazy('frogs:permit_list')

class PermitUpdate(generic.UpdateView):
    model = Permit
    form_class = PermitForm
    template_name = 'frogs/permitcreate.html'
    success_url = reverse_lazy('frogs:permit_list')

class PermitDelete(generic.DeleteView):
    model = Permit
    success_url = reverse_lazy("frogs:permit_list")


########## FROGS ############################################
class FrogList(generic.ListView):
    template_name = 'frogs/froglist.html'
    context_object_name = 'frogs'

    def get_queryset(self):
        return Frog.objects.order_by('-frogid')

class FrogDetail(generic.DetailView):
    model = Frog
    context_object_name = 'frog'
    template_name = 'frogs/frogview.html'

class FrogCreate(generic.CreateView):
    model = Frog
    template_name = 'frogs/frogcreate.html'
    form_class = FrogForm
    success_url = reverse_lazy('frogs:frog_list')

class FrogUpdate(generic.UpdateView):
    model = Frog
    form_class = FrogForm
    template_name = 'frogs/frogcreate.html'
    success_url = reverse_lazy('frogs:frog_list')

class FrogDelete(generic.DeleteView):
    model = Frog
    success_url = reverse_lazy("frogs:frog_list")

class FrogDeath(generic.UpdateView):
    model = Frog
    form_class = FrogDeathForm
    context_object_name = 'frog'
    template_name = 'frogs/frogdeath.html'
    success_url = reverse_lazy('frogs:frog_list')

class FrogDisposal(generic.UpdateView):
    model = Frog
    form_class = FrogDisposalForm
    context_object_name = 'frog'
    template_name = 'frogs/frogdisposal.html'
    success_url = reverse_lazy('frogs:frog_list')

########## OPERATIONS ############################################
class OperationList(generic.ListView):
    template_name = 'frogs/operationlist.html'
    context_object_name = 'operations'

    def get_frog(self):
        frog_id = self.kwargs['frogid']
        return Frog.objects.get(frogid=frog_id)

    def get_queryset(self):
        frog_id = self.kwargs['frogid']
        print('DEBUG:2 frogid=', frog_id)
        return Operation.objects.filter(frogid__id=frog_id)

class OperationSummary(generic.ListView):
    template_name = 'frogs/operationsummary.html'
    context_object_name = 'operations'

    def get_queryset(self):
        return Operation.objects.filter('-frogid')

class OperationDetail(generic.DetailView):
    model = Operation
    context_object_name = 'operation'
    template_name = 'frogs/operationview.html'

class OperationCreate(generic.CreateView):
    model = Operation
    template_name = 'frogs/operationcreate.html'
    form_class = OperationForm
    success_url = reverse_lazy('frogs:operation_list')

 #   def __init__(self):
 #       frog_id = self.kwargs['frogid']
 #       return Frog.objects.get(frogid=frog_id)

class OperationUpdate(generic.UpdateView):
    model = Operation
    form_class = OperationForm
    template_name = 'frogs/operationcreate.html'
    success_url = reverse_lazy('frogs:operation_list')

class OperationDelete(generic.DeleteView):
    model = Operation
    success_url = reverse_lazy("frogs:operation_list")