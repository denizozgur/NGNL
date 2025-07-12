from django.contrib import admin
from .models import Task, Skill, Level, UserSkillProgress, TaskLog, Buff

admin.site.register(Task)
admin.site.register(Skill)
admin.site.register(Level)
admin.site.register(Buff)   
admin.site.register(UserSkillProgress)
admin.site.register(TaskLog)
