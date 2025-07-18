# --- FILE: core/signals.py (MODIFIED CODE) ---

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import TaskLog
from .logic import check_for_level_up, recalculate_skill_level

# This signal runs AFTER a new TaskLog is saved successfully.
@receiver(post_save, sender=TaskLog)
def handle_task_log_save(sender, instance, created, **kwargs):
    # 'created' is True only the first time the object is saved.
    if created:
        logged_task = instance.task
        user = instance.user

        # Use a set to collect all unique skills to be processed.
        skills_to_process = set()

        # 1. Add skills from the task that was directly logged.
        skills_to_process.update(logged_task.skills.all())

        # 2. If the logged task is a parent, add skills from all its subtasks.
        # We check if the 'subtasks' related manager exists and has items.
        if hasattr(logged_task, 'subtasks') and logged_task.subtasks.exists():
            for subtask in logged_task.subtasks.all():
                skills_to_process.update(subtask.skills.all())
        
        # 3. Now, loop through the unique set of skills and check for level-ups.
        for skill in skills_to_process:
            check_for_level_up(user=user, skill=skill)


@receiver(post_delete, sender=TaskLog)
def handle_task_log_delete(sender, instance, **kwargs):
    deleted_task = instance.task
    user = instance.user

    # Use a set to collect all unique skills, just like in the save handler.
    skills_to_recalculate = set()

    # 1. Add skills from the task of the deleted log.
    skills_to_recalculate.update(deleted_task.skills.all())

    # 2. If it was a parent task, add skills from all its subtasks.
    if hasattr(deleted_task, 'subtasks') and deleted_task.subtasks.exists():
        for subtask in deleted_task.subtasks.all():
            skills_to_recalculate.update(subtask.skills.all())
            
    # 3. Now, loop through the unique set of skills and recalculate.
    for skill in skills_to_recalculate:
        recalculate_skill_level(user=user, skill=skill)