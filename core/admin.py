from django.contrib import admin
from .models import InfrastructureReport

@admin.register(InfrastructureReport)
class InfrastructureReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'barangay', 'severity', 'status', 'priority_score', 'created_at')
    list_filter = ('status', 'category', 'barangay')
    search_fields = ('title', 'description', 'barangay')