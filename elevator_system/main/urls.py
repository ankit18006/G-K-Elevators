from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Elevators
    path('elevators/', views.elevators, name='elevators'),
    path('elevators/add/', views.add_elevator, name='add_elevator'),
    path('elevators/<int:pk>/', views.elevator_detail, name='elevator_detail'),
    path('elevators/<int:pk>/edit/', views.edit_elevator, name='edit_elevator'),
    path('elevators/<int:pk>/delete/', views.delete_elevator, name='delete_elevator'),

    # Technicians
    path('technicians/', views.technicians, name='technicians'),
    path('technicians/add/', views.add_technician, name='add_technician'),
    path('technicians/<int:pk>/edit/', views.edit_technician, name='edit_technician'),
    path('technicians/<int:pk>/delete/', views.delete_technician, name='delete_technician'),

    # Faults
    path('faults/', views.faults, name='faults'),
    path('faults/add/', views.add_fault, name='add_fault'),
    path('faults/<int:pk>/update/', views.update_fault, name='update_fault'),
    path('faults/<int:pk>/delete/', views.delete_fault, name='delete_fault'),

    # Maintenance
    path('maintenance/', views.maintenance, name='maintenance'),
    path('maintenance/add/', views.add_maintenance, name='add_maintenance'),
    path('maintenance/<int:pk>/complete/', views.complete_maintenance, name='complete_maintenance'),

    # Service History
    path('service-history/', views.service_history, name='service_history'),
]
