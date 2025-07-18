# --- FILE: core/views.py ---
from django.shortcuts import render, redirect, get_object_or_404 # Add redirect and get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods # Import these decorators
from django.http import HttpResponse


from .models import Task, TaskLog, UserSkillProgress, Buff, Skill
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
    
    # 1. Get the count of buffs BEFORE logging the task
    buff_count_before = Buff.objects.filter(user=request.user, is_active=True).count()

    # --- THIS IS THE CHANGE ---
    # We now only create ONE log for the task that was clicked.
    # The signal will handle the subtask skill inheritance.
    TaskLog.objects.create(user=request.user, task=task)
    
    # We still get the subtasks to pass to the htmx response for the UI.
    subtasks = task.subtasks.all()

    # 2. Get the count of buffs AFTER logging the task
    buff_count_after = Buff.objects.filter(user=request.user, is_active=True).count()
    
    # 3. Create the htmx response object (This logic remains the same)
    if request.POST.get('is_htmx'):
        # If the logged task has subtasks, we use the cascading response
        # to show they were logged too.
        if subtasks.exists():
            context = {'task': task, 'subtasks': subtasks}
            response = render(request, 'core/partials/cascading_log_response.html', context)
        # Otherwise, use the standard "logged" response
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

    # This handles the "Close" button click
    if request.GET.get('clear'):
        # We need to send back the ORIGINAL "Subtasks" button
        return render(request, 'core/partials/subtask_button_oob.html', {'task': parent_task})

    # This handles the "Subtasks" button click
    subtasks = parent_task.subtasks.all().order_by('display_order')
    context = {
        'subtasks': subtasks,
        'parent_task': parent_task
    }
    # We send back the list AND the new "Close" button
    return render(request, 'core/partials/subtask_list_with_close_btn.html', context)


@login_required
def get_skills_list(request):
    skill_progress = UserSkillProgress.objects.filter(user=request.user).select_related('skill', 'current_level')
    return render(request, 'core/partials/skills_list.html', {'skill_progress': skill_progress})

@login_required
def get_buffs_list(request):
    active_buffs = Buff.objects.filter(user=request.user, is_active=True)
    return render(request, 'core/partials/buffs_list.html', {'active_buffs': active_buffs})

@login_required
def get_add_task_form(request):
    """Returns the HTML for the add task form."""
    return render(request, 'core/partials/add_task_form.html')

@require_POST
@login_required
def add_task(request):
    """Processes the form submission, creates a new task, and returns the task item HTML."""
    task_name = request.POST.get('task_name')
    if task_name:
        # For now, we only create top-level tasks.
        new_task = Task.objects.create(
            user=request.user, 
            name=task_name,
            parent_task=None # Explicitly a top-level task
        )
        # Return the HTML fragment for just the new task
        return render(request, 'core/partials/task_item.html', {'task': new_task})
    
    # If the name is blank, return an empty response so nothing happens
    return HttpResponse("")

@require_http_methods(["DELETE"]) # This ensures only DELETE requests are allowed
@login_required
def delete_task(request, task_id):
    """Finds the task by its ID, deletes it, and returns an empty response."""
    # Find the task ensuring it belongs to the logged-in user for security
    task_to_delete = get_object_or_404(Task, id=task_id, user=request.user)
    
    task_to_delete.delete()
    
    # Return an empty response with a 200 OK status.
    # This tells htmx the request was successful and it should proceed
    # with the swap (removing the element from the page).
    return HttpResponse("")

@login_required
def get_edit_form(request, task_id):
    """Returns the form for editing a specific task."""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    # THE ERROR IS LIKELY ON THIS LINE.
    # It must return 'edit_task_form.html'.
    return render(request, 'core/partials/edit_task_form.html', {'task': task})

    
@login_required
def get_task_item(request, task_id):
    """Returns the normal display for a single task item."""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    return render(request, 'core/partials/task_item.html', {'task': task})

@require_http_methods(["PUT"]) # Note: We use PUT for updates
@login_required
def update_task(request, task_id):
    """Processes the edit form submission and updates the task."""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    # htmx sends PUT data in a different way, so we need to parse it
    from django.http import QueryDict
    put_data = QueryDict(request.body)
    new_name = put_data.get('task_name')

    if new_name:
        task.name = new_name
        task.save()
    
    # Return the updated, normal task display
    return render(request, 'core/partials/task_item.html', {'task': task})

@login_required
def get_add_subtask_form(request, parent_id):
    """Returns the form for adding a subtask to a parent."""
    parent_task = get_object_or_404(Task, id=parent_id, user=request.user)
    return render(request, 'core/partials/add_subtask_form.html', {'parent_task': parent_task})

