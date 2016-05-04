from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.urlresolvers import reverse_lazy, reverse, clear_url_caches
from django.views import generic
from django.utils import timezone
from django.template import Context, Template
from django_tables2 import RequestConfig

from .models import Permit, Frog, Operation, Transfer, Experiment, FrogAttachment
from .forms import PermitForm, FrogForm, FrogDeathForm, FrogDisposalForm, OperationForm, TransferForm, ExperimentForm, FrogAttachmentForm, BulkFrogForm, BulkFrogDeleteForm, ExperimentDisposalForm, ExperimentAutoclaveForm, BulkFrogDisposalForm
from .tables  import ExperimentTable,PermitTable,FrogTable,TransferTable, OperationTable,DisposalTable

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
    return render(request, "frogs/index.html", {'errors': message, 'user': user})

#### PERMITS/SHIPMENTS
class PermitList(generic.ListView):
    template_name = 'frogs/shipment/shipment_list.html'
    context_object_name = 'shipment_list'

    def get_queryset(self):
        table = PermitTable(Permit.objects.order_by('-arrival_date'))
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        return table

class PermitDetail(generic.DetailView):
    model = Permit
    context_object_name = 'shipment'
    template_name = 'frogs/shipment/shipment_view.html'


class PermitCreate(generic.CreateView):
    model = Permit
    template_name = 'frogs/shipment/shipment_create.html'
    form_class = PermitForm
    success_url = reverse_lazy('frogs:permit_list')

class PermitUpdate(generic.UpdateView):
    model = Permit
    form_class = PermitForm
    template_name = 'frogs/shipment/shipment_create.html'
    success_url = reverse_lazy('frogs:permit_list')

class PermitDelete(generic.DeleteView):
    model = Permit
    success_url = reverse_lazy("frogs:permit_list")


########## FROGS ############################################
class FrogList(generic.ListView):
    template_name = 'frogs/frog/frog_list.html'
    context_object_name = 'frogs'

    def get_queryset(self):
        print('DEBUG:kwargs', self.kwargs)
        if (self.kwargs.get('shipmentid')):
            sid = self.kwargs.get('shipmentid')
            shipment = Permit.objects.get(pk=sid)
            table = FrogTable(Frog.objects.filter(qen=shipment).order_by('-frogid'))
        else:
            table = FrogTable(Frog.objects.order_by('-frogid'))
        RequestConfig(self.request, paginate={"per_page": 20}).configure(table)
        return table

class FrogDetail(generic.DetailView):
    model = Frog
    context_object_name = 'frog'
    template_name = 'frogs/frog/frog_view.html'

class FrogCreate(generic.CreateView):
    model = Frog
    template_name = 'frogs/frog/frog_create.html'
    form_class = FrogForm

    def form_valid(self, form):
        try:
            return super(FrogCreate, self).form_valid(form)
        except IntegrityError as e:
            form.add_error('frogid', 'Database Error: Unable to create Frog - see Administrator')
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('frogs:frog_detail', args=[self.object.id])

class FrogUpdate(generic.UpdateView):
    model = Frog
    form_class = FrogForm
    template_name = 'frogs/frog/frog_create.html'

    def get_success_url(self):
        return reverse('frogs:frog_detail', args=[self.object.id])

class FrogDelete(generic.DeleteView):
    model = Frog
    success_url = reverse_lazy("frogs:frog_list")

class FrogDeath(generic.UpdateView):
    model = Frog
    form_class = FrogDeathForm
    context_object_name = 'frog'
    template_name = 'frogs/frog/frog_death.html'

    def get_success_url(self):
        return reverse('frogs:frog_detail', args=[self.object.id])

class FrogDisposal(generic.UpdateView):
    model = Frog
    form_class = FrogDisposalForm
    context_object_name = 'frog'
    template_name = 'frogs/frog/frog_disposal.html'

    def get_success_url(self):
        return reverse('frogs:frog_detail', args=[self.object.id])

class FrogAttachment(generic.CreateView):
    model = FrogAttachment
    form_class = FrogAttachmentForm
    context_object_name = 'frog'
    template_name = 'frogs/frog/frog_upload.html'


    def get_success_url(self):
        return reverse('frogs:frog_detail', args=[self.object.frogid.pk])

    def get_initial(self):
        fid = self.kwargs.get('frogid')
        frog = Frog.objects.get(pk=fid)
        return {'frogid': frog}

