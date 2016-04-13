import datetime
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError

SPECIES_LIST = ( ('x.borealis', 'X.borealis'), ('x.laevis', 'X.laevis'))
LOCATION_LIST= ( ('stored_aibn', 'Stored at AIBN Animal House'),
                 ('disposed_aibn', 'Disposed of at AIBN Animal House'),
                 ('disposed_oh', 'Disposed of at Otto Hirschfeld Animal House'))
DEATHTYPES = (('culled', 'Culled'), ('found', "Found dead"), ('alive', 'Not dead'))
#QAP_LIST = (('AIBN','Q1629 (QC1)'), ('QBI', 'Q1881 (QC1)'), ('IMB L2', 'Q1695 (QC2)'))
WASTETYPES = (('solid', 'Solid'), ('liquid','Liquid'), ('solid_liquid','Solid/Liquid'))
SUPPLIER_LIST=(('nasco','NASCO'),('xenopus','Xenopus One'), ('uq','UQ'))
COUNTRY_LIST=(('usa','USA'),('australia','Australia'))
GENDERS=(('female','Female'),('male','Male'))
IMAGETYPES=(('dorsal','Dorsal'),('ventral','Ventral'))
# DB list models


class Qap(models.Model):
    qap = models.CharField(_("QAP"), max_length=80, primary_key=True)
    building = models.CharField(_("Building"), max_length=60, null=False)

    def __str__(self):
        return self.building


# DB models
class Permit(models.Model):
    aqis = models.CharField(_("AQIS"), max_length=20)
    qen = models.CharField(_("QEN"), max_length=20, unique=True)
    females = models.IntegerField(_("Females"), default=0)
    males = models.IntegerField(_("Males"), default=0)
    arrival_date = models.DateField(_("Arrival date"))
    species = models.CharField(_("Species"), max_length=30, choices=SPECIES_LIST)
    supplier = models.CharField(_("Supplier"), max_length=30, choices=SUPPLIER_LIST)
    country = models.CharField(_("Country"), max_length=30, choices=COUNTRY_LIST)

    def __str__(self):
        return self.qen

    def get_absolute_url(self):
        return reverse('permit_detail', args=[str(self.pk)])

    def arrived_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.arrival_date <= now


class Frog(models.Model):

    frogid = models.CharField(_("Frog ID"), max_length=30, unique=True)
    tankid = models.IntegerField(_("Tank ID"), default=0)
    gender = models.CharField(_("Gender"), max_length=10, default="female", choices=GENDERS)
    species = models.CharField(_("Species"), max_length=30, choices=SPECIES_LIST)
    current_location = models.CharField(_("Current Location"), max_length=80, choices=LOCATION_LIST)
    condition = models.CharField(_("Oocyte Health Condition"), max_length=100, null=True, blank=True)
    remarks = models.TextField(_("General Remarks"),null=True, blank=True)
    qen = models.ForeignKey(Permit, verbose_name="QEN", on_delete=models.CASCADE)
    aec = models.CharField(_("AEC"), max_length=80,null=True, blank=True)
    death = models.CharField(_("Death"), max_length=10, null=True, blank=True, choices=DEATHTYPES)
    death_date = models.DateField("Date of Death", null=True, blank=True)
    death_initials = models.CharField(_("Initials"), max_length=10, null=True, blank=True)
    disposed = models.BooleanField(_("Disposed"), default=False)
    autoclave_date = models.DateField("Autoclave Date", null=True, blank=True)
    autoclave_run = models.IntegerField(_("Autoclave Run"), default=0, null=True, blank=True)
    incineration_date = models.DateField(_("Incineration Date"), null=True, blank=True)

    def __str__(self):
        return self.frogid

    def get_absolute_url(self):
        return reverse('frog_detail', args=[str(self.pk)])

    def died_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.death_date <= now

    # derived fields
    def get_operations(self):
        return self.operation_set.order_by('opnum')

    def last_operation(self):
        totalops = self.operation_set.count()
        lastop = None
        if (totalops > 0):
            lastop = self.operation_set.order_by('opnum')[totalops - 1]
            return lastop.opdate

    def num_operations(self):
         return self.operation_set.count()

    def next_operation(self):
        lastop = self.last_operation()
        #add 6 months
        nextop = lastop + datetime.timedelta(6 * 365 / 12)
        return nextop

    def dorsalimage(self):
        return self.get_image('dorsal')

    def ventralimage(self):
        return self.get_image('ventral')

    def get_image(self,type):
        img = None
        if (self.frogattachment_set.count() > 0):
            imgs = self.frogattachment_set.filter(imagetype=type)
            if imgs.count() > 0:
                img = imgs[0]
        return img

