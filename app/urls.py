from django.urls import path
from django.views.generic import TemplateView, RedirectView
from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='public/index.html'), name='index'),

    # Robotica
    path('robotica/', TemplateView.as_view(template_name='public/robotica.html'), name='robotica'),
    path('robotica/edicoes/', TemplateView.as_view(template_name='public/robotica/edicoes.html')),
    path('robotica/participantes/', TemplateView.as_view(template_name='public/robotica/participantes.html')),

    # Gerais
    path('participe/', TemplateView.as_view(template_name='public/participe.html')),
    path('voluntarios/', TemplateView.as_view(template_name='public/voluntarios.html')),
    path('sobre/', TemplateView.as_view(template_name='public/sobre.html')),
    path('invista/', TemplateView.as_view(template_name='public/invista.html')),
    path('material-de-divulgacao/', TemplateView.as_view(template_name='public/material-de-divulgacao.html')),
    path('associados/', TemplateView.as_view(template_name='public/associados.html')),
    path('noticias/', TemplateView.as_view(template_name='public/noticias.html'), name='noticias'),
    path('todas-as-noticias/', TemplateView.as_view(template_name='public/todas-as-noticias.html')),
    path('contato/', TemplateView.as_view(template_name='public/contato.html')),

    # Estados
    path('<str:sigla>/', views.estado_view, name='estado'),

    # OBR
    path('obr/', TemplateView.as_view(template_name='public/obr.html'), name='obr'),
    path('obr/sobre/', TemplateView.as_view(template_name='public/obr/sobre.html')),
    path('obr/mundo-robotica/', TemplateView.as_view(template_name='public/obr/mundo-robotica.html')),
    path('obr/manuais/', TemplateView.as_view(template_name='public/obr/manuais.html')),
    path('obr/modalidade-teorica/', TemplateView.as_view(template_name='public/obr/modalidade-teorica.html')),
    path('obr/modalidades-praticas/', TemplateView.as_view(template_name='public/obr/modalidades-praticas.html')),
    path('obr/participante/', TemplateView.as_view(template_name='public/obr/participante.html')),
    path('obr/noticias/', TemplateView.as_view(template_name='public/obr/noticias.html'), name='obr-noticias'),
    path('obr/resultados/', RedirectView.as_view(url='https://robocup.org.br/wiki/doku.php', permanent=False)),
    path('obr/faq/', TemplateView.as_view(template_name='public/obr/faq.html')),

    # CBR
    path('cbr/', TemplateView.as_view(template_name='public/cbr.html'), name='cbr'),
    path('cbr/noticias/', TemplateView.as_view(template_name='public/cbr/noticias.html'), name='cbr-noticias'),
    path('cbr/sobre/', TemplateView.as_view(template_name='public/cbr/sobre.html')),
    path('cbr/ligas/', TemplateView.as_view(template_name='public/cbr/ligas.html')),
    path('cbr/tdp/', TemplateView.as_view(template_name='public/cbr/tdp.html')),
    path('cbr/pagamentos/', TemplateView.as_view(template_name='public/cbr/pagamentos.html')),
    path('cbr/resultados/', RedirectView.as_view(url='https://robocup.org.br/wiki/doku.php', permanent=False)),

    # MNR
    path('mnr/', TemplateView.as_view(template_name='public/mnr.html'), name='mnr'),
    path('mnr/noticias/', TemplateView.as_view(template_name='public/mnr/noticias.html'), name='mnr-noticias'),
    path('mnr/sobre/', TemplateView.as_view(template_name='public/mnr/sobre.html')),
    path('mnr/documentos/', TemplateView.as_view(template_name='public/mnr/documentos.html')),
    path('mnr/anais/', TemplateView.as_view(template_name='public/mnr/anais.html')),
    path('mnr/bolsista/', TemplateView.as_view(template_name='public/mnr/bolsista.html')),
    path('mnr/avaliador/', TemplateView.as_view(template_name='public/mnr/avaliador.html')),
    path('mnr/resultados/', RedirectView.as_view(url='/mnr/anais/', permanent=False)),
]
