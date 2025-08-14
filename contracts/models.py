from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Contract(models.Model):
    class ContractStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        IN_REVIEW = 'IN_REVIEW', 'In Review'
        NEGOTIATION = 'NEGOTIATION', 'Negotiation'
        SIGNED = 'SIGNED', 'Signed'
        ACTIVE = 'ACTIVE', 'Active'
        EXPIRED = 'EXPIRED', 'Expired'
        TERMINATED = 'TERMINATED', 'Terminated'

    class ContractType(models.TextChoices):
        NDA = 'NDA', 'Non-Disclosure Agreement'
        MSA = 'MSA', 'Master Service Agreement'
        SOW = 'SOW', 'Statement of Work'
        SLA = 'SLA', 'Service Level Agreement'
        EMPLOYMENT = 'EMPLOYMENT', 'Employment Agreement'
        OTHER = 'OTHER', 'Other'

    class Jurisdiction(models.TextChoices):
        US = 'US', 'United States'
        UK = 'UK', 'United Kingdom'
        EU = 'EU', 'European Union'
        APAC = 'APAC', 'Asia-Pacific'
        OTHER = 'OTHER', 'Other'

    title = models.CharField(max_length=200)
    counterparty = models.CharField(max_length=200)
    contract_type = models.CharField(max_length=20, choices=ContractType.choices, default=ContractType.OTHER)
    jurisdiction = models.CharField(max_length=20, choices=Jurisdiction.choices, default=Jurisdiction.OTHER)
    value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=ContractStatus.choices, default=ContractStatus.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    milestone_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_contracts')
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title


class Note(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='notes')
    text = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='contract_notes')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Note by {self.created_by} on {self.contract.title} at {self.timestamp.strftime("%Y-%m-%d %H:%M")}'
