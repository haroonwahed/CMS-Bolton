from django.contrib import admin
from .models import Contract, Tag, Note

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('title', 'counterparty', 'status', 'contract_type', 'created_by', 'updated_at')
    list_filter = ('status', 'contract_type', 'jurisdiction')
    search_fields = ('title', 'counterparty')
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    autocomplete_fields = ['tags']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('contract', 'created_by', 'timestamp')
    list_filter = ('timestamp', 'created_by')
    search_fields = ('text', 'contract__title')
    readonly_fields = ('created_by', 'timestamp')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('contract', 'created_by')
