from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL

WEEKDAYS = [
    (0,'Segunda'),
    (1,'Terça'),
    (2,'Quarta'),
    (3,'Quinta'),
    (4,'Sexta'),
    (5,'Sábado'),
    (6,'Domingo'),
]

class RecurringSlot(models.Model):
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recurring_slots')
    title = models.CharField(max_length=150, blank=True)
    weekday = models.IntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    capacity = models.PositiveIntegerField(default=1)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_weekday_display()} {self.start_time}-{self.end_time} ({self.title})"


class AvailabilitySlot(models.Model):
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability_slots')
    recurring = models.ForeignKey(RecurringSlot, null=True, blank=True, on_delete=models.SET_NULL, related_name='occurrences')
    start = models.DateTimeField()
    end = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start']
        indexes = [models.Index(fields=['tutor','start'])]

    def confirmed_count(self):
        return self.bookings.filter(status='confirmed').count()

    def available_spots(self):
        return max(0, self.capacity - self.confirmed_count())

    def is_full(self):
        return self.available_spots() <= 0

    def __str__(self):
        return f"{self.tutor} {self.start} - {self.end} (cap={self.capacity})"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending','Pending'),
        ('confirmed','Confirmed'),
        ('cancelled','Cancelled'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    slot = models.ForeignKey(AvailabilitySlot, on_delete=models.CASCADE, related_name='bookings')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='confirmed')

    class Meta:
        ordering = ['-created_at']