class FrogAttachment(models.Model):
    frogid = models.ForeignKey(Frog, on_delete=models.CASCADE)
    imgfile = models.ImageField(verbose_name="Image")
    imagetype = models.CharField(_("Type"), max_length=10, choices=IMAGETYPES)
    description = models.CharField(_("Description"), max_length=200, null=True, blank=True)

    def __str__(self):
        return self.imagetype

    def clean(self):
        #Check if replacing an image or new
        #Get frog - get images - get type
        frog = Frog.objects.get(pk=self.frogid.pk)
        dorsal = frog.dorsalimage()
        ventral = frog.ventralimage()
        if dorsal is not None and self.imagetype =='dorsal':
            dorsal.delete()
        elif ventral is not None and self.imagetype =='ventral':
            ventral.delete()

            #raise ValidationError("Can only transfer maximum %d ml" % max)


class Operation(models.Model):
    frogid = models.ForeignKey(Frog, on_delete=models.CASCADE)
    opnum = models.IntegerField(_("Operation Number"), default=1)
    opdate = models.DateField("Operation Date")
    anesthetic = models.CharField(_("Anesthetic"), max_length=30)
    volume = models.SmallIntegerField("Volume (ml)")
    comments = models.TextField("Comments")
    initials = models.CharField(_("Operated by"), max_length=10)

    def __str__(self):
        opref = "Frog %s Operation %d" % (self.frogid, self.opnum)
        return opref

    def clean(self):
        max = self.maxops()
        if self.opnum > max:
            raise ValidationError("Can only create %d operations per frog" % max)

    #max ops per frog - ?configurable
    def maxops(self):
        return int(6)


class TransferApproval(models.Model):
    tfr_from = models.ForeignKey(Qap, verbose_name="Transfer from", related_name="tfr_from")
    tfr_to = models.ForeignKey(Qap, verbose_name="Transfer to", related_name="tfr_to")
    sop = models.CharField(_("SOP details"), max_length=100)

    def __str__(self):
        return self.get_fromto()

    # Return string with from-to
    def get_fromto(self):
        fromto = "%s to %s" % (self.tfr_from.building, self.tfr_to.building)
        return fromto

    def get_sop(self):
        return self.sop


class Transfer(models.Model):
    transferapproval = models.ForeignKey(TransferApproval, verbose_name="Transfer from/to")
    operationid = models.ForeignKey(Operation, verbose_name="Operation", on_delete=models.CASCADE)
    volume = models.SmallIntegerField("Volume carried (ml)")
    transfer_date = models.DateField("Transfer date")
    transporter = models.CharField(_("Transporter Name or Initials"), max_length=120)
    method = models.CharField(_("Method"), max_length=120)

    def __str__(self):
        return str(self.get_verbose())

    def maxvol(self):
        return self.operationid.volume

    # Return string with from-to
    def get_verbose(self):
        verbose = "Frog %s: from operation %d on %s (total %d ml)" % (self.operationid.frogid, self.operationid.opnum, self.operationid.opdate, self.operationid.volume)
        return verbose

    def clean(self):
        max = self.maxvol()
        if self.volume > max:
            raise ValidationError("Can only transfer maximum %d ml" % max)

class Experiment(models.Model):
    transferid = models.ForeignKey(Transfer, on_delete=models.CASCADE, verbose_name="Oocyte source")
    received = models.SmallIntegerField("Oocytes received (ml)")
    transferred = models.SmallIntegerField("Oocytes transferred (ml)")
    used = models.SmallIntegerField("Oocytes used (ml)")
    expt_from = models.DateField("Experiments from")
    expt_to = models.DateField("Experiments to")
    expt_location = models.ForeignKey(Qap, verbose_name="Experiment Location", related_name="expt_location")
    expt_disposed = models.BooleanField(_("Disposed"), default=False)
    disposal_sentby = models.CharField(_("Disposal sent by initials"), max_length=30, blank=True,null=True)
    disposal_date = models.DateField("Disposal date", blank=True,null=True)
    waste_type = models.CharField(_("Type of waste"), max_length=30, choices=WASTETYPES, blank=True,null=True)
    waste_content = models.CharField(_("Waste content"), max_length=30, blank=True,null=True)
    waste_qty = models.SmallIntegerField(_("Waste quantity"), blank=True, null=True)
    autoclave_indicator = models.BooleanField("Autoclave indicator", default=False)
    autoclave_complete = models.BooleanField("Autoclave complete", default=False)

    def __str__(self):
        return self.used


class Supplier(models.Model):
    name = models.CharField(_("Name"), max_length=100)

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(_("Name"), max_length=60)
    code = models.CharField(_("Code"), max_length=5)

    def __str__(self):
        return self.name


class Species(models.Model):
    name = models.CharField(_("Species"), max_length=100)

    def __str__(self):
        return self.name


class Imagetype(models.Model):
    name = models.CharField(_("Image Type"), max_length=100)

    def __str__(self):
        return self.name


class Wastetype(models.Model):
    name = models.CharField(_("Waste Type"), max_length=100)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(_("Current Location"), max_length=100)
    brief = models.CharField(_("Abbreviation"), max_length=20)

    def __str__(self):
        return self.name


class Deathtype(models.Model):
    name = models.CharField(_("Death Type"), max_length=100)

    def __str__(self):
        return self.name