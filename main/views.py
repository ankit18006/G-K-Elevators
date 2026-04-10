from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import date, timedelta
from .models import Elevator, Technician, FaultReport, MaintenanceSchedule, ServiceHistory, ContactMessage


# ─── Public Pages ────────────────────────────────────────────────────────────

def home(request):
    stats = {
        'elevators': Elevator.objects.count(),
        'technicians': Technician.objects.count(),
        'completed_services': FaultReport.objects.filter(status='completed').count(),
        'cities_served': Elevator.objects.values('location').distinct().count(),
    }
    return render(request, 'index.html', {'stats': stats})


def about(request):
    return render(request, 'about.html')


def services(request):
    return render(request, 'services.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        if name and email and subject and message:
            ContactMessage.objects.create(name=name, email=email, subject=subject, message=message)
            messages.success(request, 'Your message has been sent! We will get back to you soon.')
            return redirect('contact')
        else:
            messages.error(request, 'Please fill in all fields.')
    return render(request, 'contact.html')


# ─── Auth ─────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        if not username or not password1:
            messages.error(request, 'Username and password are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            user = User.objects.create_user(
                username=username, email=email, password=password1,
                first_name=first_name, last_name=last_name
            )
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name or user.username}!')
            return redirect('dashboard')
    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('home')


# ─── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    today = date.today()
    next_week = today + timedelta(days=7)

    total_elevators = Elevator.objects.count()
    working = Elevator.objects.filter(status='working').count()
    faulty = Elevator.objects.filter(status='faulty').count()
    under_maintenance = Elevator.objects.filter(status='maintenance').count()

    active_faults = FaultReport.objects.filter(status__in=['pending', 'in_progress']).count()
    completed_services = FaultReport.objects.filter(status='completed').count()
    pending_faults = FaultReport.objects.filter(status='pending').count()

    upcoming_maintenance = MaintenanceSchedule.objects.filter(
        scheduled_date__gte=today, scheduled_date__lte=next_week, status='scheduled'
    ).count()
    overdue_maintenance = MaintenanceSchedule.objects.filter(
        scheduled_date__lt=today, status='scheduled'
    ).count()

    recent_faults = FaultReport.objects.select_related('elevator', 'assigned_technician').order_by('-reported_at')[:5]
    upcoming_maint = MaintenanceSchedule.objects.filter(
        scheduled_date__gte=today, status='scheduled'
    ).select_related('elevator', 'technician').order_by('scheduled_date')[:5]

    # Chart data
    fault_type_data = list(
        FaultReport.objects.values('fault_type').annotate(count=Count('id')).order_by('-count')
    )
    status_data = {
        'working': working,
        'faulty': faulty,
        'maintenance': under_maintenance,
        'offline': Elevator.objects.filter(status='offline').count(),
    }

    context = {
        'total_elevators': total_elevators,
        'working': working,
        'faulty': faulty,
        'under_maintenance': under_maintenance,
        'active_faults': active_faults,
        'completed_services': completed_services,
        'pending_faults': pending_faults,
        'upcoming_maintenance': upcoming_maintenance,
        'overdue_maintenance': overdue_maintenance,
        'recent_faults': recent_faults,
        'upcoming_maint': upcoming_maint,
        'fault_type_data': fault_type_data,
        'status_data': status_data,
        'total_technicians': Technician.objects.count(),
    }
    return render(request, 'dashboard.html', context)


# ─── Elevators ────────────────────────────────────────────────────────────────

@login_required
def elevators(request):
    qs = Elevator.objects.select_related('assigned_technician').all()
    location_filter = request.GET.get('location', '')
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')

    if location_filter:
        qs = qs.filter(location__icontains=location_filter)
    if status_filter:
        qs = qs.filter(status=status_filter)
    if type_filter:
        qs = qs.filter(elevator_type=type_filter)

    locations = Elevator.objects.values_list('location', flat=True).distinct()
    technicians = Technician.objects.all()

    context = {
        'elevators': qs,
        'locations': locations,
        'technicians': technicians,
        'location_filter': location_filter,
        'status_filter': status_filter,
        'type_filter': type_filter,
    }
    return render(request, 'elevators.html', context)


@login_required
def add_elevator(request):
    if request.method == 'POST':
        try:
            elevator = Elevator(
                building_name=request.POST['building_name'],
                location=request.POST['location'],
                elevator_type=request.POST['elevator_type'],
                model_number=request.POST.get('model_number', ''),
                floors_served=request.POST.get('floors_served', 1),
                installation_date=request.POST['installation_date'],
                status=request.POST['status'],
                notes=request.POST.get('notes', ''),
                created_by=request.user,
            )
            tech_id = request.POST.get('assigned_technician')
            if tech_id:
                elevator.assigned_technician_id = tech_id
            elevator.save()
            messages.success(request, f'Elevator at {elevator.building_name} added successfully.')
            return redirect('elevators')
        except Exception as e:
            messages.error(request, f'Error adding elevator: {str(e)}')
    technicians = Technician.objects.filter(is_available=True)
    return render(request, 'elevator_form.html', {'technicians': technicians, 'action': 'Add'})


