from django.contrib import admin
from .models import CustomUser

# Register the CustomUser model to make it available in the Django admin
admin.site.register(CustomUser)
