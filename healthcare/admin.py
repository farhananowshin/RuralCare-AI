from django.contrib import admin

from .models import Appointment, MedicalRecord, SymptomCheck


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'scheduled_for', 'status')
    list_filter = ('status', 'scheduled_for')
    search_fields = ('patient__user__username', 'doctor__user__username')


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'diagnosis', 'created_at')
    search_fields = ('diagnosis', 'patient__user__username')


@admin.register(SymptomCheck)
class SymptomCheckAdmin(admin.ModelAdmin):
    list_display = ('patient', 'created_at', 'symptoms')
    search_fields = ('symptoms', 'patient__user__username')
