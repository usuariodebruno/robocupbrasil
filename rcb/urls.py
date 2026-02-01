from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Administração RoboCup Brasil"
admin.site.site_title = "Admin RCB"
admin.site.index_title = "Painel de Controle - RoboCup Brasil"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
]

handler404 = 'app.views.custom_404'

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)