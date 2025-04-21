# users/urls.py
from django.urls import path
from .views import create_vote, accept_requested_proxy, get_my_proxied_users, remove_proxy_assignments

urlpatterns = [
    path('start-vote/', create_vote, name='start-vote'),
    path('accept-proxy-request/', accept_requested_proxy, name='accept-proxy-request'),
    path('get-my-proxied-user/', get_my_proxied_users, name='get-my-proxied-users'),
    path('remove-proxy-assignment/', remove_proxy_assignments, name='remove-proxy-assignments')
]
