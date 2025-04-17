from django.urls import path
from .views import get_person, create_person, person_detail, create_user, login_user, logout_user


urlpatterns = [
    path('person/', get_person, name='get_person'),
    path('person/create_person/', create_person, name="create_person"),
    path('person/<int:pk>/', person_detail, name="person_detail"),
    path('person/create_user/', create_user, name="create_person"),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
]