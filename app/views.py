from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse
from .models import Regiao, Pagina, Funcionario, Arquivo, Data, Noticia, PaginaEstado, Sede, Subevento
from django.views.decorators.cache import cache_page
from django.template.loader import render_to_string
from datetime import date

import json
from .utils.render_components import render_components_to_html


def build_dynamic_components_context(request):
    """
    Helper function to build the extra_context dict for dynamic components.
    Extracts pagination query params and prepares all necessary data.
    
    Returns a dict with:
    - file_page: pagination index for files
    - news_page: pagination index for news
    - extra_context: dict with funcionarios, sedes, subeventos, arquivos, noticias, datas
    """
    try:
        file_page = int(request.GET.get('file_page', 0))
    except (ValueError, TypeError):
        file_page = 0
    
    try:
        news_page = int(request.GET.get('news_page', 0))
    except (ValueError, TypeError):
        news_page = 0
    
    funcionarios = Funcionario.get_items(tag_ids=[10])
    sedes = Sede.get_items(tag_ids=[])
    subeventos = Subevento.get_items(tag_ids=[])
    arquivos = Arquivo.get_items(tag_ids=[], page_index=file_page)
    noticias = Noticia.get_items(tag_ids=[], page_index=news_page)
    datas = list(Data.objects.filter(data__gte=date.today()).order_by('data')[:50])
    
    arquivo_obj = arquivos[0] if arquivos else None
    
    extra_context = {
        'funcionarios': funcionarios,
        'sedes': sedes,
        'subeventos': subeventos,
        'arquivos': arquivos,
        'noticias': noticias,
        'datas': datas,
        'arquivo': arquivo_obj,
    }
    
    return {
        'file_page': file_page,
        'news_page': news_page,
        'extra_context': extra_context,
    }


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
    if reference not in ('cbr', 'mnr', 'obr'):
        reference = 'rcb'

    pagina = get_object_or_404(PaginaEstado, estado=sigla_upper)
    nome_estado = pagina.get_estado_display()
    sigla_lower = sigla.lower()

    # --- Build JSON structure ---

    # Section 1: Mobile Header
    padding_b_class = "padding-b-3" if reference != 'mnr' else ""
    section1 = {
        "type": "section",
        "classes": f"mobile-only flex flex-center {padding_b_class}",
        "components": [{
            "type": "html",
            "conteudo": f'<h1 class="margin-0 header-line ribbon-{reference} padding-1 state-header text-align-center">{nome_estado}</h1>'
        }]
    }

    # Section 2: Desktop Header with State Image
    if reference == 'obr':
        border_detail_s2_html = '<border-detail class="container obr blue top small spin desktop:hidden margin-t-1/"></border-detail>'
    elif reference == 'cbr':
        border_detail_s2_html = '<border-detail class="container cbr blue top left small desktop:hidden margin-t-1/"></border-detail>'
    elif reference == 'mnr':
        border_detail_s2_html = '<border-detail class="container mnr blue top small desktop:hidden"></border-detail>'
    else:  # rcb
        border_detail_s2_html = '<border-detail class="container rcb blue top small desktop:hidden margin-t-0/"></border-detail>'

    state_header_image_html = render_to_string(
        "components/content/state_header_image.html",
        {'flag_path': f"images/bandeiras/{sigla_lower}.png", 'state_path': f"images/estados/{sigla_lower}.png", 'sigla': sigla_upper}
    )

    section2 = {
        "type": "section", "classes": "margin-t-4 desktop:margin-t-3",
        "main": {"container": True, "classes": "flex-soft flex-center desktop:flex-start"},
        "components": [
            {"type": "html", "conteudo": f'<div class="padding-0/ border-radius overflow large bg-blue w-fit inside-bottom">{border_detail_s2_html}{state_header_image_html}</div>'},
            {"type": "html", "conteudo": f'<h1 class="desktop-only margin-0 header-line ribbon-{reference} padding-x-1 padding-y-0/ state-header">{nome_estado}</h1>'}
        ]
    }

    # Section 3: Tabs
    if reference == 'obr':
        border_detail_s3 = {"type": "obr", "color": "blue", "position": "top right", "size": "big", "container": True, "spin": True, "desktop_only": True, "margin_t": "1/"}
    elif reference == 'cbr':
        border_detail_s3 = {"type": "cbr", "color": "blue", "position": "top right", "size": "big", "container": True, "desktop_only": True, "margin_t": "2/"}
    elif reference == 'mnr':
        border_detail_s3 = {"type": "mnr", "color": "blue", "position": "top right", "size": "big", "container": True, "desktop_only": True}
    else:  # rcb
        border_detail_s3 = {"type": "rcb", "color": "blue", "position": "top right", "size": "big", "container": True, "desktop_only": True, "margin_t": "0/"}

    tabs = [{"id": "voluntarios", "label": "Auxilie", "icon": "group", "content": "<h3 class=\"margin-0 margin-b-1 text-xlarge\">Programa de voluntariado</h3><p class=\"margin-0 text-large\">Deseja ser um voluntário em algum evento regional ou estadual? <strong>Entre em contato</strong> com um representante e ajude-nos a democratizar a robótica!</p>"},
              {"id": "invista", "label": "Invista", "icon": "money", "content": "<h3 class=\"margin-0 margin-b-1 text-xlarge\">Invista em eventos de robótica do seu estado!</h3><p class=\"margin-0 text-large\">Deseja investir em uma Regional ou Estadual de algum evento RoboCup Brasil? Entre em contato com um <strong>representante</strong> e ajude-nos a democratizar a robótica!</p>"}]

    section3 = {
        "type": "section", "bg": "blue", "border_details": [border_detail_s3],
        "main": {"container": True, "classes": "padding-t-5 padding-b-2"},
        "components": [{"type": "tabs", "style_classes": "yin blue-secondary", "tabs": tabs}]
    }

    # Section 4: Dynamic Content from Admin
    components_context = build_dynamic_components_context(request)
    file_page = components_context['file_page']
    news_page = components_context['news_page']
    extra_context = components_context['extra_context']

    rendered_dynamic_content = render_components_to_html(pagina.componentes or [], extra_context)

    section4 = {
        "type": "section", "classes": "margin-t-1",
        "main": {"container": True},
        "components": [{"type": "html", "conteudo": rendered_dynamic_content}]
    }

    # Assemble and render
    componentes_json = [section1, section2, section3, section4]
    rendered_html = render_components_to_html(componentes_json)

    context = {
        'pagina': pagina,
        'header_type': reference,
        'titulo': f"{nome_estado} ({sigla_upper})",
        'componentes_rendered': [rendered_html],
    }
    return render(request, 'base_dynamic.html', context)

