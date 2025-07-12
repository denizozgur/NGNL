from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    class TaskType(models.TextChoices):
        RECURRING = 'RECURRING', 'Recurring'
        ONE_TIME = 'ONE_TIME', 'One-Time'

    class Priority(models.IntegerChoices):
        LOW = 1, 'Low'
        MEDIUM = 2, 'Medium'
        HIGH = 3, 'High'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    parent_task = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='subtasks' 
    )
    task_type = models.CharField(max_length=10, choices=TaskType.choices, default=TaskType.RECURRING)
    display_order = models.IntegerField(default=0)
    priority = models.IntegerField(default=0) 
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This ensures the tasks are ordered by our new field by default
        ordering = ['display_order']

    def __str__(self):
        return self.name


class Skill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    # A skill can be improved by completing one or more tasks
    tasks = models.ManyToManyField(Task, related_name='skills')

    def __str__(self):
        return self.name



class Level(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='levels')
    level_number = models.PositiveIntegerField()
    requirement_description = models.CharField(max_length=255, help_text="Human-readable rule, e.g., 'Log meditation 3 times.'")
    
    requirement_log_count = models.PositiveIntegerField(default=1, help_text="How many total logs are needed to reach this level.")
    
    benefits_description = models.CharField(max_length=255, help_text="Short description of the buff/reward.")
    
    class Meta:
        unique_together = ('skill', 'level_number')
        ordering = ['level_number']

    def __str__(self):
        return f"{self.skill.name} - Level {self.level_number}"


class Buff(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buffs')
    name = models.CharField(max_length=100)
    description = models.TextField()
    source_level = models.ForeignKey(Level, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} for {self.user.username} (Active: {self.is_active})"


###### This model tracks the user's progress 
class UserSkillProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    current_level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)
    xp = models.IntegerField(default=0, help_text="Experience points towards the next level.")
    streak = models.IntegerField(default=0, help_text="Consecutive days the skill's tasks were completed.")

    class Meta:
        unique_together = ('user', 'skill')

    def __str__(self):
        return f"{self.user.username}'s progress in {self.skill.name}"



class TaskLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} logged {self.task.name} at {self.timestamp}"