from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_overview, name='admin_dashboard'),
    path('users/', views.manage_users, name='manage_users'),
    path('users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),
    path('roles/', views.manage_roles, name='manage_roles'),
    path('roles/add/', views.add_role, name='add_role'),
    path('roles/<int:role_id>/edit/', views.edit_role, name='edit_role'),
    path('roles/<int:role_id>/delete/', views.delete_role, name='delete_role'),
    path('skills/', views.manage_skills, name='manage_skills'),
    path('skills/<int:skill_id>/delete/', views.delete_skill, name='delete_skill'),
    path('logs/', views.resume_logs, name='resume_logs'),
    path('logs/export-csv/', views.export_resumes_csv, name='export_resumes_csv'),
]
