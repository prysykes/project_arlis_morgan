from django.contrib import admin
from .models import TempTestImagesCSV


class TempTestImagesCSVAdmin(admin.ModelAdmin):
    list_display = ('test_images_file', 'test_csv_file')

admin.site.register(TempTestImagesCSV, TempTestImagesCSVAdmin)

# class TempT (admin.ModelAdmin):
#     list_display = ('user', 'date_created',)
#     search_fields = ['user']


# admin.site.register(Userreg, UserAdmin)

