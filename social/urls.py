from django.urls import path

from . import views

app_name = 'social'
urlpatterns = [
    path('timeline/', views.timeline, name='timeline'),
]