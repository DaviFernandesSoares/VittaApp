from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.db import transaction

from .models import RecurringSlot, AvailabilitySlot, Booking
from .forms import RecurringSlotForm, AvailabilitySlotForm
from .utils import materialize_recurring

@login_required
def tutor_panel(request):
    return render(request, 'agenda.html', {})

@login_required
@require_http_methods(["POST"])
def create_recurring(request):
    form = RecurringSlotForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
    rec = form.save(commit=False)
    rec.tutor = request.user
    rec.save()
    # materializar próximas 8 semanas para UX imediato
    materialize_recurring(rec, weeks=8)
    return JsonResponse({'ok': True, 'id': rec.pk})

def slots_json(request):
    """
    Retorna AvailabilitySlot como eventos FullCalendar.
    Aceita ?tutor=<id> e start/end params do FullCalendar.
    """
    qs = AvailabilitySlot.objects.select_related('tutor','recurring').all()
    tutor_id = request.GET.get('tutor')
    if tutor_id:
        qs = qs.filter(tutor_id=tutor_id)
    start = request.GET.get('start')
    end = request.GET.get('end')
    if start:
        s = parse_datetime(start)
        if s:
            qs = qs.filter(end__gte=s)
    if end:
        e = parse_datetime(end)
        if e:
            qs = qs.filter(start__lte=e)
    events = []
    for slot in qs:
        title = slot.recurring.title if slot.recurring and slot.recurring.title else (getattr(slot.tutor,'get_full_name',None)() or str(slot.tutor))
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
                'is_recurring': bool(slot.recurring),
            },
            'color': '#8a4dff' if slot.capacity>1 else '#4b8cff'
        })
    return JsonResponse(events, safe=False)

@login_required
@require_http_methods(["POST"])
def create_booking(request):
    slot_id = request.POST.get('slot_id')
    if not slot_id:
        return HttpResponseBadRequest('slot_id required')
    slot = get_object_or_404(AvailabilitySlot, pk=slot_id)
    if request.user.pk == slot.tutor_id:
        return HttpResponseForbidden('Tutors cannot book own slots')
    # proteção contra oversell
    try:
        with transaction.atomic():
            slot_locked = AvailabilitySlot.objects.select_for_update().get(pk=slot.pk)
            if slot_locked.is_full():
                return JsonResponse({'ok': False, 'error': 'Slot está lotado'}, status=400)
            booking = Booking.objects.create(student=request.user, slot=slot_locked, status='confirmed')
            return JsonResponse({'ok': True, 'booking_id': booking.pk})
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Erro interno'}, status=500)

