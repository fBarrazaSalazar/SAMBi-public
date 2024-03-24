from django.contrib import admin
from .models import User,Face,Person,Finger,Logs,Voice

admin.site.register(User)
admin.site.register(Face)
admin.site.register(Person)
admin.site.register(Finger)
admin.site.register(Logs)
admin.site.register(Voice)

# Register your models here.
