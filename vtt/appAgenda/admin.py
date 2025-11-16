# appAgenda/admin.py
from django.contrib import admin
from .models import AvailabilitySlot, Booking

@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'start', 'end', 'capacity', 'created_at')
    list_filter = ('tutor',)
    search_fields = ('tutor__username', 'tutor__email')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('student', 'slot', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('student__username', 'student__email')

