from django.contrib import admin
from .models import File, Invoice

admin.site.register(File)

class InvoiceAdmin(admin.ModelAdmin):
    model = Invoice
    list_display = ['num', 'dt']

admin.site.register(Invoice, InvoiceAdmin)