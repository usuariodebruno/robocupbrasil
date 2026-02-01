from django.shortcuts import render
from django.http import Http404
from .models import Regiao

def custom_404(request, exception):
    return render(request, '404.html', {
        'exception': exception,
    }, status=404)

def estado_view(request, sigla):
    sigla_upper = sigla.upper()  # RN, SP, etc.

    try:
        regiao = Regiao[sigla_upper]
    except KeyError:
        raise Http404("Estado não encontrado")

    context = {
        'sigla': sigla_upper,
        'nome_estado': regiao.label,
        'bandeira_url': regiao.bandeira,
    }

    return render(request, f'estados/{sigla.lower()}.html', context)

from django.shortcuts import render