import os
from django.conf import settings
from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import SimpleRouter, DefaultRouter
from django.conf.urls.static import static
from django.views.static import serve

router = SimpleRouter()


if settings.ENABLE_FRONTEND_HELPER:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FLUTTER_WEB_APP = os.path.join(BASE_DIR, 'frontend_helper', 'templates', 'frontend_helper', 'web')
def flutter_redirect(request, resource):
    return serve(request, resource, FLUTTER_WEB_APP)
urlpatterns = [
    path('frontend_helper/', lambda r: flutter_redirect(r, 'index.html')),
    path('frontend_helper/<path:resource>', flutter_redirect),
    path('api/csrf_cookie/', views.GetCSRFToken.as_view()),
    path('api/frontend_updater/',views.ProductionFrontEndUpdater.as_view()),
    path('api/frontend_server_status/',views.ProductionServerStatus.as_view()),
    path('api/frontend_server_backups/',views.ProductionBackupManage.as_view()),
    path('api/manage_whitelist/',views.UFWManager.as_view()),
    path('api/dj-login/', views.UserLogin.as_view()),
    path('api/my_account/', views.ClassMyProfile.as_view()),

]
# Include the router's URLs
urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
