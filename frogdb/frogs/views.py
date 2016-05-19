from django.shortcuts import get_object_or_404, render, redirect, resolve_url, render_to_response
from django.db import IntegrityError
from django.core.urlresolvers import reverse_lazy, reverse, clear_url_caches
from django.http import HttpResponseRedirect
from django.views import generic
from django_tables2 import RequestConfig
from django.utils.http import is_safe_url
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME, login, logout, authenticate
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView
from django.conf import settings
from ipware.ip import get_ip
from axes.utils import reset
from django.template import RequestContext
try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse # python3 support

from .models import Permit, Frog, Operation, Transfer, Experiment, FrogAttachment, Qap, Notes, Location
from .forms import PermitForm, FrogForm, FrogDeathForm, FrogDisposalForm, OperationForm, TransferForm, ExperimentForm, FrogAttachmentForm, BulkFrogForm, BulkFrogDeleteForm, ExperimentDisposalForm, ExperimentAutoclaveForm, BulkFrogDisposalForm, BulkExptDisposalForm, NotesForm, AxesCaptchaForm
from .tables import ExperimentTable,PermitTable,FrogTable,TransferTable, OperationTable,DisposalTable, FilteredSingleTableView, NotesTable, PermitReportTable
from .filters import FrogFilter, PermitFilter, TransferFilter, ExperimentFilter, OperationFilter
###AUTHORIZATION CLASS ##########################################################################
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin


#################################################################################################
## Index page
class IndexView(generic.ListView):
    template_name ='frogs/index.html'
    context_object_name = 'datalist'


    def get_shipment_count(self):
        return Permit.objects.count()

    def get_frog_count(self):
        return Frog.objects.count()

    def get_transfer_count(self):
        return Transfer.objects.count()

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['shipment_list']= self.get_shipment_count()
        context['frog_list'] = self.get_frog_count()
        context['transfer_list']= self.get_transfer_count()
        return context

    def get_queryset(self):
        """Return the all shipments"""
        return Permit.objects.all()

## Login
class LoginView(FormView):
    """
    Provides the ability to login as a user with a username and password
    """
    template_name = 'frogs/index.html'
    success_url = '/frogs'
    form_class = AuthenticationForm
    redirect_field_name = REDIRECT_FIELD_NAME

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()

        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        if user is not None:
            if user.is_active:
                login(self.request, user)
            else:
                # Return a 'disabled account' error message
                form.add_error = 'Your account has been disabled. Please contact admin.'

        else:
            # Return an 'invalid login' error message.
            form.add_error = 'Login credentials are invalid. Please try again'

        # If the test cookie worked, go ahead and
        # delete it since its no longer needed
        self.check_and_delete_test_cookie()
        return super(LoginView, self).form_valid(form)

    def form_invalid(self, form):
        """
        The user has provided invalid credentials (this was checked in AuthenticationForm.is_valid()). So now we
        set the test cookie again and re-render the form with errors.
        """
        self.set_test_cookie()
        return super(LoginView, self).form_invalid(form)

    def set_test_cookie(self):
        self.request.session.set_test_cookie()

    def check_and_delete_test_cookie(self):
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
            return True
        return False

    def get_success_url(self):
        if self.success_url:
            redirect_to = self.success_url
        else:
            redirect_to = self.request.POST.get(
                self.redirect_field_name,
                self.request.GET.get(self.redirect_field_name, ''))

        netloc = urlparse.urlparse(redirect_to)[1]
        if not redirect_to:
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
        # Security check -- don't allow redirection to a different host.
        elif netloc and netloc != self.request.get_host():
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
        return redirect_to
        #return reverse(redirect_to)


class LogoutView(RedirectView):
    """
    Provides users the ability to logout
    """
    #template_name = 'frogs/index.html'
    successurl = '/frogs'

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(self.successurl)

