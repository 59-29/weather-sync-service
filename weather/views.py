from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import CityWeather
from .serializers import CityWeatherSerializer
from .tasks import sync_weather

@api_view(["POST"])
def trigger_sync(request):
    task = sync_weather.delay()
    return Response(
        {"task_id": task.id, "status": "started"},
        status=status.HTTP_202_ACCEPTED,
    )

class WeatherList(ListAPIView):
    queryset = CityWeather.objects.all().order_by("id")
    serializer_class = CityWeatherSerializer

class WeatherDetail(RetrieveAPIView):
    queryset = CityWeather.objects.all()
    serializer_class = CityWeatherSerializer
