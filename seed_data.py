"""
Optional seed data script.
Run with: python manage.py shell < seed_data.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elevator_system.settings')

from datetime import date, timedelta
from django.contrib.auth.models import User
from main.models import Elevator, Technician, FaultReport, MaintenanceSchedule

print("Seeding sample data...")

# Demo user
if not User.objects.filter(username='demo').exists():
    demo = User.objects.create_user('demo', 'demo@elevatech.com', 'demo1234', first_name='Demo', last_name='User')
    print("Created demo user: username=demo, password=demo1234")
else:
    demo = User.objects.get(username='demo')

# Technicians
techs_data = [
    {'name': 'Ravi Kumar',    'email': 'ravi@elevatech.com',    'phone': '+91 98100 11111', 'skills': 'Wiring, PCB / Motherboard'},
    {'name': 'Priya Sharma',  'email': 'priya@elevatech.com',   'phone': '+91 98100 22222', 'skills': 'Sensors, Full Service'},
    {'name': 'James Mathew',  'email': 'james@elevatech.com',   'phone': '+91 98100 33333', 'skills': 'Mechanical, Wiring'},
    {'name': 'Anita Desai',   'email': 'anita@elevatech.com',   'phone': '+91 98100 44444', 'skills': 'PCB / Motherboard, Sensors'},
]
techs = []
for t in techs_data:
    obj, created = Technician.objects.get_or_create(name=t['name'], defaults={**t, 'joined_date': date(2022, 1, 1), 'created_by': demo})
    techs.append(obj)
    if created: print(f"  Created technician: {obj.name}")

# Elevators
elevs_data = [
    {'building_name': 'Skyline Tower A',    'location': 'Bandra, Mumbai',     'elevator_type': 'passenger', 'floors_served': 24, 'installation_date': date(2019, 3, 15), 'status': 'working',     'assigned_technician': techs[0]},
    {'building_name': 'Green Valley Mall',  'location': 'Andheri, Mumbai',    'elevator_type': 'goods',     'floors_served': 4,  'installation_date': date(2020, 7, 1),  'status': 'working',     'assigned_technician': techs[1]},
    {'building_name': 'Sunrise Residency',  'location': 'Powai, Mumbai',      'elevator_type': 'passenger', 'floors_served': 18, 'installation_date': date(2021, 1, 20), 'status': 'faulty',      'assigned_technician': techs[2]},
    {'building_name': 'City Hospital',      'location': 'Dadar, Mumbai',      'elevator_type': 'hospital',  'floors_served': 8,  'installation_date': date(2018, 5, 10), 'status': 'working',     'assigned_technician': techs[3]},
    {'building_name': 'Tech Park Block B',  'location': 'Goregaon, Mumbai',   'elevator_type': 'service',   'floors_served': 12, 'installation_date': date(2022, 9, 5),  'status': 'maintenance', 'assigned_technician': techs[0]},
    {'building_name': 'Ocean View Apts',    'location': 'Worli, Mumbai',      'elevator_type': 'passenger', 'floors_served': 30, 'installation_date': date(2023, 2, 14), 'status': 'working',     'assigned_technician': techs[1]},
]
elevs = []
for e in elevs_data:
    obj, created = Elevator.objects.get_or_create(building_name=e['building_name'], defaults={**e, 'created_by': demo})
    elevs.append(obj)
    if created: print(f"  Created elevator: {obj.building_name}")

# Fault Reports
faults_data = [
    {'elevator': elevs[2], 'fault_type': 'sensor',    'description': 'Floor level sensor not triggering correctly on floors 5 and 7.', 'severity': 'high',     'status': 'in_progress', 'assigned_technician': techs[2]},
    {'elevator': elevs[0], 'fault_type': 'door',      'description': 'Main lobby door takes too long to close, safety sensor intermittent.', 'severity': 'medium', 'status': 'pending',     'assigned_technician': techs[0]},
    {'elevator': elevs[4], 'fault_type': 'motor',     'description': 'Unusual humming noise during ascent above floor 8.', 'severity': 'high',     'status': 'pending',     'assigned_technician': techs[2]},
    {'elevator': elevs[1], 'fault_type': 'pcb',       'description': 'Control board showing error code E07 intermittently.',    'severity': 'critical', 'status': 'in_progress', 'assigned_technician': techs[3]},
    {'elevator': elevs[3], 'fault_type': 'wiring',    'description': 'Floor 3 call button not responding, wiring inspection needed.', 'severity': 'low',  'status': 'completed',   'assigned_technician': techs[0]},
]
for f in faults_data:
    obj, created = FaultReport.objects.get_or_create(
        elevator=f['elevator'], fault_type=f['fault_type'],
        defaults={**f, 'reported_by': demo}
    )
    if created: print(f"  Created fault: {obj.elevator.building_name} — {obj.get_fault_type_display()}")

# Maintenance Schedules
today = date.today()
maint_data = [
    {'elevator': elevs[0], 'maintenance_type': 'monthly',    'scheduled_date': today + timedelta(days=5),  'technician': techs[0], 'status': 'scheduled'},
    {'elevator': elevs[1], 'maintenance_type': 'quarterly',  'scheduled_date': today + timedelta(days=14), 'technician': techs[1], 'status': 'scheduled'},
    {'elevator': elevs[3], 'maintenance_type': 'monthly',    'scheduled_date': today - timedelta(days=3),  'technician': techs[3], 'status': 'overdue'},
    {'elevator': elevs[5], 'maintenance_type': 'annual',     'scheduled_date': today + timedelta(days=30), 'technician': techs[1], 'status': 'scheduled'},
    {'elevator': elevs[2], 'maintenance_type': 'emergency',  'scheduled_date': today + timedelta(days=1),  'technician': techs[2], 'status': 'scheduled'},
]
for m in maint_data:
    obj, created = MaintenanceSchedule.objects.get_or_create(
        elevator=m['elevator'], maintenance_type=m['maintenance_type'], scheduled_date=m['scheduled_date'],
        defaults={**m, 'created_by': demo}
    )
    if created: print(f"  Created maintenance: {obj.elevator.building_name} — {obj.get_maintenance_type_display()}")

print("\n✅ Seed data complete!")
print("Login at /login/ with username='demo', password='demo1234'")
