from django.contrib import admin

from .models import Brick, User, Vote, Complaint, SettingsBunch

admin.site.register(Brick)
admin.site.register(User)
admin.site.register(Vote)
admin.site.register(Complaint)
admin.site.register(SettingsBunch)
