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

    reference = request.GET.get('ref', 'rcb').lower()
    if(reference != 'cbr' and reference != 'mnr' and reference != 'obr'):
        reference = 'rcb'

    pagina = get_object_or_404(PaginaEstado, estado=sigla_upper)

    tabs = [
        {
            "id": "voluntarios",
            "label": "Auxilie",
            "icon": "group",
            "content": """
                <h3 class="margin-0 margin-b-0/ text-xlarge">Programa de voluntariado</h3>
                <p class="margin-0 text-large">Deseja ser um voluntário em algum evento regional ou estadual? <strong>Entre em contato</strong> com um representante e ajude-nos a democratizar a robótica!</p>
            """
        },
        {
            "id": "invista",
            "label": "Invista",
            "icon": "money",
            "content": """
                <h3 class="margin-0 margin-b-0/ text-xlarge">Invista em eventos de robótica do seu estado!</h3>
                <p class="margin-0 text-large">
                    Deseja investir em uma Regional ou Estadual de algum evento RoboCup Brasil?
                    Entre em contato com um <strong>representante</strong> e ajude-nos a democratizar a robótica!
                </p>
            """
        }
    ]

    context = {
        'sigla': sigla_upper,
        'nome_estado': pagina.get_estado_display(),
        'conteudo': pagina.componentes,
        'reference': reference,
        'tabs': tabs,
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
        try:
            if comp['type'] == 'equipe':
                funcionario_ids = comp.get('funcionarios', []) 
    
                rendered_components.append(render(request, 'components/dynamic/equipe.html', {
                    'titulo': comp.get('titulo', 'Equipe'),
                    'funcionarios': Funcionario.objects.filter(id__in=funcionario_ids)
                }).content.decode())
        except Exception as e:
            rendered_components.append(f"<p>Erro ao renderizar componente: {e}</p>")
        pass

    context = {
        'pagina': pagina,
        'componentes_rendered': rendered_components,
        'header_type': pagina.header_type,
    }
    return render(request, 'base_dynamic.html', context)

def noticia_detail(request, permalink):
    noticia = get_object_or_404(Noticia, permalink=permalink)

    context = {
        'noticia': noticia,
        'header_type': noticia.header_type,
    }

    return render(request, 'news_dynamic.html', context)

from django.shortcuts import render