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
        INTERNAL_REVIEW = 'INTERNAL_REVIEW', 'Internal Review'
        EXTERNAL_REVIEW = 'EXTERNAL_REVIEW', 'External Review'
        NEGOTIATION = 'NEGOTIATION', 'Negotiation'
        SIGNATURE = 'SIGNATURE', 'Signature'
        EXECUTION = 'EXECUTION', 'Execution'
        RENEWAL_TERMINATION = 'RENEWAL_TERMINATION', 'Renewal/Termination'

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


class WorkflowStep(models.Model):
    class StepType(models.TextChoices):
        INTERNAL_REVIEW = 'INTERNAL_REVIEW', 'Internal Review'
        EXTERNAL_REVIEW = 'EXTERNAL_REVIEW', 'External Review'
        NEGOTIATION = 'NEGOTIATION', 'Negotiation'
        SIGNATURE = 'SIGNATURE', 'Signature'
        EXECUTION = 'EXECUTION', 'Execution'

    class StepStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        SKIPPED = 'SKIPPED', 'Skipped'

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='workflow_steps')
    step_type = models.CharField(max_length=20, choices=StepType.choices)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='workflow_tasks')
    status = models.CharField(max_length=20, choices=StepStatus.choices, default=StepStatus.PENDING)
    notes = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.get_step_type_display()} for {self.contract.title}'


class ContractVersion(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    content_snapshot = models.TextField()
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_versions')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('contract', 'version_number')
        ordering = ['-version_number']

    def __str__(self):
        return f'{self.contract.title} - Version {self.version_number}'


class NegotiationThread(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='negotiation_threads')
    round_number = models.PositiveIntegerField()
    internal_note = models.TextField(blank=True)
    external_note = models.TextField(blank=True)
    attachment = models.FileField(upload_to='negotiation_attachments/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='negotiation_posts')

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'Negotiation Round {self.round_number} for {self.contract.title}'


class TrademarkRequest(models.Model):
    class TrademarkStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        FILED = 'FILED', 'Filed'
        IN_REVIEW = 'IN_REVIEW', 'In Review'
        REGISTERED = 'REGISTERED', 'Registered'
        REJECTED = 'REJECTED', 'Rejected'
        ABANDONED = 'ABANDONED', 'Abandoned'

    region = models.CharField(max_length=100)
    class_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=TrademarkStatus.choices, default=TrademarkStatus.PENDING)
    request_date = models.DateField(auto_now_add=True)
    documents = models.FileField(upload_to='trademark_documents/', blank=True, null=True)
    renewal_deadline = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='trademark_requests')

    def __str__(self):
        return f'Trademark Request for {self.region} - Class {self.class_number}'


class LegalTask(models.Model):
    class TaskStatus(models.TextChoices):
        TODO = 'TODO', 'To Do'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        DONE = 'DONE', 'Done'

    class TaskPriority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'

    title = models.CharField(max_length=200)
    task_type = models.CharField(max_length=100, blank=True)
    priority = models.CharField(max_length=10, choices=TaskPriority.choices, default=TaskPriority.MEDIUM)
    subject = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='legal_tasks')
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.TODO)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
