from django.contrib import admin

from .models import Doctor, Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'village', 'phone', 'date_of_birth', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'village')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'clinic_name', 'license_number')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialty', 'clinic_name')
