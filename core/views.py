# --- FILE: core/views.py ---
from django.shortcuts import render, redirect, get_object_or_404 # Add redirect and get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST # Import this decorator

from .models import Task, TaskLog, UserSkillProgress, Buff
# The home view is no longer needed since we are using a dashboard
# You can delete the old home function

@login_required
def dashboard(request):
    # --- MODIFY THIS LINE ---
    # Fetch only top-level tasks (those with no parent).
    # The subtasks will be accessed from the template.
    parent_tasks = Task.objects.filter(user=request.user, parent_task__isnull=True).order_by('display_order')
    
    skill_progress = UserSkillProgress.objects.filter(user=request.user).select_related('skill', 'current_level')
    active_buffs = Buff.objects.filter(user=request.user, is_active=True)

    context = {
        # --- UPDATE THE CONTEXT KEY ---
        'tasks': parent_tasks, # We are passing parent_tasks to the 'tasks' key
        'skill_progress': skill_progress,
        'active_buffs': active_buffs,
    }
    
    return render(request, 'core/dashboard.html', context)

@require_POST
@login_required
def log_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)

    # --- MODIFICATION STARTS HERE ---
    
    # 1. Get the count of buffs BEFORE logging the task
    buff_count_before = Buff.objects.filter(user=request.user, is_active=True).count()

    # Create the log(s) - this is the existing logic that might trigger a level up
    TaskLog.objects.create(user=request.user, task=task)
    
    subtasks = task.subtasks.all()
    if subtasks.exists():
        for subtask in subtasks:
            TaskLog.objects.create(user=request.user, task=subtask)

    # 2. Get the count of buffs AFTER logging the task
    buff_count_after = Buff.objects.filter(user=request.user, is_active=True).count()
    
    # 3. Create the htmx response object
    if request.POST.get('is_htmx'):
        if subtasks.exists():
            context = {'task': task, 'subtasks': subtasks}
            response = render(request, 'core/partials/cascading_log_response.html', context)
        else:
            context = {'task': task}
            response = render(request, 'core/partials/task_item_logged.html', context)
        
        # 4. If a new buff was created, add the HX-Trigger header to the response
        if buff_count_after > buff_count_before:
            response['HX-Trigger'] = 'levelUp'
            
        return response
        

@login_required
def get_subtasks(request, parent_id):
    parent_task = get_object_or_404(Task, id=parent_id, user=request.user)

    # Check if we are in "collapse" mode
    if request.GET.get('clear'):
        # Return an empty string for the main target, and the original '+' button via OOB
        return render(request, 'core/partials/expand_button_oob.html', {'task': parent_task})

    # "Expand" mode (the original logic)
    subtasks = parent_task.subtasks.all().order_by('display_order')
    context = {
        'subtasks': subtasks,
        'parent_task': parent_task # Pass the parent task for the template IDs
    }
    return render(request, 'core/partials/subtask_list_with_collapse_btn.html', context)    


@login_required
def get_skills_list(request):
    skill_progress = UserSkillProgress.objects.filter(user=request.user).select_related('skill', 'current_level')
    return render(request, 'core/partials/skills_list.html', {'skill_progress': skill_progress})

@login_required
def get_buffs_list(request):
    active_buffs = Buff.objects.filter(user=request.user, is_active=True)
    return render(request, 'core/partials/buffs_list.html', {'active_buffs': active_buffs})