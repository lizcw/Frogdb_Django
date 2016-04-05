from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.utils import timezone
from .models import Permit, Frog
from .forms import PermitForm, FrogForm, OperationForm, LoginForm

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
        return Permit.objects.order_by('-arrival_date')[:5]

class PermitFormView(generic.FormView):
    template_name = 'frogs/create.html'
    form_class = PermitForm
    success_url = reverse_lazy('frogs/permitlist')


class PermitView(generic.DetailView):
    model = Permit
    context_object_name = 'shipment'
    template_name = 'frogs/shipmentview.html'

    def get_context_data(self, **kwargs):
        context = super(PermitView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


def create_permit(request):
    if request.method == "POST":
        form = PermitForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            #post.author = request.user
            #post.published_date = timezone.now()
            post.save()
            #return redirect('post_detail', pk=post.pk)
            return redirect("frogs/permitlist")
    else:
        form = PermitForm()
    return render(request, "frogs/create.html", {'form': form, 'itemtype': 'Shipment'})

#TODO - not working
def edit_permit(request, permit_id):
    #permit = get_object_or_404(Permit, pk=permit_id)
    print('DEBUG: permit_id=', permit_id)
    if request.method == "POST":
        form = PermitForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect("frogs/permitlist")
    else:
        print('DEBUG: GET request')
        permit = Permit.objects.get(permit_id)
        print('DEBUG: found permit, qen=', permit.qen)
        form = PermitForm(instance=permit)
    return render(request, "frogs/create.html", {'form': form, 'itemtype': 'Edit Shipment'})

########## FROGS ############################################
class FrogList(generic.ListView):
    template_name = 'frogs/froglist.html'
    context_object_name = 'frogs'

    def get_queryset(self):
        return Frog.objects.order_by('-frogid')


class FrogView(generic.DetailView):
    model = Frog
    context_object_name = 'frog'
    template_name = 'frogs/frogview.html'

    def get_context_data(self, **kwargs):
        context = super(FrogView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


def create_frog(request):
    if request.method == "POST":
        form = FrogForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect("frogs/froglist")
    else:
        form = FrogForm()
    return render(request, "frogs/create.html", {'form': form, 'itemtype': 'Frog'})

############### OPERATIONS ##############################
def create_operation(request):
    if request.method == "POST":
        form = OperationForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect("frogs/permitlist")
    else:
        form = OperationForm()
    return render(request, "frogs/create.html", {'form': form, 'itemtype': 'Operation'})