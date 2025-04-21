# users/urls.py
from django.urls import path
from .views import create_vote

urlpatterns = [
    path('vote/', create_vote, name='vote'),

]
