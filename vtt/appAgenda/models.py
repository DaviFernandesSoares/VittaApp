# appAgenda/models.py
from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL

class AvailabilitySlot(models.Model):
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability_slots')
    start = models.DateTimeField()
    end = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=1)  # >1 = turma (várias vagas)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start']
        indexes = [models.Index(fields=['tutor', 'start'])]

    def clean(self):
        if self.end <= self.start:
            raise ValidationError("End must be after start")

    def confirmed_count(self):
        return self.bookings.filter(status='confirmed').count()

    def available_spots(self):
        return max(0, self.capacity - self.confirmed_count())

    def is_full(self):
        return self.available_spots() <= 0

    def __str__(self):
        return f"{self.tutor} — {self.start.isoformat()}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    slot = models.ForeignKey(AvailabilitySlot, on_delete=models.CASCADE, related_name='bookings')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='confirmed')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} -> {self.slot} ({self.status})"