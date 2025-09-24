# inspections/admin.py
from django.contrib import admin
from .models import InspectionReport, InspectionFinding, RequiredPart, RequiredConsumable


class RequiredPartInline(admin.TabularInline):
    model = RequiredPart
    extra = 1
    fields = ('description', 'part_number', 'quantity', 'status', 'notes')


class RequiredConsumableInline(admin.TabularInline):
    model = RequiredConsumable
    extra = 1
    fields = ('name', 'quantity', 'unit', 'notes')


class InspectionFindingInline(admin.StackedInline):
    model = InspectionFinding
    extra = 1
    fields = ('description', 'severity', 'time_required', 'remarks')
    inlines = [RequiredPartInline, RequiredConsumableInline]

    # Inject nested inlines manually (Django doesn't support nested inlines natively)
    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        if obj:  # Load nested inlines only when editing existing report
            for finding in obj.findings.all():
                inline_instances.append(RequiredPartInline(self.model, self.admin_site))
                inline_instances.append(RequiredConsumableInline(self.model, self.admin_site))
        return inline_instances


@admin.register(InspectionReport)
class InspectionReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'job_card', 'created_by', 'total_findings', 'total_estimated_hours', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('job_card__id', 'job_card__vehicle__plate_number')
    readonly_fields = ('created_at', 'updated_at', 'total_findings', 'total_estimated_hours')
    inlines = [InspectionFindingInline]

    fieldsets = (
        ('Linked Job Card', {
            'fields': ('job_card', 'created_by')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'total_findings', 'total_estimated_hours'),
            'classes': ('collapse',)
        }),
    )
