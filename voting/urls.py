# users/urls.py
from django.urls import path
from .views import (
    candidate_vote_summary, casted_ballot_summary, create_vote,
    request_proxy_access, accept_requested_proxy,
    get_my_proxied_users, remove_proxy_assignments,
    set_started_vote,
)

urlpatterns = [
    path('start-vote/', create_vote, name='start-vote'),
    path('accept-proxy-request/', accept_requested_proxy, name='accept-proxy-request'),
    path('get-my-proxied-user/', get_my_proxied_users, name='get-my-proxied-users'),
    path('remove-proxy-assignment/', remove_proxy_assignments, name='remove-proxy-assignments'),
    path('request-proxy/', request_proxy_access, name='request-proxy'),
    path('vote-summary/', candidate_vote_summary, name='vote-summary'),
    path('casted-ballot-summary/', casted_ballot_summary, name='casted-ballot-summary'),
    path('set-started-voting/', set_started_vote, name='set-started-voting'),
]
