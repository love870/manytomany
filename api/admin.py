from django.contrib import admin

from secret.models import AddStudent
from .models import *
# Register your models here.

admin.site.register(Timezones)
admin.site.register(Roles)
admin.site.register(Profile)
admin.site.register(AddStudent)



