from django.contrib import admin
from .models import TransferApproval,Qap

# Register your models here.

class TransferApprovalAdmin(admin.ModelAdmin):
    pass

admin.site.register(TransferApproval, TransferApprovalAdmin)
admin.site.register(Qap)