def locked_out(request):
    if request.POST:
        form = AxesCaptchaForm(request.POST)
        print('DEBUG: REQUEST=', request)
        if form.is_valid():
            print('DEBUG: FORM=', form)
            ip = get_ip(request)
            if ip is not None:
                print("we have an IP address=", ip)
                reset(ip=ip)

            return HttpResponseRedirect(reverse_lazy('frogs:index'))
    else:
        form = AxesCaptchaForm()

    return render_to_response('frogs/locked.html', dict(form=form), context_instance=RequestContext(request))


# def logoutfrogdb(request):
#     logout(request)
#     return redirect('/frogs')
#     # Redirect to a success page.
#
# def loginfrogdb(request):
#     username = request.POST['username']
#     password = request.POST['password']
#     try:
#         user = authenticate(username=username, password=password)
#
#         message = None
#         if user is not None:
#             if user.is_active:
#                 login(request, user)
#                  # Redirect to a success page.
#             else:
#                 # Return a 'disabled account' error message
#                 message = 'Your account has been disabled. Please contact admin.'
#     except:
#         # Return an 'invalid login' error message.
#         message = 'Login credentials are invalid. Please try again'
#
#     return render(request, "frogs/index.html", {'errors': message, 'user': user})
###########################################################################################
#### PERMITS/SHIPMENTS

class PermitList(LoginRequiredMixin, generic.ListView):
    template_name = 'frogs/shipment/shipment_list.html'
    context_object_name = 'shipment_list'
    raise_exception = True

    def get_queryset(self):
        table = PermitTable(Permit.objects.order_by('-arrival_date'))
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        return table

class PermitDetail(LoginRequiredMixin, generic.DetailView):
    model = Permit
    context_object_name = 'shipment'
    template_name = 'frogs/shipment/shipment_view.html'
    raise_exception = True

class PermitFilterView(FilteredSingleTableView):
    model = Permit
    table_class = PermitTable
    filter_class = PermitFilter

class PermitCreate(LoginRequiredMixin, generic.CreateView):
    model = Permit
    template_name = 'frogs/shipment/shipment_create.html'
    form_class = PermitForm
    raise_exception = True
    success_url = reverse_lazy('frogs:permit_list')

class PermitUpdate(LoginRequiredMixin, generic.UpdateView):
    model = Permit
    form_class = PermitForm
    template_name = 'frogs/shipment/shipment_create.html'
    success_url = reverse_lazy('frogs:permit_list')
    raise_exception = True

class PermitDelete(LoginRequiredMixin, generic.DeleteView):
    model = Permit
    success_url = reverse_lazy("frogs:permit_list")
    raise_exception = True

# Frog Log Quarantine Report
class ReportTableView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'frogs/shipment/report_froglog.html'
    raise_exception = True

    def get_queryset(self, **kwargs):
        species = self.kwargs.get('species')
        print('DEBUG: Species=', species)
        if (species == None):
            qs = Permit.objects.all()
        else:
            qs = Permit.objects.filter(species__name=species)

        return qs

    def get_context_data(self, **kwargs):
        context = super(ReportTableView, self).get_context_data(**kwargs)
        table = PermitReportTable(self.get_queryset())
        RequestConfig(self.request).configure(table)
        notes_table = NotesTable(Notes.objects.all().order_by('-note_date'))
        RequestConfig(self.request).configure(notes_table)

        context['species'] = self.kwargs.get('species')
        context['frognotes_table'] = notes_table
        context['table'] = table
        context['locations'] = Location.objects.all()
        context['genders'] =['female','male']
        context['frogs_table']= Frog.objects.all()
        return context

    # def pdfview(self, request):
    #     resp = HttpResponse(content_type='application/pdf')
    #     context = self.get_context_data()
    #     result = generate_pdf(self.template_name, file_object=resp, context=context)
    #     return result