@require_POST
@login_required
def add_subtask(request, parent_id):
    """Processes the form submission, creates a new subtask."""
    parent_task = get_object_or_404(Task, id=parent_id, user=request.user)
    subtask_name = request.POST.get('subtask_name')

    if subtask_name:
        # Create the new subtask, linking it to its parent
        new_subtask = Task.objects.create(
            user=request.user,
            name=subtask_name,
            parent_task=parent_task
        )
        # Return the HTML for the new subtask list item
        return render(request, 'core/partials/task_item.html', {'task': new_subtask})
    
    return HttpResponse("")

@login_required
def skills_page_view(request):
    """
    Displays the main skills management page.
    """
    skills = Skill.objects.filter(user=request.user)
    context = {
        'skills': skills
    }
    return render(request, 'core/skills_page.html', context)

@login_required
def get_add_skill_form(request):
    """
    Returns the HTML for the add skill form.
    """
    return render(request, 'core/partials/add_skill_form.html')


@login_required
def get_add_skill_button(request):
    """
    Returns the original 'Create New Skill' button.
    """
    return render(request, 'core/partials/get_add_skill_button.html')


@require_POST
@login_required
def add_skill(request):
    """
    Processes the form submission, creates a new skill,
    and returns the HTML for the new skill item.
    """
    skill_name = request.POST.get('skill_name')
    if skill_name:
        # Create the new skill for the logged-in user
        new_skill = Skill.objects.create(
            user=request.user, 
            name=skill_name
        )
        # Return the HTML fragment for just the new skill item
        # This uses the 'skill_item.html' partial we created earlier
        return render(request, 'core/partials/skill_item.html', {'skill': new_skill})
    
    # If the name is blank, return an empty response so nothing happens
    return HttpResponse("")



@login_required
def get_skill_edit_form(request, skill_id):
    """
    Returns the form for editing a specific skill.
    """
    skill = get_object_or_404(Skill, id=skill_id, user=request.user)
    return render(request, 'core/partials/edit_skill_form.html', {'skill': skill})

@require_http_methods(["PUT"])
@login_required
def update_skill(request, skill_id):
    """
    Processes the edit form submission and updates the skill.
    """
    skill = get_object_or_404(Skill, id=skill_id, user=request.user)
    
    from django.http import QueryDict
    put_data = QueryDict(request.body)
    new_name = put_data.get('skill_name')

    if new_name:
        skill.name = new_name
        skill.save()
    
    # Return the updated, normal skill display
    return render(request, 'core/partials/skill_item.html', {'skill': skill})

@login_required
def get_skill_item(request, skill_id):
    """
    Returns the normal display for a single skill item (used for canceling an edit).
    """
    skill = get_object_or_404(Skill, id=skill_id, user=request.user)
    return render(request, 'core/partials/skill_item.html', {'skill': skill})

@require_http_methods(["DELETE"])
@login_required
def delete_skill(request, skill_id):
    """
    Finds the skill by its ID, deletes it, and returns an empty response.
    """
    skill_to_delete = get_object_or_404(Skill, id=skill_id, user=request.user)
    skill_to_delete.delete()
    
    # Return an empty 200 OK response to signal success to htmx
    return HttpResponse("")


# --- FILE: core/views.py ---
# --- FILE: core/views.py (Replace the function with this) ---
@login_required
def get_skill_task_manager(request, skill_id):
    """
    Fetches and returns the task management UI for a specific skill,
    or clears it if 'clear=true' is passed.
    This logic now mirrors the get_subtasks view.
    """
    skill = get_object_or_404(Skill, id=skill_id, user=request.user)

    # If the "Close" button was clicked, it sends ?clear=true
    if request.GET.get('clear'):
        # Return an empty main response to clear the panel
        # And include the OOB template to restore the original button
        return render(request, 'core/partials/manage_tasks_button_oob.html', {'skill': skill})

    # If the "Manage Tasks" button was clicked, get the data for the panel
    linked_tasks = skill.tasks.all()
    unlinked_tasks = Task.objects.filter(user=request.user).exclude(id__in=linked_tasks.values_list('id', flat=True))

    context = {
        'skill': skill,
        'linked_tasks': linked_tasks,
        'unlinked_tasks': unlinked_tasks
    }
    
    # Render the template that contains both the panel AND the OOB "Close" button
    return render(request, 'core/partials/skill_task_manager_with_close_btn.html', context)

@require_POST
@login_required
def associate_task_to_skill(request, skill_id, task_id):
    """
    Creates an association between a skill and a task.
    """
    skill = get_object_or_404(Skill, id=skill_id, user=request.user)
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    # This is the key line to create the association
    skill.tasks.add(task)
    
    # After adding, we return the refreshed manager component
    # IMPORTANT: Ensure this view returns the correct template now
    return get_skill_task_manager(request, skill_id)

@require_POST
@login_required
def disassociate_task_from_skill(request, skill_id, task_id):
    """
    Removes an association between a skill and a task.
    """
    skill = get_object_or_404(Skill, id=skill_id, user=request.user)
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    # This is the key line to remove the association
    skill.tasks.remove(task)

    # After removing, we also return the refreshed manager component
    return get_skill_task_manager(request, skill_id)

