from django.contrib import admin
from . import models

class PdfReader(admin.ModelAdmin):
    pass

admin.site.register(models.Complaint, PdfReader)
