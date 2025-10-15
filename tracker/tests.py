from django.test import TestCase
from django.utils import timezone
from .models import Swipe
from .utils import compute_stats_for_card


class PairingTests(TestCase):
    def setUp(self):
        Swipe.objects.all().delete()

    def test_normal_day_pairs(self):
        now = timezone.localtime()
        card = 'T1'
        Swipe.objects.create(card_no=card, reader_name='Main Door - IN', time=now.replace(hour=9, minute=0, second=0, microsecond=0))
        Swipe.objects.create(card_no=card, reader_name='Main Door - OUT', time=now.replace(hour=12, minute=30, second=0, microsecond=0))
        Swipe.objects.create(card_no=card, reader_name='Main Door - IN', time=now.replace(hour=13, minute=30, second=0, microsecond=0))
        Swipe.objects.create(card_no=card, reader_name='Main Door - OUT', time=now.replace(hour=18, minute=0, second=0, microsecond=0))
        stats = compute_stats_for_card(card)
        self.assertEqual(len(stats['per_day']), 1)
        self.assertEqual(stats['per_day'][0]['worked_minutes'], 480)

    def test_mis_swipe_replace_in(self):
        now = timezone.localtime()
        card = 'T2'
        Swipe.objects.create(card_no=card, reader_name='Main Door - IN', time=now.replace(hour=8, minute=50, microsecond=0))
        Swipe.objects.create(card_no=card, reader_name='Main Door - IN', time=now.replace(hour=9, minute=5, microsecond=0))
        Swipe.objects.create(card_no=card, reader_name='Main Door - OUT', time=now.replace(hour=17, minute=0, microsecond=0))
        stats = compute_stats_for_card(card)
        # used second IN (9:05) to OUT 17:00 => 7h55m = 475
        self.assertEqual(stats['per_day'][0]['worked_minutes'], 475)

    def test_unmatched_out_ignored(self):
        now = timezone.localtime()
        card = 'T3'
        Swipe.objects.create(card_no=card, reader_name='Main Door - OUT', time=now.replace(hour=8, minute=0, microsecond=0))
        Swipe.objects.create(card_no=card, reader_name='Main Door - IN', time=now.replace(hour=9, minute=0, microsecond=0))
        Swipe.objects.create(card_no=card, reader_name='Main Door - OUT', time=now.replace(hour=17, minute=0, microsecond=0))
        stats = compute_stats_for_card(card)
        # should pair 9:00 - 17:00 => 480
        self.assertEqual(stats['per_day'][0]['worked_minutes'], 480)