########## FROGS ############################################
class FrogList(LoginRequiredMixin, generic.ListView):
    template_name = 'frogs/frog/frog_minilist.html'
    context_object_name = 'table'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(FrogList, self).get_context_data(**kwargs)
        list_title="Frogs List"
        if (self.kwargs.get('shipmentid')):
            sid = self.kwargs.get('shipmentid')
            shipment = Permit.objects.get(pk=sid)
            list_title = "Frogs for QEN %s" % shipment.qen
        context['list_title'] = list_title
        return context

    def get_queryset(self):
        print('DEBUG:kwargs', self.kwargs)
        qs = Frog.objects.all()
        if (self.kwargs.get('shipmentid')):
            sid = self.kwargs.get('shipmentid')
            shipment = Permit.objects.get(pk=sid)
            qs = qs.filter(qen=shipment)
            print('DEBUG:frogs per shipment=', qs.count())
        table = FrogTable(qs)
        RequestConfig(self.request, paginate={"per_page": 20}).configure(table)
        return table

class FrogFilterView(LoginRequiredMixin, FilteredSingleTableView):
    template_name = 'frogs/frog/frog_list.html'
    model = Frog
    table_class = FrogTable
    filter_class = FrogFilter
    raise_exception = True


class FrogDetail(LoginRequiredMixin, generic.DetailView):
    model = Frog
    context_object_name = 'frog'
    template_name = 'frogs/frog/frog_view.html'
    raise_exception = True

class FrogCreate(LoginRequiredMixin, generic.CreateView):
    model = Frog
    template_name = 'frogs/frog/frog_create.html'
    form_class = FrogForm
    raise_exception = True

    def form_valid(self, form):
        try:
            return super(FrogCreate, self).form_valid(form)
        except IntegrityError as e:
            form.add_error('frogid', 'Database Error: Unable to create Frog - see Administrator')
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('frogs:frog_detail', args=[self.object.id])

class FrogUpdate(LoginRequiredMixin, generic.UpdateView):
    model = Frog
    form_class = FrogForm
    template_name = 'frogs/frog/frog_create.html'
    raise_exception = True

    def get_success_url(self):
        return reverse('frogs:frog_detail', args=[self.object.id])

class FrogDelete(LoginRequiredMixin, generic.DeleteView):
    model = Frog
    success_url = reverse_lazy("frogs:frog_list")
    raise_exception = True

class FrogDeath(LoginRequiredMixin, generic.UpdateView):
    model = Frog
    form_class = FrogDeathForm
    context_object_name = 'frog'
    template_name = 'frogs/frog/frog_death.html'
    raise_exception = True

    def get_success_url(self):
        return reverse('frogs:frog_detail', args=[self.object.id])

class FrogDisposal(LoginRequiredMixin, generic.UpdateView):
    model = Frog
    form_class = FrogDisposalForm
    context_object_name = 'frog'
    template_name = 'frogs/frog/frog_disposal.html'
    raise_exception = True

    def get_success_url(self):
        return reverse('frogs:frog_detail', args=[self.object.id])

class FrogAttachment(LoginRequiredMixin, generic.CreateView):
    model = FrogAttachment
    form_class = FrogAttachmentForm
    context_object_name = 'frog'
    template_name = 'frogs/frog/frog_upload.html'
    raise_exception = True


    def get_success_url(self):
        return reverse('frogs:frog_detail', args=[self.object.frogid.pk])

    def get_initial(self):
        fid = self.kwargs.get('frogid')
        frog = Frog.objects.get(pk=fid)
        return {'frogid': frog}

