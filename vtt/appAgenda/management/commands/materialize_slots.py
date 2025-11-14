# appAgenda/management/commands/materialize_slots.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from appAgenda.models import RecurringSlot
from appAgenda.utils import materialize_recurring_slot

class Command(BaseCommand):
    help = "Gera AvailabilitySlot a partir de RecurringSlot nos próximos N dias"

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=56, help='Quantos dias à frente gerar (padrão 56 ~ 8 semanas)')
        parser.add_argument('--tutor', type=int, default=None, help='Gerar apenas para tutor id')

    def handle(self, *args, **options):
        days = options['days']
        tutor_id = options['tutor']
        from_date = date.today()
        to_date = from_date + timedelta(days=days)
        qs = RecurringSlot.objects.filter(active=True)
        if tutor_id:
            qs = qs.filter(tutor_id=tutor_id)
        total = 0
        for rec in qs:
            created = materialize_recurring_slot(rec, from_date, to_date)
            total += len(created)
            self.stdout.write(f"Rec {rec.pk}: {len(created)} slots")
        self.stdout.write(self.style.SUCCESS(f"Total slots criados: {total}"))