from django.shortcuts import render, redirect
from django.utils import timezone
from django.urls import reverse
from .models import Swipe
from .utils import compute_stats_for_card
from django.db import DatabaseError
from django.http import HttpResponse

def index(request):
    return render(request, 'index.html', {})
def swipe(request):
    if request.method == 'POST':
        card_no = request.POST.get('card_no', 'USER1').strip() or 'USER1'
        action = request.POST.get('action')
        # validate action
        if action not in ('IN', 'OUT'):
            return HttpResponse('Invalid action', status=400)
        reader = 'Main Door - IN' if action == 'IN' else 'Main Door - OUT'
        # create swipe — catch DB errors to avoid 500s during dev
        try:
            Swipe.objects.create(card_no=card_no, reader_name=reader, time=timezone.now())
        except DatabaseError:
            return HttpResponse('Database not ready. Please run migrations (manage.py migrate).', status=503)
        # redirect to track page with card_no so user sees their stats immediately
        url = reverse('track') + f'?card_no={card_no}&ok=1'
        return redirect(url)
    return redirect('index')


def track(request):
    card_no = request.GET.get('card_no', 'USER1')

    stats = compute_stats_for_card(card_no)
    return render(request, 'track.html', {'card_no': card_no, 'stats': stats})
