from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Technician(models.Model):
    SKILL_CHOICES = [
        ('wiring', 'Wiring'),
        ('sensors', 'Sensors'),
        ('pcb', 'PCB / Motherboard'),
        ('mechanical', 'Mechanical'),
        ('full', 'Full Service'),
    ]
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    skills = models.CharField(max_length=200, help_text="Comma-separated skills")
    is_available = models.BooleanField(default=True)
    joined_date = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    def skills_list(self):
        return [s.strip() for s in self.skills.split(',') if s.strip()]


class Elevator(models.Model):
    TYPE_CHOICES = [
        ('passenger', 'Passenger'),
        ('goods', 'Goods / Freight'),
        ('service', 'Service'),
        ('hospital', 'Hospital / Stretcher'),
    ]
    STATUS_CHOICES = [
        ('working', 'Working'),
        ('faulty', 'Faulty'),
        ('maintenance', 'Under Maintenance'),
        ('offline', 'Offline'),
    ]
    building_name = models.CharField(max_length=200)
    location = models.CharField(max_length=300)
    elevator_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='passenger')
    model_number = models.CharField(max_length=100, blank=True)
    floors_served = models.PositiveIntegerField(default=1)
    installation_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='working')
    assigned_technician = models.ForeignKey(
        Technician, on_delete=models.SET_NULL, null=True, blank=True, related_name='elevators'
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.building_name} - {self.get_elevator_type_display()}"

    def get_active_faults(self):
        return self.fault_reports.filter(status__in=['pending', 'in_progress'])

    def get_fault_count(self):
        return self.fault_reports.count()


class FaultReport(models.Model):
    FAULT_TYPE_CHOICES = [
        ('sensor', 'Sensor Issue'),
        ('door', 'Door Issue'),
        ('motor', 'Motor Issue'),
        ('pcb', 'PCB / Motherboard Failure'),
        ('wiring', 'Wiring Issue'),
        ('cabin', 'Cabin Issue'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('escalated', 'Escalated'),
    ]
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    elevator = models.ForeignKey(Elevator, on_delete=models.CASCADE, related_name='fault_reports')
    fault_type = models.CharField(max_length=20, choices=FAULT_TYPE_CHOICES)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_technician = models.ForeignKey(
        Technician, on_delete=models.SET_NULL, null=True, blank=True, related_name='fault_assignments'
    )
    image_before = models.ImageField(upload_to='fault_images/before/', blank=True, null=True)
    image_after = models.ImageField(upload_to='fault_images/after/', blank=True, null=True)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    ai_suggestion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.elevator} - {self.get_fault_type_display()} ({self.status})"

    def save(self, *args, **kwargs):
        # AI suggestion: if same fault type repeats 3+ times, suggest replacement
        if self.pk is None:  # new report
            repeat_count = FaultReport.objects.filter(
                elevator=self.elevator,
                fault_type=self.fault_type
            ).count()
            if repeat_count >= 2:
                self.ai_suggestion = (
                    f"⚠️ Smart Suggestion: This elevator has reported '{self.get_fault_type_display()}' "
                    f"{repeat_count + 1} times. Consider replacing the {self.get_fault_type_display()} "
                    f"component entirely instead of repeated repairs."
                )
        if self.status == 'completed' and not self.resolved_at:
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)


class MaintenanceSchedule(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    TYPE_CHOICES = [
        ('monthly', 'Monthly Service'),
        ('quarterly', 'Quarterly Inspection'),
        ('annual', 'Annual Overhaul'),
        ('emergency', 'Emergency Check'),
    ]

    elevator = models.ForeignKey(Elevator, on_delete=models.CASCADE, related_name='maintenance_schedules')
    maintenance_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='monthly')
    scheduled_date = models.DateField()
    technician = models.ForeignKey(
        Technician, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_jobs'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.elevator} - {self.get_maintenance_type_display()} on {self.scheduled_date}"

    def is_overdue(self):
        from datetime import date
        return self.scheduled_date < date.today() and self.status == 'scheduled'


class ServiceHistory(models.Model):
    elevator = models.ForeignKey(Elevator, on_delete=models.CASCADE, related_name='service_history')
    technician = models.ForeignKey(
        Technician, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_records'
    )
    fault_report = models.ForeignKey(
        FaultReport, on_delete=models.SET_NULL, null=True, blank=True
    )
    maintenance = models.ForeignKey(
        MaintenanceSchedule, on_delete=models.SET_NULL, null=True, blank=True
    )
    service_date = models.DateField()
    work_done = models.TextField()
    parts_replaced = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.elevator} service on {self.service_date}"

    class Meta:
        ordering = ['-service_date']


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject}"
