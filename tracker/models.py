from django.db import models
class Swipe(models.Model):
    CARD_CHOICES = (
        ('Main Door - IN', 'Main Door - IN'),
        ('Main Door - OUT', 'Main Door - OUT'),
    )
    card_no = models.CharField(max_length=50, default='USER1')
    reader_name = models.CharField(max_length=32, choices=CARD_CHOICES)
    # allow explicit timestamps (auto_now_add prevented setting custom times)
    time = models.DateTimeField()
    def __str__(self):
        return f"{self.card_no} {self.reader_name} @ {self.time}"
