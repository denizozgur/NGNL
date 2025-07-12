# --- FILE: core/signals.py (FULL AND CORRECTED CODE) ---

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import TaskLog
from .logic import check_for_level_up, recalculate_skill_level

# This signal runs AFTER a new TaskLog is saved successfully.
@receiver(post_save, sender=TaskLog)
def handle_task_log_save(sender, instance, created, **kwargs):
    # 'created' is True only the first time the object is saved.
    if created:
        for skill in instance.task.skills.all():
            check_for_level_up(user=instance.user, skill=skill)

# This signal runs AFTER a TaskLog is deleted successfully.
@receiver(post_delete, sender=TaskLog)
def handle_task_log_delete(sender, instance, **kwargs):
    for skill in instance.task.skills.all():
        recalculate_skill_level(user=instance.user, skill=skill)