class FrogBulkCreate(generic.FormView):
    model = Frog
    form_class = BulkFrogForm
    template_name = "frogs/frog/bulkfrog_create.html"
    success_url = reverse_lazy("frogs:frog_list")

    def form_valid(self, form):
        #Get shipment: number female/male
        fid = self.kwargs.get('shipmentid')
        shipment = Permit.objects.get(pk=fid)
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
        return reverse('frogs:frog_list')


#Delete frogs from a shipment
class FrogBulkDelete(generic.FormView):
    template_name = 'frogs/frog/bulkfrog_confirm_delete.html'
    form_class=BulkFrogDeleteForm


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

#Save fields
class FrogBulkDisposal(generic.FormView):
    template_name = 'frogs/frog/frog_bulkdisposal.html'
    form_class = BulkFrogDisposalForm
    model = Frog
    frogids = []
   # success_url = 'frogs/frog/frog_bulkdisposal.html'

    def form_valid(self, form):
        if self.request.POST.getlist('selectfrog'):
            print('DEBUG: FIRST FORM')
        else:
            print('DEBUG: form_valid', self.request.POST)
            print('BulkFrog: updating records=', len(self.frogids))
            # Generate Frog objects
            for pk in self.frogids:
                print('Updating frog:', pk)
                frog = Frog.objects.get(pk=pk)
                frog.disposed = form.cleaned_data['disposed']
                frog.autoclave_date = form.cleaned_data['autoclave_date']
                frog.autoclave_run = form.cleaned_data['autoclave_run']
                frog.incineration_date = form.cleaned_data['incineration_date']
                print('Updated:Frog=', frog.frogid)
                frog.update()

        return super(FrogBulkDisposal, self).form_valid(form)

    def get_initial(self):
        self.frogids = self.request.POST.getlist('selectfrog')
        print('DEBUG: Get initial=', self.frogids)
        return {'frogids': self.frogids}

    def get_queryset(self):
        print('DEBUG: Get queryset=', self.frogids)

        return Frog.objects.in_bulk(self.frogids)

    def get_success_url(self):
        print('DEBUG: Get success URL')
        return reverse('frogs:frog_list')


########## OPERATIONS ############################################
class OperationSummary(generic.ListView):
    template_name = 'frogs/operation/operation_summary.html'
    context_object_name = 'summaries'


    def get_queryset(self):
        #Get Operations first
        ops = Operation.objects.all().values_list('frogid')
        self.species = self.kwargs.get('species')
        print('DEBUG:OPS BY SPECIES=', self.species)
        #Get queryset
        qs = Frog.objects.all()
        qs = qs.filter(id__in=ops).order_by('-frogid')
        if (self.species is not None and self.species != 'all'):
            qs = qs.filter(species=self.species.lower())
            print('DEBUG:BY species=', qs.count())
        table = OperationTable(qs)
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        return table

    def get_success_url(self):
        return reverse('frogs:operation_summary', args=[self.species])



## 1. Set frogid then 2. Increment opnum
## Limits: 6 operations and 6 mths apart - in Model
class OperationCreate(generic.CreateView):
    model = Operation
    template_name = 'frogs/operation/operation_create.html'
    form_class = OperationForm

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


class OperationUpdate(generic.UpdateView):
    model = Operation
    form_class = OperationForm
    template_name = 'frogs/operation/operation_create.html'

    def get_success_url(self):
        frogid = self.object.frogid
        frog = Frog.objects.filter(frogid=frogid)
        fid = frog[0].id
        return reverse('frogs:frog_detail', args=[fid])


class OperationDelete(generic.DeleteView):
    model = Operation
    template_name = 'frogs/operation/operation_confirm_delete.html'

    def get_success_url(self):
        frog = Frog.objects.filter(frogid=self.object.frogid)
        return reverse('frogs:frog_detail', args=[frog[0].id])

########## TRANSFERS ############################################
class TransferList(generic.ListView):
    template_name = 'frogs/transfer/transfer_list.html'
    context_object_name = 'transfer_list'

    def get_queryset(self):
        if (self.kwargs.get('operationid')):
            table = TransferTable(Transfer.objects.filter(operationid=self.kwargs.get('operationid')))
        else:
            table = TransferTable(Transfer.objects.order_by('-transfer_date'))
        RequestConfig(self.request, paginate={"per_page": 20}).configure(table)
        return table

