from django.contrib import admin
from .models import TransferApproval, Qap, Country, Supplier, Species, Imagetype, Location, Wastetype, Deathtype

# Register your models here.
class QapInline(admin.TabularInline):
    model = Qap

class TransferApprovalAdmin(admin.ModelAdmin):
    #inlines = [QapInline,]

    pass


admin.site.register(TransferApproval, TransferApprovalAdmin)
admin.site.register(Qap)
admin.site.register(Country)
admin.site.register(Supplier)
admin.site.register(Species)
admin.site.register(Imagetype)
admin.site.register(Location)
admin.site.register(Wastetype)
admin.site.register(Deathtype)
