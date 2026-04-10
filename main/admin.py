from django.contrib import admin
from .models import Elevator, Technician, FaultReport, MaintenanceSchedule, ServiceHistory, ContactMessage

@admin.register(Elevator)
class ElevatorAdmin(admin.ModelAdmin):
    list_display = ['building_name', 'location', 'elevator_type', 'status', 'installation_date']
    list_filter = ['status', 'elevator_type']
    search_fields = ['building_name', 'location']

@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'skills', 'is_available']

@admin.register(FaultReport)
class FaultReportAdmin(admin.ModelAdmin):
    list_display = ['elevator', 'fault_type', 'severity', 'status', 'reported_at']
    list_filter = ['status', 'fault_type', 'severity']

@admin.register(MaintenanceSchedule)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ['elevator', 'maintenance_type', 'scheduled_date', 'status']
    list_filter = ['status', 'maintenance_type']

@admin.register(ServiceHistory)
class ServiceHistoryAdmin(admin.ModelAdmin):
    list_display = ['elevator', 'technician', 'service_date', 'work_done']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'submitted_at', 'is_read']