@cache_page(60 * 60 * 24 * 7)
def subevento_view(request, permalink):
    subevento = get_object_or_404(Subevento, permalink=permalink)
    
    # Determine colors and border type based on event type
    evento = subevento.evento.lower()
    
    if evento == 'mnr':
        bg_color = 'green-secondary'
        border_type = 'mnr'
    elif evento == 'cbr':
        bg_color = 'gray'
        border_type = 'cbr'
    elif evento == 'obr':
        bg_color = 'yellow-secondary'
        border_type = 'obr'
    else:  # RoboCup, Robotica, Todos, etc. → default blue
        bg_color = 'blue'
        border_type = 'rcb'
    
    # Get pagination context for dynamic components
    components_context = build_dynamic_components_context(request)
    extra_context = components_context['extra_context']
    
    # Build custom header JSON structure
    border_detail = {
        "type": border_type,
        "color": bg_color,
        "position": "top right",
        "container": True,
        "size": "small desktop:big"
    }
    # Only add spin for RCB or OBR
    if border_type in ('rcb', 'obr'):
        border_detail["spin"] = True
    
    header_componentes = [
        {
            "type": "section",
            "bg": "",
            "main": {
                "container": True,
                "flex": True
            },
            "components": [
                {
                    "type": "imagem_container",
                    "imagem": f"/media/{str(subevento.icone)}" if subevento.icone else ""
                },
                {
                    "type": "dynamic_texto",
                    "conteudo": "",
                    "theme_foreground": "yin"
                }
            ],
            "border_details": [],
            "inside_bottom": True
        },
        {
            "type": "section",
            "bg": bg_color,
            "main": {
                "container": True
            },
            "components": [
                {
                    "type": "dynamic_texto",
                    "theme_foreground": "yin",
                    "conteudo": f'<div class="text-xlarge desktop:text-xxlarge margin-t-5 margin-b-1 text-shadow text-yang text-700">{subevento.nome}</div>'
                }
            ],
            "border_details": [border_detail]
        }
    ]
    
    # Combine header with user-provided components
    all_componentes = header_componentes + (subevento.componentes or [])
    
    # Render
    rendered_html = render_components_to_html(all_componentes, extra_context)
    
    context = {
        'subevento': subevento,
        'header_type': evento,
        'componentes_rendered': [rendered_html],
        'titulo': subevento.nome,
    }
    return render(request, 'base_dynamic.html', context)

