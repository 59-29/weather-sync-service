from rest_framework import serializers
from .models import CityWeather

class CityWeatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityWeather
        fields = "__all__"