@login_required
def edit_elevator(request, pk):
    elevator = get_object_or_404(Elevator, pk=pk)
    if request.method == 'POST':
        try:
            elevator.building_name = request.POST['building_name']
            elevator.location = request.POST['location']
            elevator.elevator_type = request.POST['elevator_type']
            elevator.model_number = request.POST.get('model_number', '')
            elevator.floors_served = request.POST.get('floors_served', 1)
            elevator.installation_date = request.POST['installation_date']
            elevator.status = request.POST['status']
            elevator.notes = request.POST.get('notes', '')
            tech_id = request.POST.get('assigned_technician')
            elevator.assigned_technician_id = tech_id if tech_id else None
            elevator.save()
            messages.success(request, 'Elevator updated successfully.')
            return redirect('elevators')
        except Exception as e:
            messages.error(request, f'Error updating elevator: {str(e)}')
    technicians = Technician.objects.all()
    return render(request, 'elevator_form.html', {
        'elevator': elevator, 'technicians': technicians, 'action': 'Edit'
    })


@login_required
def elevator_detail(request, pk):
    elevator = get_object_or_404(Elevator, pk=pk)
    faults = elevator.fault_reports.select_related('assigned_technician').order_by('-reported_at')
    history = elevator.service_history.select_related('technician').order_by('-service_date')[:10]
    maintenance = elevator.maintenance_schedules.order_by('scheduled_date')[:5]
    return render(request, 'elevator_detail.html', {
        'elevator': elevator, 'faults': faults, 'history': history, 'maintenance': maintenance
    })


@login_required
def delete_elevator(request, pk):
    elevator = get_object_or_404(Elevator, pk=pk)
    if request.method == 'POST':
        elevator.delete()
        messages.success(request, 'Elevator deleted.')
    return redirect('elevators')


# ─── Technicians ──────────────────────────────────────────────────────────────

@login_required
def technicians(request):
    techs = Technician.objects.annotate(
        active_jobs=Count('fault_assignments', filter=Q(fault_assignments__status__in=['pending', 'in_progress']))
    ).all()
    return render(request, 'technicians.html', {'technicians': techs})


@login_required
def add_technician(request):
    if request.method == 'POST':
        skills_list = request.POST.getlist('skills')
        Technician.objects.create(
            name=request.POST['name'],
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            skills=', '.join(skills_list),
            is_available=request.POST.get('is_available') == 'on',
            joined_date=request.POST.get('joined_date') or date.today(),
            created_by=request.user,
        )
        messages.success(request, 'Technician added successfully.')
        return redirect('technicians')
    return render(request, 'technician_form.html', {'action': 'Add'})


@login_required
def edit_technician(request, pk):
    tech = get_object_or_404(Technician, pk=pk)
    if request.method == 'POST':
        skills_list = request.POST.getlist('skills')
        tech.name = request.POST['name']
        tech.email = request.POST.get('email', '')
        tech.phone = request.POST.get('phone', '')
        tech.skills = ', '.join(skills_list)
        tech.is_available = request.POST.get('is_available') == 'on'
        tech.joined_date = request.POST.get('joined_date') or date.today()
        tech.save()
        messages.success(request, 'Technician updated.')
        return redirect('technicians')
    return render(request, 'technician_form.html', {'technician': tech, 'action': 'Edit'})


@login_required
def delete_technician(request, pk):
    tech = get_object_or_404(Technician, pk=pk)
    if request.method == 'POST':
        tech.delete()
        messages.success(request, 'Technician deleted.')
    return redirect('technicians')


# ─── Fault Reports ────────────────────────────────────────────────────────────

@login_required
def faults(request):
    qs = FaultReport.objects.select_related('elevator', 'assigned_technician').order_by('-reported_at')
    status_filter = request.GET.get('status', '')
    fault_filter = request.GET.get('fault_type', '')
    severity_filter = request.GET.get('severity', '')

    if status_filter:
        qs = qs.filter(status=status_filter)
    if fault_filter:
        qs = qs.filter(fault_type=fault_filter)
    if severity_filter:
        qs = qs.filter(severity=severity_filter)

    context = {
        'faults': qs,
        'status_filter': status_filter,
        'fault_filter': fault_filter,
        'severity_filter': severity_filter,
    }
    return render(request, 'faults.html', context)


