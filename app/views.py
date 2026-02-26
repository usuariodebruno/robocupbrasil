from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse
from .models import Regiao, Pagina, Funcionario, Arquivo, Data, Noticia, PaginaEstado, Sede, Subevento
from django.views.decorators.cache import cache_page

import json
from .utils.render_components import render_components_to_html

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


def component_preview(request):
    """Utility endpoint used by the admin component builder to render a
    live preview of a components JSON structure.  Accepts a ``json``
    query parameter and returns the HTML produced by
    ``render_components_to_html``.  The view is deliberately simple and
    does not perform any permissions checks since the JSON comes from the
    same user who is editing the page.  If the payload fails to parse we
    fall back to an empty list.
    """
    data = request.GET.get('json', '[]')
    try:
        comps = json.loads(data)
    except Exception:
        comps = []
    html = render_components_to_html(comps)

    # allow caller to request a specific page header type for the preview
    header = request.GET.get('header', '')
    header_lower = header.lower() if header else 'rcb'
    # normalize allowed values (rcb, cbr, mnr, obr)
    if header_lower not in ('rcb', 'cbr', 'mnr', 'obr'):
        header_lower = 'rcb'

    return render(request, 'component_preview.html', {'html': html, 'header_type_lower': header_lower})

# Essa página eventualmente será excluída, mas por ora serve como exemplo de renderização de componentes dinâmicos
@cache_page(60 * 60 * 24 * 7)
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
            "content": "<h3 class=\"margin-0 margin-b-1 text-xlarge\">Programa de voluntariado</h3><p class=\"margin-0 text-large\">Deseja ser um voluntário em algum evento regional ou estadual? <strong>Entre em contato</strong> com um representante e ajude-nos a democratizar a robótica!</p>"
        },
        {
            "id": "invista",
            "label": "Invista",
            "icon": "money",
            "content": "<h3 class=\"margin-0 margin-b-1 text-xlarge\">Invista em eventos de robótica do seu estado!</h3><p class=\"margin-0 text-large\">Deseja investir em uma Regional ou Estadual de algum evento RoboCup Brasil? Entre em contato com um <strong>representante</strong> e ajude-nos a democratizar a robótica!</p>"
        }
    ]

    funcionarios = Funcionario.get_items(tag_ids=[10])
    # pagination params for files and news (começar em 0)
    try:
        file_page = int(request.GET.get('file_page', 0))
    except (ValueError, TypeError):
        file_page = 0

    try:
        news_page = int(request.GET.get('news_page', 0))
    except (ValueError, TypeError):
        news_page = 0

    sedes = Sede.get_items(tag_ids=[])
    subeventos = Subevento.get_items(tag_ids=[])
    arquivos = Arquivo.get_items(tag_ids=[], page_index=file_page)
    noticias = Noticia.get_items(tag_ids=[], page_index=news_page)

    from datetime import date
    datas = list(Data.objects.filter(data__gte=date.today()).order_by('data')[:50])

    context = {
        'sigla': sigla_upper,
        'nome_estado': pagina.get_estado_display(),
        'conteudo': pagina.componentes,
        'conteudo_html': getattr(pagina, 'componentes_html', ''),
        'reference': reference,
        'tabs': tabs,
        'funcionarios': funcionarios,
        'sedes': sedes,
        'subeventos': subeventos,
        'arquivos': arquivos,
        'arquivo': arquivos[0] if arquivos else None,
        'noticias': noticias,
        'datas': datas,
        'imagem_estado': f"/static/images/estados/{sigla_upper.lower()}.png",
    }
    return render(request, 'estado.html', context)

@cache_page(60 * 60 * 24 * 7)
def subevento_view(request, permalink):
    subevento = get_object_or_404(Subevento, permalink=permalink)

    reference = request.GET.get('ref', 'rcb').lower()
    if(reference != 'cbr' and reference != 'mnr' and reference != 'obr'):
        reference = 'rcb'

    context = {
        'subevento': subevento,
        'conteudo': subevento.componentes,
        'conteudo_html': getattr(subevento, 'componentes_html', ''),
        'reference': reference,
    }
    return render(request, 'subevento.html', context)

@cache_page(60 * 60 * 24 * 7)
def sede_view(request, ano):
    sede = get_object_or_404(Sede, ano=ano)

    reference = request.GET.get('ref', 'rcb').lower()
    if(reference != 'cbr' and reference != 'mnr' and reference != 'obr'):
        reference = 'rcb'

    context = {
        'sede': sede,
        'conteudo': sede.componentes,
        'conteudo_html': getattr(sede, 'componentes_html', ''),
        'reference': reference,
    }
    return render(request, 'sede.html', context)

