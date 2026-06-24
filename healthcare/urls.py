from django.urls import path

from . import views

app_name = 'healthcare'

urlpatterns = [
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/book/', views.appointment_create, name='appointment_create'),
    path('appointments/<int:pk>/confirm/', views.appointment_confirm, name='appointment_confirm'),
    path('records/', views.record_list, name='record_list'),
    path('records/add/', views.record_create, name='record_create'),
    path('records/add/<int:appointment_pk>/', views.record_create, name='record_create_for_appointment'),
    path('symptom-check/', views.symptom_check, name='symptom_check'),
]