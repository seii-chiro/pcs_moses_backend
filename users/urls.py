# users/urls.py
from django.urls import path
from .views import MeView, get_all_committees, request_proxy, accept_proxy, reject_proxy, get_all_voters

urlpatterns = [
    path('me/', MeView.as_view(), name='me'),  # Add the route for /me/
    path('voters/', get_all_voters, name='get_all_voters'),
    path('commitees/', get_all_committees, name='get_all_committees'),
    path('me/request-proxy/', request_proxy, name='request-proxy'),
    path('me/accept-proxy/', accept_proxy, name='accept-proxy'),
    path('me/reject-proxy/', reject_proxy, name='reject-proxy'),
]
