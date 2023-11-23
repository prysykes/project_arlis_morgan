from django.contrib import admin

from .models import Userreg

class UserAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_created',)
    search_fields = ['user']


admin.site.register(Userreg, UserAdmin)
