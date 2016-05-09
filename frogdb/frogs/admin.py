from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import SiteConfiguration
from .models import TransferApproval, Qap, Country, Supplier, Species, Imagetype, Location, Wastetype, Deathtype
from .forms import SiteConfigurationForm
# Register your models here.
class QapInline(admin.TabularInline):
    model = Qap

class TransferApprovalAdmin(admin.ModelAdmin):
    #inlines = [QapInline,]

    pass

class SiteConfigurationAdmin(admin.ModelAdmin):
    form = SiteConfigurationForm


admin.site.register(SiteConfiguration, SiteConfigurationAdmin)
#admin.site.register(SingletonModelAdmin)
admin.site.register(TransferApproval, TransferApprovalAdmin)
admin.site.register(Qap)
admin.site.register(Country)
admin.site.register(Supplier)
admin.site.register(Species)
admin.site.register(Imagetype)
admin.site.register(Location)
admin.site.register(Wastetype)
admin.site.register(Deathtype)
