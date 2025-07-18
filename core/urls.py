# --- FILE: core/urls.py (The Fix) ---
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('log_task/<int:task_id>/', views.log_task, name='log_task'),
    path('get_subtasks/<int:parent_id>/', views.get_subtasks, name='get_subtasks'),
    path('get_skills_list/', views.get_skills_list, name='get_skills_list'),
    path('get_buffs_list/', views.get_buffs_list, name='get_buffs_list'),
    path('get_add_task_form/', views.get_add_task_form, name='get_add_task_form'),
    path('add_task/', views.add_task, name='add_task'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('get_edit_form/<int:task_id>/', views.get_edit_form, name='get_edit_form'),
    path('update_task/<int:task_id>/', views.update_task, name='update_task'),
    path('get_task_item/<int:task_id>/', views.get_task_item, name='get_task_item'),
    path('get_add_subtask_form/<int:parent_id>/', views.get_add_subtask_form, name='get_add_subtask_form'),
    path('add_subtask/<int:parent_id>/', views.add_subtask, name='add_subtask'),
    path('skills/', views.skills_page_view, name='skills_page'),
    path('get-add-skill-form/', views.get_add_skill_form, name='get_add_skill_form'),
    path('get-add-skill-button/', views.get_add_skill_button, name='get_add_skill_button'),
    path('add_skill/', views.add_skill, name='add_skill'),
    path('get_skill_edit_form/<int:skill_id>/', views.get_skill_edit_form, name='get_skill_edit_form'),
    path('update_skill/<int:skill_id>/', views.update_skill, name='update_skill'),
    path('get_skill_item/<int:skill_id>/', views.get_skill_item, name='get_skill_item'),
    path('delete_skill/<int:skill_id>/', views.delete_skill, name='delete_skill'),
    path('get_skill_task_manager/<int:skill_id>/', views.get_skill_task_manager, name='get_skill_task_manager'),
    path('associate_task/<int:skill_id>/<int:task_id>/', views.associate_task_to_skill, name='associate_task_to_skill'),
    path('disassociate_task/<int:skill_id>/<int:task_id>/', views.disassociate_task_from_skill, name='disassociate_task_from_skill'),

]