@cache_page(60 * 60 * 24 * 7)
def sede_view(request, ano):
    sede = get_object_or_404(Sede, ano=ano)

    # Get pagination context for dynamic components
    components_context = build_dynamic_components_context(request)
    extra_context = components_context['extra_context']
    
    # Build header JSON structure for sede
    # always blue, no event type
    bg_color = 'blue'
    border_type = 'rcb'

    # header section similar to news header: solid color with cut border detail
    header_section = {
        "type": "section",
        "bg": bg_color,
        "components": [{
            "type": "dynamic_texto",
            "theme_foreground": "yin",
            "conteudo": f'<div class="container padding-y-1 text-yang text-shadow-darker bold text-large">Robótica {sede.ano} - {sede.cidade}</div>'
        }],
        "border_details": [{
            "type": f"{border_type} cut",
            "color": bg_color,
            "position": "bottom left",
            "container": True,
            "size": "small desktop:big",
            "desktop_only": True
        }]
    }

    # second section with state image on right, inside-top to overlap
    state_img_path = sede.foto.url if sede.foto else f"images/estados/{sede.estado.lower()}.png"
    # header template for state image uses flag path and state path; here we only have state image
    state_header_image_html = render_to_string(
        "components/content/state_header_image.html",
        {'flag_path': f"images/bandeiras/{sede.estado.lower()}.png", 'state_path': state_img_path, 'sigla': sede.estado}
    )

    second_section = {
        "type": "section",
        "main": {"container": True, "classes": "flex-soft flex-center desktop:flex-end"},
        "components": [
            {"type": "html", "conteudo": f'<div class="padding-0/ border-radius overflow large bg-blue w-fit">{state_header_image_html}</div>'},
        ]
    }

    header_componentes = [header_section, second_section]
    
    # Combine header with user-provided components
    all_componentes = header_componentes + (sede.componentes or [])
    
    # Render
    rendered_html = render_components_to_html(all_componentes, extra_context)

    context = {
        'sede': sede,
        'header_type': 'rcb',
        'componentes_rendered': [rendered_html],
        'titulo': f"Sede {sede.ano} - {sede.cidade}, {sede.estado}",
    }
    return render(request, 'base_dynamic.html', context)

def pagina_dinamica_view(request, path):
    path = path.strip('/')
    # reserved paths that should not be treated as pages
    if path in ('component-preview',):
        raise Http404()

    # Get pagination context
    components_context = build_dynamic_components_context(request)
    extra_context = components_context['extra_context']
    extra_context['news_page'] = components_context['news_page']
    extra_context['file_page'] = components_context['file_page']

    # Resolve page by path
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

    rendered = render_components_to_html(pagina.componentes or [], extra_context)

    context = {
        'pagina': pagina,
        'header_type': pagina.header_type,
        'componentes_rendered': [rendered],
        'conteudo_html': getattr(pagina, 'componentes_html', ''),
        'titulo': pagina.nome,
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
            "imagem": f"/media/{str(noticia.imagem)}"
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
        'titulo': noticia.titulo,
    }
    return render(request, 'base_dynamic.html', context)

from django.shortcuts import render