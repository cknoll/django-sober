from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group

from .models import Brick, Vote, Complaint, SettingsBunch
from .models import SoberUser, SoberGroup

admin.site.register(Brick)
admin.site.register(Vote)
admin.site.register(Complaint)
admin.site.register(SettingsBunch)


# Define an inline admin descriptor for SoberUser model
# which acts a bit like a singleton
class SoberUserInline(admin.StackedInline):
    model = SoberUser
    can_delete = False
    verbose_name_plural = "SoberUsers"


# noinspection PyClassHasNoInit
# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (SoberUserInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# Define an inline admin descriptor for SoberGroup model
class SoberGroupInline(admin.StackedInline):
    model = SoberGroup
    can_delete = False
    verbose_name_plural = "SoberGroups"


# noinspection PyClassHasNoInit
# Define a new Group admin
class GroupAdmin(BaseGroupAdmin):
    inlines = (SoberGroupInline,)


# Re-register GroupAdmin
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
