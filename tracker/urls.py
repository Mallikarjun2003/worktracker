from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('swipe/', views.swipe, name='swipe'),
    path('track/', views.track, name='track'),
    
]
