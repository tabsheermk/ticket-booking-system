from django.db import models
from django.conf import settings 

class Movie(models.Model):
    title = models.CharField(max_length=255)
    duration_minutes = models.IntegerField()

class Show(models.Model):
    movie = models.ForeignKey("Movie", on_delete=models.DO_NOTHING)
    screen_name = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    total_seats = models.IntegerField()

class Booking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING
    )
    show = models.ForeignKey("Show", on_delete=models.DO_NOTHING)
    seat_number = models.IntegerField()
    status = models.CharField(max_length=12)
    created_at = models.DateTimeField()