@cache_page(60 * 60 * 24 * 7)
def pagina_dinamica_view(request, path):
    path = path.strip('/')
    # reserved paths that should not be treated as pages
    if path in ('component-preview',):
        raise Http404()

    # Query params for pagination

    try:
        file_page = int(request.GET.get('file_page', 0))
    except (ValueError, TypeError):
        file_page = 0

    try:
        news_page = int(request.GET.get('news_page', 0))
    except (ValueError, TypeError):
        news_page = 0
    
    # ------------------

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

    # prepare the same queries that estado_view uses so components can
    # reference them by name
    funcionarios = Funcionario.get_items(tag_ids=[10])
    sedes = Sede.get_items(tag_ids=[])
    subeventos = Subevento.get_items(tag_ids=[])

    # pagination params (unused here but available if components need them)
    try:
        file_page = int(request.GET.get('file_page', 0))
    except (ValueError, TypeError):
        file_page = 0
    try:
        news_page = int(request.GET.get('news_page', 0))
    except (ValueError, TypeError):
        news_page = 0

    arquivos = Arquivo.get_items(tag_ids=[], page_index=file_page)
    noticias = Noticia.get_items(tag_ids=[], page_index=news_page)
    from datetime import date
    datas = list(Data.objects.filter(data__gte=date.today()).order_by('data')[:50])

    arquivo_obj = arquivos[0] if arquivos else None
    # build context for dynamic components; include a few convenience
    # aliases used in the example JSON so users don't have to guess the
    # correct name.
    extra = {
        'funcionarios': funcionarios,
        'sedes': sedes,
        'subeventos': subeventos,
        'arquivos': arquivos,
        'noticias': noticias,
        'datas': datas,
        'arquivo': arquivo_obj,
        # aliases matching the example JSON we shipped
        'arquivos_exemplo': arquivos,
        'noticias_exemplo': noticias,
        'datas_exemplo': datas,
    }

    from .utils.render_components import render_components_to_html
    rendered = render_components_to_html(pagina.componentes or [], extra)

    context = {
        'pagina': pagina,
        'header_type': pagina.header_type,
        # keep the entire rendered HTML as one item so the template loop
        # simply dumps it
        'componentes_rendered': [rendered],
        'conteudo_html': getattr(pagina, 'componentes_html', ''),
    }
    return render(request, 'base_dynamic.html', context)

@cache_page(60 * 60 * 24 * 7)
def noticia_detail(request, permalink):
    noticia = get_object_or_404(Noticia, permalink=permalink)

    # 1. Determinar variáveis condicionais baseadas no header_type
    header_type = noticia.header_type
    if header_type == 'OBR':
        bg_color = 'yellow-secondary'
        mb_class = 'mb-obr'
        border_type = 'obr'
    elif header_type == 'CBR':
        bg_color = 'gray'
        mb_class = 'mb-cbr'
        border_type = 'cbr'
    elif header_type == 'MNR':
        bg_color = 'green-secondary'
        mb_class = 'mb-mnr'
        border_type = 'mnr'
    else:  # RCB (padrão)
        bg_color = 'blue'
        mb_class = 'mb-obr'
        border_type = 'rcb'

    # 2. Preparar partes condicionais do conteúdo
    tags_html = ""
    if noticia.tags.exists():
        tags_list = ", ".join([tag.nome for tag in noticia.tags.all()])
        tags_html = f'<p><strong>Tags:</strong><br/>{tags_list}</p>'

    ler_mais_html = ''
    tag_div_class = ''
    imagem_component = []
    if noticia.imagem:
        ler_mais_html = '<a class="square-button" href="#conteudo">Ler Mais</a>'
        tag_div_class = 'desktop:text-align-right'
        imagem_component.append({
            "type": "imagem_container",
            "imagem": str(noticia.imagem)
        })

    # 3. Montar a estrutura de componentes JSON
    componentes_json = [
        {
            "type": "section",
            "bg": bg_color,
            "classes": mb_class,
            "border_details": [{
                "type": f"{border_type} cut", "color": bg_color, "position": "bottom right",
                "container": True, "size": "small desktop:big"
            }],
            "components": [{
                "type": "dynamic_texto", "theme_foreground": "yang",
                "conteudo": f'<div class="container padding-y-1 text-yang text-shadow-darker bold text-medium">Visualizar Notícia</div>'
            }]
        },
        {
            "type": "section",
            "main": {"container": True},
            "components": [
                {
                    "type": "html",
                    "conteudo": f"""
                        <div class="margin-y-1/ desktop:margin-y-2">
                            <h1 class="margin-0 extra-bold text-xlarge desktop:text-xxlarge">{noticia.titulo}</h1>
                            <p class="margin-0 text-gray-secondary">Publicado em {noticia.data.strftime('%d/%m/%Y')}</p>
                            <p class="margin-y-1/">{noticia.chamada}</p>
                            <div class="flex-soft flex-between flex-reverse desktop:flex-row">
                                {ler_mais_html}
                                <div class="{tag_div_class}">{tags_html}</div>
                            </div>
                        </div>
                    """
                },
                *imagem_component
            ]
        },
        {
            "type": "section",
            "id": "conteudo",
            "main": {"container": True},
            "components": [
                {"type": "dynamic_texto", "conteudo": noticia.conteudo}
            ]
        }
    ]

    rendered_html = render_components_to_html(componentes_json)

    context = {
        'pagina': noticia,  # Usamos o objeto noticia como se fosse uma 'pagina'
        'header_type': noticia.header_type,
        'componentes_rendered': [rendered_html],
    }
    return render(request, 'base_dynamic.html', context)

from django.shortcuts import render