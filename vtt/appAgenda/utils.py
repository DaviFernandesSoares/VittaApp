from datetime import date, datetime, timedelta
from .models import AvailabilitySlot

def materialize_recurring(recurring, weeks=8):
    """
    Gera AvailabilitySlot para as próximas `weeks` semanas (inclui start_date se fornecido).
    Retorna lista de slots criados.
    """
    today = date.today()
    start_day = recurring.start_date or today
    end_date = start_day + timedelta(weeks=weeks)
    # ajustar cur para o primeiro weekday correto >= start_day
    days_ahead = (recurring.weekday - start_day.weekday()) % 7
    cur = start_day + timedelta(days=days_ahead)
    created = []
    while cur <= end_date:
        if recurring.end_date and cur > recurring.end_date:
            break
        if not recurring.active:
            break
        start_dt = datetime.combine(cur, recurring.start_time)
        end_dt = datetime.combine(cur, recurring.end_time)
        # evitar duplicatas
        exists = AvailabilitySlot.objects.filter(
            tutor=recurring.tutor,
            start=start_dt,
            end=end_dt
        ).exists()
        if not exists:
            slot = AvailabilitySlot.objects.create(
                tutor=recurring.tutor,
                recurring=recurring,
                start=start_dt,
                end=end_dt,
                capacity=recurring.capacity
            )
            created.append(slot)
        cur += timedelta(days=7)
    return created