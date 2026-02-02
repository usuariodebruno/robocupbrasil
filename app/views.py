from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Regiao, Pagina, Funcionario, Arquivo, Data, Noticia, PaginaEstado

def custom_404(request, exception):
    return render(request, '404.html', {
        'exception': exception,
    }, status=404)

def estado_view(request, sigla):
    sigla_upper = sigla.upper()
    # Valida se estado existe
    if sigla_upper not in [choice[0] for choice in Regiao.choices]:
        raise Http404("Estado não encontrado")

    # Pega a página do estado (cria se não existir, ou deixa 404)
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
        # ... lógica de render por type (equipe, calendario, etc.)
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
        'header_type': noticia.header_type,  # passa para o template decidir o header
    }

    return render(request, 'news_dynamic.html', context)

from django.shortcuts import render