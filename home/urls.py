from django.contrib import admin
from django.urls import path
from home import views
urlpatterns = [
    path("", views.index, name="home"),
    path('about/', views.about, name="about"),
    path('services/', views.services, name="services"),
    path('contacts/', views.contacts, name="contacts"),

    path('mcq/', views.mcq, name="mcq"),
    path('summary/', views.summarizer, name="summarizer"),
    path('tutorial/', views.tutorials, name="tutorials"),
    path('quiz/', views.quiz, name="quiz"),
    path('pricing/', views.pricing, name="pricing"),
]
