from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'phone_number', 'email_verified', 'phone_verified')
    search_fields = ('username', 'email', 'phone_number')
