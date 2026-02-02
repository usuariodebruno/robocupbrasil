from django.urls import path, re_path
from . import views

urlpatterns = [
    path('estados/<str:sigla>', views.estado_view, name='estado'),

    path('noticias/<int:pk>', views.noticia_detail, name='noticia_detail'),

    re_path(r'^(?P<path>.*)/?$', views.pagina_dinamica_view, name='pagina_dinamica'),
]