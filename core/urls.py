# --- FILE: core/urls.py (The Fix) ---
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('log_task/<int:task_id>/', views.log_task, name='log_task'),
    path('get_subtasks/<int:parent_id>/', views.get_subtasks, name='get_subtasks'),
    path('get_skills_list/', views.get_skills_list, name='get_skills_list'),
    path('get_buffs_list/', views.get_buffs_list, name='get_buffs_list'),
]