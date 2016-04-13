from django.contrib import admin
from .models import TransferApproval, Qap, Country, Supplier, Species, Imagetype, Location, Wastetype, Deathtype

# Register your models here.
class QapInline(admin.TabularInline):
    model = Qap

class TransferApprovalAdmin(admin.ModelAdmin):
    #inlines = [QapInline,]

    pass
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass

class SupplierAdmin(admin.ModelAdmin):
    fields = ['name']
    pass

class SpeciesAdmin(admin.ModelAdmin):
    pass

class ImagetypeAdmin(admin.ModelAdmin):
    pass

class LocationAdmin(admin.ModelAdmin):
    pass

class WastetypeAdmin(admin.ModelAdmin):
    pass

class DeathtypeAdmin(admin.ModelAdmin):
    pass

admin.site.register(TransferApproval, TransferApprovalAdmin)
admin.site.register(Qap)
#admin.site.register(Country, CountryAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Species, SpeciesAdmin)
admin.site.register(Imagetype, ImagetypeAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Wastetype, WastetypeAdmin)
admin.site.register(Deathtype, DeathtypeAdmin)
