from django.shortcuts import render
from django.http import Http404

ESTADOS_VALIDOS = {'ac', 'al', 'ap', 'am', 'ba', 'ce', 'df', 'es', 'go', 'ma', 'mt', 'ms', 'mg',
                   'pa', 'pb', 'pr', 'pe', 'pi', 'rj', 'rn', 'rs', 'ro', 'rr', 'sc', 'sp', 'se', 'to'}

def estado_view(request, sigla):
    sigla = sigla.lower()
    if sigla not in ESTADOS_VALIDOS:
        raise Http404("Estado não encontrado")
    template = f'estados/{sigla}.html'
    return render(request, template, {'sigla': sigla.upper()})
