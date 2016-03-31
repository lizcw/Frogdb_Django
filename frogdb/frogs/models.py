import datetime
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

SPECIES_LIST = ( ('x.borealis', 'X.borealis'), ('x.laevis', 'X.laevis'))
LOCATION_LIST= ( ('stored_aibn', 'Stored at AIBN Animal House'),
                 ('disposed_aibn', 'Disposed of at AIBN Animal House'),
                 ('disposed_oh', 'Disposed of at Otto Hirschfeld Animal House'))
DEATHTYPES = (('culled', 'Culled'), ('found', "Found dead"), ('alive', 'Not dead'))
QAP_LIST = (('AIBN','Q1629 (QC1)'), ('QBI', 'Q1881 (QC1)'), ('IMB L2', 'Q1695 (QC2)'))
WASTETYPES = (('solid', 'Solid'), ('liquid','Liquid'))
# Create your models here.


class Permit(models.Model):

    qen = models.CharField(_("QEN"), max_length=10)
    arrival_date = models.DateTimeField(_("Arrival date"))
    aqis = models.CharField(_("AQIS"), max_length=10)
    females = models.IntegerField(_("Females"), default=0)
    males = models.IntegerField(_("Males"), default=0)
    species = models.CharField(_("Species"), max_length=30, choices=SPECIES_LIST)
    supplier = models.CharField(_("Supplier"), max_length=30)
    country = models.CharField(_("Country"), max_length=30)

    def __str__(self):
        return self.qen

    def arrived_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.arrival_date <= now


class Frog(models.Model):
    qen = models.ForeignKey(Permit, on_delete=models.CASCADE)
    frogid = models.CharField(_("Frog ID"), max_length=30)
    tankid = models.IntegerField(_("Tank ID"), default=0)
    species = models.CharField(_("Species"), max_length=30, choices=SPECIES_LIST)
    current_location = models.CharField(_("Current Location"), max_length=80, choices=LOCATION_LIST)
    condition = models.CharField(_("Oocyte Health Condition"), max_length=100)
    remarks = models.TextField(_("General Remarks"))
    aec = models.CharField(_("AEC"), max_length=80)
    death = models.CharField(_("Type of Death"), max_length=10, choices=DEATHTYPES)
    death_date = models.DateField("Date of Death")
    death_initials = models.CharField(_("Initials"), max_length=10)
    disposed = models.BooleanField(_("Disposed"), default=False)
    autoclave_date = models.DateField("Autoclave Date")
    autoclave_run = models.IntegerField(_("Autoclave Run"), default=0)
    incineration_date = models.DateField(_("Incineration Date"))

    def __str__(self):
        return self.frogid

    def died_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.death_date <= now


class Operation(models.Model):
    frogid = models.ForeignKey(Frog, on_delete=models.CASCADE)
    opnum = models.IntegerField(_("Operation Number"), default=1)
    opdate = models.DateField("Operation Date")
    anesthetic = models.CharField(_("Anesthetic"), max_length=30)
    volume = models.SmallIntegerField("Volume (ml)")
    comments = models.TextField("Comments")
    initials = models.CharField(_("Operated by"), max_length=10)

    def __str__(self):
        return self.opnum


class TransferApproval(models.Model):
    tfr_from = models.CharField(_("Transfer from"), max_length=30, choices=QAP_LIST)
    tfr_to = models.CharField(_("Transfer to"), max_length=30, choices=QAP_LIST)
    sop = models.CharField(_("SOP details"), max_length=100)

    def __str__(self):
        return self.sop


class Transfer(models.Model):
    tfr_from = models.CharField(_("Transfer from"), max_length=30, choices=QAP_LIST)
    tfr_to = models.CharField(_("Transfer to"), max_length=30, choices=QAP_LIST)
    transferapproval = models.ForeignKey(TransferApproval)
    operationid = models.ForeignKey(Operation, on_delete=models.CASCADE)
    volume = models.SmallIntegerField("Volume carried (ml)")
    tfr_date = models.DateField("Transfer date")
    transporter = models.CharField(_("Transporter Name or Initials"), max_length=120)

    def __str__(self):
        return self.volume


class Experiment(models.Model):
    frogid = models.ForeignKey(Frog, on_delete=models.CASCADE)
    received = models.SmallIntegerField("Oocytes received (ml)")
    transferred = models.SmallIntegerField("Oocytes transferred (ml)")
    used = models.SmallIntegerField("Oocytes used (ml)")
    expt_from = models.DateField("Experiments from")
    expt_to = models.DateField("Experiments to")
    expt_location = models.CharField(_("Experiment location"), max_length=80)
    expt_disposed = models.BooleanField(_("Disposed"))
    disposal_sentby = models.CharField(_("Disposal sent by initials"), max_length=30)
    disposal_date = models.DateField("Disposal date")
    waste_type = models.CharField(_("Type of waste"), max_length=30, choices=WASTETYPES)
    waste_content = models.CharField(_("Waste content"), max_length=30)
    waste_qty = models.SmallIntegerField(_("Waste quantity"))
    autoclave_indicator = models.BooleanField("Autoclave indicator")
    autoclave_complete = models.BooleanField("Autoclave complete")

    def __str__(self):
        return self.used