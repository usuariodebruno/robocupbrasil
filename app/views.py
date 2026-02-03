from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Regiao, Pagina, Funcionario, Arquivo, Data, Noticia, PaginaEstado

def error_view(request, exception=None):
    path = request.path
    
    if exception:
        import django.core.exceptions
        if isinstance(exception, django.core.exceptions.PermissionDenied):
            status_code = 403
        else:
            status_code = 404
    else:
        status_code = 500

    return render(request, 'error.html', {
        'status_code': status_code,
        'path': path,
        'exception': exception,
    }, status=status_code)

def estado_view(request, sigla):
    sigla_upper = sigla.upper()
    if sigla_upper not in [choice[0] for choice in Regiao.choices]:
        raise Http404("Estado não encontrado")

    pagina = get_object_or_404(PaginaEstado, estado=sigla_upper)

    context = {
        'sigla': sigla_upper,
        'nome_estado': pagina.get_estado_display(),
        'bandeira': pagina.bandeira,
        'texto': pagina.texto,
    }
    return render(request, 'estado.html', context)

def pagina_dinamica_view(request, path):
    path = path.strip('/')

    if not path:
        try:
            pagina = Pagina.objects.get(slug='')
        except Pagina.DoesNotExist:
            raise Http404("Página inicial não encontrada. Crie uma página com slug vazio.")
    else:
        slugs = path.split('/')
        pagina = None
        for slug in slugs:
            if slug:
                pagina = get_object_or_404(Pagina, slug=slug, parent=pagina)

    rendered_components = []
    for comp in pagina.componentes:
        pass

    context = {
        'pagina': pagina,
        'componentes_rendered': rendered_components,
        'header_type': pagina.header_type,
    }
    return render(request, 'base_dynamic.html', context)

def noticia_detail(request, pk):
    noticia = get_object_or_404(Noticia, pk=pk)

    context = {
        'noticia': noticia,
        'header_type': noticia.header_type,
    }

    return render(request, 'news_dynamic.html', context)

from django.shortcuts import render