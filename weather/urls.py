from django.urls import path
from .views import trigger_sync, WeatherList, WeatherDetail

urlpatterns = [
    path("sync/", trigger_sync),
    path("weather/", WeatherList.as_view()),
    path("weather/<int:pk>/", WeatherDetail.as_view()),
]
