from django.db import models

# Create your models here.
class Complaint(models.Model):
    # Core fields for the complaint
    report_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    priority = models.CharField(max_length=50, blank=True, null=True)
    assigned_to = models.CharField(max_length=255, blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True) # Use DateTimeField for dates/times
    reported_by = models.CharField(max_length=255, blank=True, null=True)
    reported_on = models.DateTimeField(blank=True, null=True) # Assuming 'Reported on' is a datetime
    occurred_at = models.DateTimeField(blank=True, null=True) # Assuming 'Occurred at' is a datetime
    location = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    closed_date = models.DateTimeField(blank=True, null=True)

    # Multi-line text fields (using TextField for potentially long strings)
    details = models.TextField(blank=True, null=True)
    action_taken = models.TextField(blank=True, null=True)
    resolution = models.TextField(blank=True, null=True)

    # Optional: Automatically set creation/update timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Complaint {self.report_id} - {self.category}"

    class Meta:
        verbose_name = "Complaint Record"
        verbose_name_plural = "Complaint Records"