class TransferDetail(generic.DetailView):
    model = Transfer
    template_name = 'frogs/transfer/transfer_detail.html'

    def get_context_data(self, **kwargs):
        context = super(TransferDetail, self).get_context_data(**kwargs)
        return context

class TransferCreate(generic.CreateView):
    model = Transfer
    template_name = 'frogs/transfer/transfer_create.html'
    form_class = TransferForm

    def get_initial(self):
        opid = self.kwargs.get('operationid')
        op = Operation.objects.get(pk=opid)
        return {'operationid': op}

    def get_success_url(self):
        return reverse('frogs:transfer_detail', args=[self.object.id])

class TransferUpdate(generic.UpdateView):
    model = Transfer
    form_class = TransferForm
    template_name = 'frogs/transfer/transfer_create.html'

    def get_success_url(self):
        return reverse('frogs:transfer_detail', args=[self.object.id])

class TransferDelete(generic.DeleteView):
    model = Transfer
    template_name = 'frogs/transfer/transfer_confirm_delete.html'
    success_url = reverse_lazy("frogs:transfer_list")

########## EXPERIMENTS ############################################
class ExperimentList(generic.ListView):
    template_name = 'frogs/experiment/experiment_list.html'
    context_object_name = 'expt_list'


    def get_queryset(self):
        table = None
        if (self.kwargs.get('transferid')):
            table = ExperimentTable(Experiment.objects.filter(transferid=self.kwargs.get('transferid')))
        else:
            table = ExperimentTable(Experiment.objects.order_by('-transferid'))
        RequestConfig(self.request, paginate={"per_page": 20}).configure(table)
        return table

class ExperimentDetail(generic.DetailView):
    model = Experiment
    context_object_name = 'expt'
    template_name = 'frogs/experiment/experiment_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ExperimentDetail, self).get_context_data(**kwargs)
        return context

class ExperimentCreate(generic.CreateView):
    model = Experiment
    template_name = 'frogs/experiment/experiment_create.html'
    form_class = ExperimentForm

    def get_initial(self):
        opid = self.kwargs.get('transferid')
        op = Transfer.objects.get(pk=opid)
        location = op.transferapproval.tfr_to
        return {'transferid': op, 'expt_location': location}

    def get_success_url(self):
        return reverse('frogs:experiment_detail', args=[self.object.id])

class ExperimentUpdate(generic.UpdateView):
    model = Experiment
    form_class = ExperimentForm
    template_name = 'frogs/experiment/experiment_create.html'

    def get_success_url(self):
        return reverse('frogs:experiment_detail', args=[self.object.id])

class ExperimentDelete(generic.DeleteView):
    model = Experiment
    success_url = reverse_lazy("frogs:experiment_list")

class ExperimentDisposal(generic.UpdateView):
    model = Experiment
    form_class = ExperimentDisposalForm
    context_object_name = 'experiment'
    template_name = 'frogs/experiment/experiment_create.html'

    def get_success_url(self):
        return reverse('frogs:experiment_detail', args=[self.object.id])


class ExperimentAutoclave(generic.UpdateView):
    model = Experiment
    form_class = ExperimentAutoclaveForm
    context_object_name = 'experiment'
    template_name = 'frogs/experiment/experiment_create.html'

    def get_success_url(self):
        return reverse('frogs:experiment_detail', args=[self.object.id])

class DisposalList(generic.ListView):
    template_name = 'frogs/experiment/disposal_list.html'
    context_object_name = 'expt_list'

    def get_queryset(self):
        table = DisposalTable(Experiment.objects.filter(expt_disposed=False).order_by('-expt_to'))
        RequestConfig(self.request, paginate={"per_page": 20}).configure(table)
        return table

# class BatchExptDisposal(generic.FormView):
#     model = Experiment
#     form_class = BatchExptDisposalForm
#     template_name="frogs/batchdisposal_create.html"
#
#     def form_valid(self, form):
#         form.instance.created_by = self.request.user
#         return super(BatchExptDisposal, self).form_valid(form)
#
#     def get_queryset(self):
#         qs = Experiment.objects.filter(disposed=False)
#         qs = qs.select_for_update()
#         return qs