class FrogBulkCreate(LoginRequiredMixin, generic.FormView):
    model = Frog
    form_class = BulkFrogForm
    template_name = "frogs/frog/bulkfrog_create.html"
    success_url = reverse_lazy("frogs:frog_list")
    fid = None
    raise_exception = True

    def form_valid(self, form):
        #Get shipment: number female/male
        self.fid = self.kwargs.get('shipmentid')
        shipment = Permit.objects.get(pk=self.fid)
        females = shipment.females
        males = shipment.males
        prefix = form.cleaned_data['prefix']
        startid = int(form.cleaned_data['startid'])
        qen = form.cleaned_data['qen']
        tankid = int(form.cleaned_data['tankid'])
        species = form.cleaned_data['species']
        location = form.cleaned_data['current_location']
        aec = form.cleaned_data['aec']
        bulk_list=[]
        #Check initial prefix unique
        firstfrogid = "%s%d" % (prefix, startid)
        print('BulkFrog: generating records from QEN=', shipment.qen)
        #Generate Frog objects
        for i in range(startid,(startid + females + males)):
            gender = 'female'
            if (i > (startid + females)):
                gender = 'male'
            frogid = "%s%d" % (prefix, i)
            frog = Frog()
            frog.frogid=frogid
            frog.qen=qen
            frog.tankid=tankid
            frog.species=species
            frog.gender=gender
            frog.current_location=location
            frog.condition= ''
            frog.remarks='auto-generated'
            frog.aec=aec
            print('Generated:Frog=',frog.frogid)
            bulk_list.append(frog)

        try:
            Frog.objects.bulk_create(bulk_list)
            print('BulkFrog: frogs generated=', len(bulk_list))
            return super(FrogBulkCreate, self).form_valid(form)
        except IntegrityError:
            return super(FrogBulkCreate, self).form_invalid(form)

    def get_initial(self):
        fid = self.kwargs.get('shipmentid')
        shipment = Permit.objects.get(pk=fid)
        #print('DEBUG: Shipment qen:', shipment.qen)
        return {'qen': shipment, 'species': shipment.species}

    def get_success_url(self):
        return reverse('frogs:frog_list_byshipment',kwargs={'shipmentid': self.fid})


#Delete frogs from a shipment
class FrogBulkDelete(LoginRequiredMixin, generic.FormView):
    template_name = 'frogs/frog/bulkfrog_confirm_delete.html'
    form_class=BulkFrogDeleteForm
    raise_exception = True


    def post(self, request, *args, **kwargs):
        print('DEBUG: post')
        froglist = self.get_queryset()
        #print('DELETING frogs', len(froglist))
        r = froglist.delete()
        message = 'Successfully deleted ' + str(r[0]) + ' frogs'
        print('DELETED: ', message, ' r=', r)
        return render(request, self.template_name, {'msg': message})

    def get_context_data(self, **kwargs):
        context = super(FrogBulkDelete, self).get_context_data(**kwargs)
        print('DEBUG: Get context data=', context)
       # print('DEBUG: Form=', context['form'])
        fid = self.kwargs.get('shipmentid')
        shipment = Permit.objects.get(pk=fid)
        froglist = self.get_queryset()
        context.update({
            'qen': shipment.qen,
            'species' : shipment.species,
            'pk': shipment
        })
        if (len(froglist) > 0):
            context['frogs'] = len(froglist)
        else:
            context['msg'] = 'There are NO frogs to delete for this shipment (QEN=%s)' % shipment.qen
        return context

    def get_queryset(self):
        fid = self.kwargs.get('shipmentid')
        print('DEBUG: Get queryset')
        shipment = Permit.objects.get(pk=fid)
        return Frog.objects.filter(qen=shipment)

    def get_success_url(self):
        print('DEBUG: Get success URL')
        return reverse('frogs:frog_list')

# Bulk entry for disposal of frogs
class FrogBulkDisposal(LoginRequiredMixin, generic.FormView):
    template_name = 'frogs/frog/frog_bulkdisposal.html'
    form_class = BulkFrogDisposalForm
    model = Frog
    raise_exception = True

    def form_valid(self, form):
        bulkfrogs = form.cleaned_data['frogs']
        print('BulkFrog: updating records=', len(bulkfrogs))
        # Generate Frog objects
        for pk in bulkfrogs:
            print('Updating frog:', pk)
            frog = pk #Frog.objects.get(pk=pk)
            frog.disposed = form.cleaned_data['disposed']
            frog.autoclave_date = form.cleaned_data['autoclave_date']
            frog.autoclave_run = form.cleaned_data['autoclave_run']
            frog.incineration_date = form.cleaned_data['incineration_date']
            print('Updated:Frog=', frog.frogid)
            frog.save()

        return super(FrogBulkDisposal, self).form_valid(form)


    def get_success_url(self):
        return reverse('frogs:frog_list')


########## OPERATIONS ############################################

# Filtered listing

