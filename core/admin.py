from django.contrib import admin
from .models import Case, Task, Document, Payment, Profile

# Register models
admin.site.register(Case)
admin.site.register(Task)
admin.site.register(Document)
admin.site.register(Payment)
admin.site.register(Profile)