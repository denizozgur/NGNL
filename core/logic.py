# --- FILE: core/logic.py (FULL AND CORRECTED CODE) ---

from .models import Buff, Level, TaskLog, UserSkillProgress

# Function 1: To create a new, active buff.
def apply_buff_from_level(user, level):
    """Creates and applies a new, ACTIVE buff to a user based on a level."""
    # Check if a buff from this level already exists to prevent duplicates.
    if Buff.objects.filter(user=user, source_level=level).exists():
        return

    Buff.objects.create(
        user=user,
        name=f"{level.skill.name} Lv. {level.level_number} Bonus",
        description=level.benefits_description, # Using your field name
        source_level=level,
        is_active=True  # This is the most important line
    )

# Function 2: The main function to call after a task is logged.
def check_for_level_up(user, skill):
    """
    Checks if a user has enough logs to level up in a skill.
    If they do, it updates their progress and calls apply_buff_from_level.
    """
    try:
        progress = UserSkillProgress.objects.get(user=user, skill=skill)
        current_level_num = progress.current_level.level_number if progress.current_level else 0
    except UserSkillProgress.DoesNotExist:
        progress, _ = UserSkillProgress.objects.get_or_create(user=user, skill=skill)
        current_level_num = 0

    # Find the next level the user is aiming for.
    next_level = Level.objects.filter(
        skill=skill,
        level_number__gt=current_level_num
    ).order_by('level_number').first()

    # If there is no next level, they've maxed out the skill.
    if not next_level:
        return

    # Count the logs and check against the requirement.
    log_count = TaskLog.objects.filter(user=user, task__in=skill.tasks.all()).count()
    
    if log_count >= next_level.requirement_log_count:
        # LEVEL UP!
        progress.current_level = next_level
        progress.save()
        
        # Call the function to create the active buff.
        apply_buff_from_level(user, next_level)

# Function 3: To be used ONLY when a TaskLog is deleted.
def recalculate_skill_level(user, skill):
    """
    Recalculates a user's level from scratch (e.g., after deleting a log)
    and synchronizes all related buffs to match.
    """
    # Count the user's relevant logs for this skill.
    log_count = TaskLog.objects.filter(user=user, task__in=skill.tasks.all()).count()

    # Find the highest level the user now qualifies for.
    new_current_level = None
    for level in skill.levels.order_by('-level_number'):
        if log_count >= level.requirement_log_count:
            new_current_level = level
            break

    # Update the user's skill progress record.
    progress, _ = UserSkillProgress.objects.get_or_create(user=user, skill=skill)
    progress.current_level = new_current_level
    progress.save()

    # Synchronize all buffs for this skill.
    all_buffs_for_skill = Buff.objects.filter(user=user, source_level__skill=skill)
    for buff in all_buffs_for_skill:
        if new_current_level and buff.source_level.level_number <= new_current_level.level_number:
            buff.is_active = True
        else:
            buff.is_active = False
        buff.save()