class OperationFilterView(LoginRequiredMixin, FilteredSingleTableView):
    template_name = 'frogs/operation/operation_summary.html'
    model = Frog
    table_class = OperationTable
    filter_class = OperationFilter
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(OperationFilterView, self).get_context_data(**kwargs)
        ops = Operation.objects.all().values_list('frogid')
        qs = Frog.objects.filter(gender='female') \
            .filter(death_date__isnull=True) \
            .filter(id__in=ops).order_by('-frogid')
        table = OperationTable(qs, prefix='1-')
        RequestConfig(self.request, paginate={"per_page": 20}).configure(table)
        stats_table1 = OperationTable(qs.filter(species__name='X.borealis'), prefix='2-')
        RequestConfig(self.request, paginate={"per_page": 20}).configure(stats_table1)
        stats_table2 = OperationTable(qs.filter(species__name='X.laevis'), prefix='3-')
        RequestConfig(self.request, paginate={"per_page": 20}).configure(stats_table2)

        context['species'] = self.kwargs.get('species')
        context['summaries'] = table
        context['summaries_borealis'] = stats_table1
        context['summaries_laevis'] = stats_table2
        return context

## 1. Set frogid then 2. Increment opnum
## Limits: 6 operations and 6 mths apart - in Model
class OperationCreate(LoginRequiredMixin, generic.CreateView):
    model = Operation
    template_name = 'frogs/operation/operation_create.html'
    form_class = OperationForm
    raise_exception = True

    def get_success_url(self):
        frog = Frog.objects.filter(frogid=self.object.frogid)
        return reverse('frogs:frog_detail', args=[frog[0].id])


    def get_initial(self):
        fid = self.kwargs.get('frogid')
        frog = Frog.objects.get(pk=fid)
        ## next opnum
        opnum = 1 #default
        if (frog.operation_set.all()):
            opnum = frog.operation_set.count() + 1
        return {'frogid': frog, 'opnum': opnum}


class OperationUpdate(LoginRequiredMixin, generic.UpdateView):
    model = Operation
    form_class = OperationForm
    template_name = 'frogs/operation/operation_create.html'
    raise_exception = True

    def get_success_url(self):
        frogid = self.object.frogid
        frog = Frog.objects.filter(frogid=frogid)
        fid = frog[0].id
        return reverse('frogs:frog_detail', args=[fid])


class OperationDelete(LoginRequiredMixin, generic.DeleteView):
    model = Operation
    template_name = 'frogs/operation/operation_confirm_delete.html'
    raise_exception = True

    def get_success_url(self):
        frog = Frog.objects.filter(frogid=self.object.frogid)
        return reverse('frogs:frog_detail', args=[frog[0].id])

########## TRANSFERS ############################################
class TransferList(LoginRequiredMixin, generic.ListView):
    template_name = 'frogs/transfer/transfer_list.html'
    context_object_name = 'transfer_list'
    raise_exception = True

    def get_queryset(self):
        if (self.kwargs.get('operationid')):
            table = TransferTable(Transfer.objects.filter(operationid=self.kwargs.get('operationid')))
        else:
            table = TransferTable(Transfer.objects.order_by('-transfer_date'))
        RequestConfig(self.request, paginate={"per_page": 20}).configure(table)
        return table

class TransferFilterView(LoginRequiredMixin, FilteredSingleTableView):
    template_name = 'frogs/transfer/transfer_list.html'
    context_object_name = 'table'
    model = Transfer
    table_class = TransferTable
    filter_class = TransferFilter
    raise_exception = True

class TransferDetail(LoginRequiredMixin, generic.DetailView):
    model = Transfer
    template_name = 'frogs/transfer/transfer_detail.html'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(TransferDetail, self).get_context_data(**kwargs)
        return context

class TransferCreate(LoginRequiredMixin, generic.CreateView):
    model = Transfer
    template_name = 'frogs/transfer/transfer_create.html'
    form_class = TransferForm
    raise_exception = True

    def get_initial(self):
        opid = self.kwargs.get('operationid')
        op = Operation.objects.get(pk=opid)
        return {'operationid': op, 'volume': op.volume}

    def get_success_url(self):
        return reverse('frogs:transfer_detail', args=[self.object.id])

