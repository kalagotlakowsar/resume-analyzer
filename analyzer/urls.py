from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_resume, name='upload_resume'),
    path('report/<int:report_id>/', views.view_report, name='view_report'),
    path('report/<int:report_id>/download/', views.download_report_pdf, name='download_report_pdf'),
    path('history/', views.resume_history, name='resume_history'),
    path('compare/', views.compare_resumes, name='compare_resumes'),
    path('resume/<int:resume_id>/delete/', views.delete_resume, name='delete_resume'),
    path('api/role-skills/<int:role_id>/', views.ajax_skills_for_role, name='ajax_skills_for_role'),
]
