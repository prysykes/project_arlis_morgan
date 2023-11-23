from django.contrib import admin
from .models import NLPCSV



class NLPCSVAdmin(admin.ModelAdmin):
    list_display = ('uploaded_nlp_csv',)


admin.site.register(NLPCSV, NLPCSVAdmin)

# class TempT (admin.ModelAdmin):
#     list_display = ('user', 'date_created',)
#     search_fields = ['user']


# admin.site.register(Userreg, UserAdmin)

