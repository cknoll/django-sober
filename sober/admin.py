from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Brick, User, Vote, Complaint, SettingsBunch
from .models import SoberUser

admin.site.register(Brick)
admin.site.register(Vote)
admin.site.register(Complaint)
admin.site.register(SettingsBunch)


# Define an inline admin descriptor for SoberUser model
# which acts a bit like a singleton
class SoberUserInline(admin.StackedInline):
    model = SoberUser
    can_delete = False
    verbose_name_plural = 'SoberUsers'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (SoberUserInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
