from django.urls import path, re_path
from . import views

urlpatterns = [
    path('estado/<str:sigla>', views.estado_view, name='estado'),

    path('noticia/<int:pk>', views.noticia_detail, name='noticia_detail'),

    re_path(r'^(?P<path>.*)/?$', views.pagina_dinamica_view, name='pagina_dinamica'),
]