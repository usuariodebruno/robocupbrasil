from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from app import views

admin.site.site_header = "Painel Administrativo | RoboCup Brasil"
admin.site.site_title = "Histórico | RoboCup Brasil"
admin.site.index_title = "Painel de Controle - RoboCup Brasil"

urlpatterns = [
    path('admin/app/', RedirectView.as_view(url='/admin/')),
    path('admin/admin/', RedirectView.as_view(url='/admin/')),
    path('admin/', admin.site.urls),
    path('estados/<str:sigla>', views.estado_view, name='estado'),
    path('noticias/<int:pk>', views.noticia_detail, name='noticia_detail'),

    re_path(r'^(?!(media|static|admin)/)(?P<path>.*)/?$', views.pagina_dinamica_view, name='pagina_dinamica'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler403 = 'app.views.error_view'
handler404 = 'app.views.error_view'
handler500 = 'app.views.error_view'