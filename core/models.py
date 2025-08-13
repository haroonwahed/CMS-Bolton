from django.db import models
from django.contrib.auth.models import User

class Contract(models.Model):
    STATUS_CHOICES = [
        ('DR', 'Draft'),
        ('IR', 'In Review'),
        ('AC', 'Active'),
        ('EX', 'Expired'),
        ('TE', 'Terminated'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    counterparty = models.CharField(max_length=255)
    contract_type = models.CharField(max_length=100)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='DR')
    execution_date = models.DateField(null=True, blank=True)
    effective_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    contract_document = models.FileField(upload_to='contracts/')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_contracts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
