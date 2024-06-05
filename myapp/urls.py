
from django.urls import path
from .views import process_data
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('process/', views.process, name='process'),
    path('service_result/', views.service_result, name='service_result'),
    path('service_no_result/', views.service_no_result, name='service_no_result'),
]