class TransferUpdate(LoginRequiredMixin, generic.UpdateView):
    model = Transfer
    form_class = TransferForm
    template_name = 'frogs/transfer/transfer_create.html'
    raise_exception = True

    def get_success_url(self):
        return reverse('frogs:transfer_detail', args=[self.object.id])

class TransferDelete(LoginRequiredMixin, generic.DeleteView):
    model = Transfer
    template_name = 'frogs/transfer/transfer_confirm_delete.html'
    success_url = reverse_lazy("frogs:transfer_list")
    raise_exception = True

########## EXPERIMENTS ############################################
class ExperimentList(LoginRequiredMixin, generic.ListView):
    template_name = 'frogs/experiment/experiment_list_transfer.html'
    context_object_name = 'expt_list'
    raise_exception = True

    def get_queryset(self):
        mylist = Experiment.objects.order_by('-transferid')
        if (self.kwargs.get('transferid')):
            mylist = mylist.filter(transferid=self.kwargs.get('transferid'))

        table = ExperimentTable(mylist)
        RequestConfig(self.request, paginate={"per_page": 20}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(ExperimentList, self).get_context_data(**kwargs)
        print('DEBUG:GET INITIAL')
        tid = self.kwargs.get('transferid')
        transfer = Transfer.objects.get(pk=tid)
        context['frogid']= transfer.operationid.frogid
        context['transfer_date']= transfer.transfer_date
        context['transfer_from_to']= transfer.transferapproval
        return context

class ExperimentFilterView(LoginRequiredMixin, FilteredSingleTableView):
    template_name = 'frogs/experiment/experiment_list.html'
    context_object_name = 'table'
    model = Experiment
    table_class = ExperimentTable
    filter_class = ExperimentFilter
    raise_exception = True


# Filtered listing
def experiment_listing(request):
    print('DEBUG:expt listing=', request)
    template_name = 'frogs/experiment/experiment_list.html'
    qs = Experiment.objects.order_by('-transferid')
    config = RequestConfig(request, paginate={"per_page": 20})
    table = ExperimentTable(qs, prefix='1-')
    table1 = ExperimentTable(qs.filter(expt_location__building='QBI'), prefix='2-')
    table2 = ExperimentTable(qs.filter(expt_location__building='IMB'), prefix='3-')
    config.configure(table)
    config.configure(table1)
    config.configure(table2)

    return render(request, template_name, {
        'expt_list' : table,
        'qbi_table': table1,
        'imb_table': table2
    })



class ExperimentDetail(LoginRequiredMixin, generic.DetailView):
    model = Experiment
    context_object_name = 'expt'
    template_name = 'frogs/experiment/experiment_detail.html'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(ExperimentDetail, self).get_context_data(**kwargs)
        return context

class ExperimentCreate(LoginRequiredMixin, generic.CreateView):
    model = Experiment
    template_name = 'frogs/experiment/experiment_create.html'
    form_class = ExperimentForm
    raise_exception = True

    def get_initial(self):
        opid = self.kwargs.get('transferid')
        op = Transfer.objects.get(pk=opid)
        location = op.transferapproval.tfr_to
        return {'transferid': op, 'expt_location': location}

    def get_success_url(self):
        return reverse('frogs:experiment_detail', args=[self.object.id])

class ExperimentUpdate(LoginRequiredMixin, generic.UpdateView):
    model = Experiment
    form_class = ExperimentForm
    template_name = 'frogs/experiment/experiment_create.html'
    raise_exception = True

    def get_success_url(self):
        return reverse('frogs:experiment_detail', args=[self.object.id])

class ExperimentDelete(LoginRequiredMixin, generic.DeleteView):
    model = Experiment
    success_url = reverse_lazy("frogs:experiment_list")
    raise_exception = True

class ExperimentDisposal(LoginRequiredMixin, generic.UpdateView):
    model = Experiment
    form_class = ExperimentDisposalForm
    context_object_name = 'experiment'
    template_name = 'frogs/experiment/experiment_create.html'
    raise_exception = True

    def get_success_url(self):
        return reverse('frogs:experiment_detail', args=[self.object.id])


class ExperimentAutoclave(LoginRequiredMixin, generic.UpdateView):
    model = Experiment
    form_class = ExperimentAutoclaveForm
    context_object_name = 'experiment'
    template_name = 'frogs/experiment/experiment_create.html'
    raise_exception = True

    def get_success_url(self):
        return reverse('frogs:experiment_detail', args=[self.object.id])

class DisposalList(LoginRequiredMixin, generic.ListView):
    template_name = 'frogs/experiment/disposal_list.html'
    context_object_name = 'expt_list'
    raise_exception = True

    def get_queryset(self):
        table = DisposalTable(Experiment.objects.order_by('disposal_date'))
        RequestConfig(self.request, paginate={"per_page": 20}).configure(table)
        return table

class BulkDisposal(LoginRequiredMixin, generic.FormView):
    template_name = 'frogs/experiment/bulkdisposal.html'
    form_class = BulkExptDisposalForm
    model = Experiment
    raise_exception = True

    def form_valid(self, form):
        print('DEBUG: form_valid', self.request.POST)
        bulklist = form.cleaned_data['expts']
        print('bulklist: updating records=', len(bulklist))
        # Generate Frog objects
        for pk in bulklist:
            print('Updating expt:', pk)
            expt = pk  # Frog.objects.get(pk=pk)
            expt.expt_disposed = form.cleaned_data['expt_disposed']
            expt.disposal_sentby = form.cleaned_data['disposal_sentby']
            expt.disposal_date = form.cleaned_data['disposal_date']
            expt.waste_type = form.cleaned_data['waste_type']
            expt.waste_content = form.cleaned_data['waste_content']
            expt.waste_qty = form.cleaned_data['waste_qty']
            expt.autoclave_indicator = form.cleaned_data['autoclave_indicator']
            expt.autoclave_complete = form.cleaned_data['autoclave_complete']
            print('Updated:Expt=', expt.id)
            expt.save()

        return super(BulkDisposal, self).form_valid(form)

    def get_queryset(self):
        mylist = Experiment.objects.order_by('-disposal_date')
        print('DEBUG: get queryset')
        if (self.kwargs.get('location')):
            location = self.kwargs.get('location')
            print('DEBUG: location=', location)
            if (location != 'all'):
                mylist = mylist.filter(expt_location__name=location)

        table = ExperimentTable(mylist)
        RequestConfig(self.request, paginate={"per_page": 20}).configure(table)
        return table

    def get_success_url(self):
        print('DEBUG: Get success URL')
        return reverse('frogs:experiment_list_location')

# FROG NOTES
class NotesList(LoginRequiredMixin, generic.ListView):
    template_name = 'frogs/notes/notes_list.html'
    context_object_name = 'notes_list'
    raise_exception = True

    def get_queryset(self):
        table = NotesTable(Notes.objects.order_by('-note_date'))
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        return table

class NotesDetail(LoginRequiredMixin, generic.DetailView):
    model = Notes
    context_object_name = 'notes'
    template_name = 'frogs/notes/notes_view.html'
    raise_exception = True

# class NotesFilterView(FilteredSingleTableView):
#     model = Notes
#     table_class = NotesTable
#     filter_class = NotesFilter

class NotesCreate(LoginRequiredMixin, generic.CreateView):
    model = Notes
    template_name = 'frogs/notes/notes_create.html'
    form_class = NotesForm
    success_url = reverse_lazy('frogs:notes_list')
    raise_exception = True

class NotesUpdate(LoginRequiredMixin, generic.UpdateView):
    model = Notes
    form_class = NotesForm
    template_name = 'frogs/notes/notes_create.html'
    success_url = reverse_lazy('frogs:notes_list')
    raise_exception = True

class NotesDelete(LoginRequiredMixin, generic.DeleteView):
    model = Notes
    success_url = reverse_lazy("frogs:notes_list")
    template_name = 'frogs/notes/notes_confirm_delete.html'
    raise_exception = True