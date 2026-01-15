from django.db import models

# Create your models here.

class CityWeather(models.Model):
    city_name = models.CharField(max_length=64, unique=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=4)
    longitude = models.DecimalField(max_digits=9, decimal_places=4)

    temperature = models.FloatField(null=True, blank=True)
    windspeed = models.FloatField(null=True, blank=True)
    winddirection = models.FloatField(null=True, blank=True)
    weathercode = models.IntegerField(null=True, blank=True)
    weather_time = models.DateTimeField(null=True, blank=True)

    raw_payload = models.JSONField(null=True, blank=True)
    synced_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.city_name
