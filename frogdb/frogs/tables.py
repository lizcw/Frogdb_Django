import django_tables2 as tables
from django_tables2.utils import A
from .models import Transfer,Experiment,Frog,Permit

class ExperimentTable(tables.Table):
    #selection = tables.CheckBoxColumn(accessor="pk", orderable=False)
    id = tables.LinkColumn('frogs:experiment_detail', text='...', args=[A('pk')], verbose_name='')
    transfer_date = tables.DateColumn(verbose_name='Date Received', accessor=A('transferid.transfer_date'), format='d-M-Y')
    frogid = tables.Column(verbose_name='Frog ID', accessor=A('transferid.operationid.frogid.frogid'))
    species = tables.Column(verbose_name = 'Species', accessor = A('transferid.operationid.frogid.species'))
    class Meta:
        model = Experiment
        attrs = {"class": "ui-responsive table table-hover"}
        fields = ['transfer_date','frogid','species','expt_location','received','transferred','used','expt_from','expt_to','expt_disposed','id']


class DisposalTable(tables.Table):
    id = tables.LinkColumn('frogs:experiment_detail', text='...', args=[A('pk')], verbose_name='')
    frogid = tables.Column(verbose_name='Frog ID', accessor=A('transferid.operationid.frogid.frogid'))
    qen = tables.Column(verbose_name='QEN', accessor=A('transferid.operationid.frogid.qen'))
    class Meta:
        model = Experiment
        attrs = {"class": "ui-responsive table table-hover"}
        fields = ['expt_location','qen','frogid','waste_type','waste_content','waste_qty','autoclave_indicator','autoclave_complete','disposal_date','disposal_sentby','id']


class TransferTable(tables.Table):
    id = tables.LinkColumn('frogs:transfer_detail', text='...', args=[A('pk')], verbose_name='')
    frogid = tables.LinkColumn('frogs:frog_detail', accessor=A('operationid.frogid.frogid'), args=[A('operationid.frogid.pk')],verbose_name='Frog ID')
    species = tables.Column(verbose_name='Species', accessor=A('operationid.frogid.species'))
    qen = tables.Column(verbose_name='QEN', accessor=A('operationid.frogid.qen'))
    sop = tables.Column(verbose_name='Transfer Approval', accessor=A('transferapproval.sop'))

    class Meta:
        model = Transfer
        attrs = {"class": "ui-responsive table table-hover"}
        fields = ['frogid','species','qen','volume','transporter','method','transfer_date','transferapproval', 'sop','id']

class FrogTable(tables.Table):
    frogid = tables.LinkColumn('frogs:frog_detail', args=[A('pk')])
    class Meta:
        model = Frog
        attrs = {"class": "ui-responsive table table-hover"}
        fields = ['frogid','tankid','gender','species','current_location','condition','remarks','qen','aec','death']
        order_by_field = 'frogid'
        sortable = True

class PermitTable(tables.Table):
    id = tables.LinkColumn('frogs:permit_detail', text='...', args=[A('pk')], verbose_name='' )
    class Meta:
        model = Permit
        attrs = {"class": "ui-responsive table table-hover"}
        fields = ['aqis','qen','females','males', 'arrival_date','species','supplier','country','id']

        order_by_field = 'arrival_date'
        sortable = True

class OperationTable(tables.Table):
    frogid = tables.LinkColumn('frogs:frog_detail', accessor=A('frogid'), args=[A('pk')],verbose_name='Frog ID')
    num_operations = tables.Column(verbose_name="Num Ops", accessor=A('num_operations'), orderable=False)
    last_operation = tables.DateColumn(verbose_name="Last Op", format='d-M-Y', accessor=A('last_operation'), orderable=False)
    next_operation = tables.DateColumn(verbose_name="Next Op not before", format='d-M-Y', accessor=A('next_operation'), orderable=False)

    class Meta:
        model = Frog
        attrs = {"class": "ui-responsive table table-hover"}
        fields = ['frogid', 'num_operations', 'last_operation', 'next_operation', 'condition', 'remarks', 'tankid']

        order_by_field = '-next_operation'
        sortable = True
