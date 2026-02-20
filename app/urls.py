from django.urls import path, re_path
from . import views

urlpatterns = [
    path('estado/<str:sigla>', views.estado_view, name='estado'),
    path('noticia/<str:permalink>', views.noticia_detail, name='noticia_detail'),
    path('sede/<str:ano>', views.sede_view, name='sede'),
    path('evento/<str:permalink>', views.subevento_view, name='evento'),

    re_path(r'^(?P<path>.*)/?$', views.pagina_dinamica_view, name='pagina_dinamica'),
]