@login_required
def add_fault(request):
    if request.method == 'POST':
        try:
            fault = FaultReport(
                elevator_id=request.POST['elevator'],
                fault_type=request.POST['fault_type'],
                description=request.POST['description'],
                severity=request.POST['severity'],
                status=request.POST.get('status', 'pending'),
                reported_by=request.user,
            )
            tech_id = request.POST.get('assigned_technician')
            if tech_id:
                fault.assigned_technician_id = tech_id
            if 'image_before' in request.FILES:
                fault.image_before = request.FILES['image_before']
            fault.save()
            messages.success(request, 'Fault report submitted.')
            if fault.ai_suggestion:
                messages.warning(request, fault.ai_suggestion)
            return redirect('faults')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    elevators = Elevator.objects.all()
    technicians = Technician.objects.filter(is_available=True)
    return render(request, 'fault_form.html', {
        'elevators': elevators, 'technicians': technicians, 'action': 'Report'
    })


@login_required
def update_fault(request, pk):
    fault = get_object_or_404(FaultReport, pk=pk)
    if request.method == 'POST':
        fault.status = request.POST.get('status', fault.status)
        fault.resolution_notes = request.POST.get('resolution_notes', '')
        tech_id = request.POST.get('assigned_technician')
        fault.assigned_technician_id = tech_id if tech_id else None
        if 'image_after' in request.FILES:
            fault.image_after = request.FILES['image_after']
        fault.save()

        # Auto-create service history on completion
        if fault.status == 'completed':
            ServiceHistory.objects.create(
                elevator=fault.elevator,
                technician=fault.assigned_technician,
                fault_report=fault,
                service_date=date.today(),
                work_done=f"Resolved: {fault.get_fault_type_display()}. {fault.resolution_notes}",
                recorded_by=request.user,
            )
            # Update elevator status back to working
            fault.elevator.status = 'working'
            fault.elevator.save()
        messages.success(request, 'Fault report updated.')
        return redirect('faults')
    technicians = Technician.objects.all()
    return render(request, 'fault_update.html', {'fault': fault, 'technicians': technicians})


@login_required
def delete_fault(request, pk):
    fault = get_object_or_404(FaultReport, pk=pk)
    if request.method == 'POST':
        fault.delete()
        messages.success(request, 'Fault report deleted.')
    return redirect('faults')


# ─── Maintenance ──────────────────────────────────────────────────────────────

@login_required
def maintenance(request):
    today = date.today()
    qs = MaintenanceSchedule.objects.select_related('elevator', 'technician').order_by('scheduled_date')

    # Mark overdue
    qs.filter(scheduled_date__lt=today, status='scheduled').update(status='overdue')

    upcoming = qs.filter(scheduled_date__gte=today, status='scheduled')
    overdue = qs.filter(status='overdue')
    completed = qs.filter(status='completed').order_by('-completed_at')[:10]

    return render(request, 'maintenance.html', {
        'upcoming': upcoming,
        'overdue': overdue,
        'completed': completed,
        'today': today,
    })


@login_required
def add_maintenance(request):
    if request.method == 'POST':
        try:
            MaintenanceSchedule.objects.create(
                elevator_id=request.POST['elevator'],
                maintenance_type=request.POST['maintenance_type'],
                scheduled_date=request.POST['scheduled_date'],
                technician_id=request.POST.get('technician') or None,
                notes=request.POST.get('notes', ''),
                created_by=request.user,
            )
            messages.success(request, 'Maintenance scheduled successfully.')
            return redirect('maintenance')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    elevators = Elevator.objects.all()
    technicians = Technician.objects.filter(is_available=True)
    return render(request, 'maintenance_form.html', {'elevators': elevators, 'technicians': technicians})


@login_required
def complete_maintenance(request, pk):
    maint = get_object_or_404(MaintenanceSchedule, pk=pk)
    if request.method == 'POST':
        maint.status = 'completed'
        maint.completed_at = timezone.now()
        maint.notes += '\n' + request.POST.get('completion_notes', '')
        maint.save()
        ServiceHistory.objects.create(
            elevator=maint.elevator,
            technician=maint.technician,
            maintenance=maint,
            service_date=date.today(),
            work_done=f"Scheduled {maint.get_maintenance_type_display()} completed.",
            recorded_by=request.user,
        )
        messages.success(request, 'Maintenance marked as completed.')
        return redirect('maintenance')
    return render(request, 'complete_maintenance.html', {'maint': maint})


@login_required
def service_history(request):
    history = ServiceHistory.objects.select_related(
        'elevator', 'technician', 'fault_report'
    ).order_by('-service_date')
    return render(request, 'service_history.html', {'history': history})
