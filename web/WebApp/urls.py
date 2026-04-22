from django.urls import path
from WebApp import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.home,name="Home"),
    path('tienda/', views.tienda,name="tienda"),
    path('offline/', views.offline, name="offline"),
    path('manifest.webmanifest', views.manifest, name="manifest"),
    path('service-worker.js', views.service_worker, name="service_worker"),
]

urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
