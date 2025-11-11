# appAgenda/views.py
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_datetime

from .models import AvailabilitySlot, Booking

def slots_json(request):
    """
    Retorna slots compatíveis com FullCalendar.
    Aceita querystring start, end (ISO datetimes).
    """
    start = request.GET.get('start')
    end = request.GET.get('end')

    qs = AvailabilitySlot.objects.select_related('tutor').all()
    if start:
        try:
            s = parse_datetime(start)
            if s:
                qs = qs.filter(end__gte=s)
        except Exception:
            pass
    if end:
        try:
            e = parse_datetime(end)
            if e:
                qs = qs.filter(start__lte=e)
        except Exception:
            pass

    events = []
    for slot in qs:
        title = f"{getattr(slot.tutor, 'get_full_name', None)() or str(slot.tutor)}"
        events.append({
            'id': f"slot-{slot.pk}",
            'start': slot.start.isoformat(),
            'end': slot.end.isoformat(),
            'title': title,
            'extendedProps': {
                'slot_id': slot.pk,
                'tutor_id': slot.tutor.pk,
                'capacity': slot.capacity,
                'available': slot.available_spots(),
            },
            'color': '#8a4dff' if slot.capacity > 1 else '#4b8cff',
        })
    return JsonResponse(events, safe=False)

@login_required
@require_http_methods(["POST"])
def create_booking(request):
    slot_id = request.POST.get('slot_id')
    if not slot_id:
        return HttpResponseBadRequest("slot_id required")

    slot = get_object_or_404(AvailabilitySlot, pk=slot_id)

    # Não permitir tutor marcar para si próprio
    if request.user.pk == slot.tutor_id:
        return HttpResponseForbidden("Tutors cannot book their own slots")

    try:
        with transaction.atomic():
            slot_locked = AvailabilitySlot.objects.select_for_update().get(pk=slot.pk)
            if slot_locked.is_full():
                return JsonResponse({'ok': False, 'error': 'Slot is full'}, status=400)

            booking = Booking.objects.create(
                student=request.user,
                slot=slot_locked,
                status='confirmed'
            )
            return JsonResponse({'ok': True, 'booking_id': booking.pk})
    except ValidationError as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': 'Internal error'}, status=500)



from django.shortcuts import render

def agenda_view(request):
    return render(request, 'agenda.html')