"""
Management command to create default tags, sedes, subeventos, dynamic pages and global config.
Idempotent: safe to run multiple times.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from app.models import (
    Sede, Subevento, TagArquivo, TagData, TagFuncionario, TagNoticia,
    PaginaEstado, ConfiguracaoGlobal, Pagina, AtalhoGlobal, ItemMenu, Arquivo,
    Funcionario, Data,
)
from django.conf import settings
from django.utils.text import slugify
from django.core.files.base import ContentFile
from datetime import datetime, timedelta


# ─── helpers ──────────────────────────────────────────────────────────────────

def _sec(components, bg=None, container=True, border_details=None,
         classes=None, margin_y=None, padding_y=None, gap=None,
         flex=False, flex_soft=False, desktop_flex=False, inside_bottom=False):
    """Shortcut for building a section dict."""
    main = {"container": container}
    if gap:
        main["gap"] = gap
    if flex:
        main["flex"] = True
    if flex_soft:
        main["flex_soft"] = True
    if desktop_flex:
        main["desktop:flex"] = True
    d = {
        "type": "section",
        "main": main,
        "components": components,
        "border_details": border_details or [],
    }
    if bg:
        d["bg"] = bg
    if classes:
        d["classes"] = classes
    if margin_y:
        d["margin_y"] = margin_y
    if padding_y:
        d["padding_y"] = padding_y
    if inside_bottom:
        d["inside_bottom"] = True
    return d


def _txt(conteudo, fg="yin"):
    return {"type": "dynamic_texto", "theme_foreground": fg, "conteudo": conteudo}


def _hdr(titulo, theme="rcb", alignment="start", size="xxlarge", fullwidth=False, classes=None):
    d = {"type": "header", "titulo": titulo, "theme": theme,
         "alignment": alignment, "size": size}
    if fullwidth:
        d["fullwidth"] = True
    if classes:
        d["classes"] = classes
    return d


def _btn_inline(texto, href, theme="yin", color="blue", icon="arrow-right", shrink=True):
    return {"type": "button_inline", "texto": texto, "href": href,
            "theme": theme, "color": color, "icon": icon, "shrink": shrink}


def _btn_rounded(texto, href, theme="blue", icon="arrow-right"):
    return {"type": "button_rounded", "texto": texto, "href": href,
            "theme": theme, "icon": icon}


def _sq(titulo, descricao, imagem, inline_text, inline_href,
        inline_color="blue", inline_theme="yang", theme_foreground="yin",
        image_align_desktop="left", image_align_mobile="top", classes=""):
    return {
        "type": "conteudo_square",
        "titulo": titulo,
        "descricao": descricao,
        "imagem": imagem,
        "text_align": "start",
        "image_align_mobile": image_align_mobile,
        "image_align_desktop": image_align_desktop,
        "inline_text": inline_text,
        "inline_href": inline_href,
        "theme_primary": "yang",
        "theme_secondary": "yang",
        "theme_foreground": theme_foreground,
        "inline_color": inline_color,
        "inline_theme": inline_theme,
        "classes": classes,
    }


def _noticias_page(tag_ids, theme="rcb", primary="blue", secondary="blue-secondary"):
    return [
        _sec([_hdr("Todas as Notícias", theme=theme, fullwidth=True)], margin_y="1/"),
        _sec([
            {"type": "dynamic_noticias", "tag_ids": tag_ids, "pagination": True,
             "theme_foreground": "yang", "theme_primary": primary,
             "theme_secondary": secondary, "limit": 12}
        ])
    ]



# ─── page content builders ────────────────────────────────────────────────────

def page_sobre_rcb():
    return [
        {
            "type": "section",
            "bg": "blue",
            "main": {"container": True, "classes": "padding-y-5"},
            "border_details": [
                {"type": "rcb", "color": "yang", "position": "bottom right", "spin": True, "container": True, "desktop_only": True}
            ],
            "components": [
                _txt('<span class="text-xxxlarge text-700">Sobre a <i>RoboCup Brasil</i></span>', "yang"),
                _txt('<span class="text-large text-300">Ciência, Tecnologia e Inovação aliadas à Educação desde 2007</span>', "yang"),
            ]
        },
        _sec([
            _txt("""## Nossa História

A **RoboCup Brasil (RCB)** é a principal associação de robótica e inteligência artificial do Brasil, responsável por organizar e promover competições, mostras e congressos que reúnem estudantes do ensino fundamental à pós-graduação.

Fundada em 2007, a RoboCup Brasil nasceu do entusiasmo de pesquisadores e professores que acreditavam no poder transformador da robótica e da inteligência artificial para a educação brasileira. Ao longo de quase duas décadas, a organização cresceu de um pequeno grupo de competições universitárias para se tornar um dos maiores eventos de CTIS (Ciência, Tecnologia, Inovação e Sociedade) da América Latina.

Hoje, a RoboCup Brasil reúne mais de **200.000 participantes por ano** e conta com três grandes eventos: a **Olimpíada Brasileira de Robótica (OBR)**, a **Competição Brasileira de Robótica (CBR)** e a **Mostra Nacional de Robótica (MNR)** — cada um com foco e público distintos, mas todos unidos pelo mesmo propósito: **levar a robótica e a IA para perto das pessoas**.

O evento anual **Robótica** reúne as três competições simultaneamente em uma mesma cidade-sede, criando um ambiente único de intercâmbio científico, cultural e humano.""")
        ], margin_y="2"),
        _sec([
            _txt('<span class="text-xxlarge text-700">Nossa Liderança</span>'),
        ], margin_y="1/"),
        _sec([
            {"type": "slider_funcionarios", "tags": [], "title": "Presidência e Vice-Presidências",
             "theme_primary": "blue", "theme_foreground": "yang", "theme_secondary": "blue-secondary",
             "size": "large", "limit": 10}
        ], container=False, inside_bottom=True),
        _sec([
            _txt('<span class="text-xlarge text-600">Conselheiros (Trustees)</span>'),
        ], margin_y="1/"),
        _sec([
            {"type": "slider_funcionarios", "tags": [], "title": "Curadores",
             "theme_primary": "gray", "theme_foreground": "yang", "theme_secondary": "gray-secondary",
             "size": "medium", "limit": 20}
        ], container=False, inside_bottom=True),
        _sec([
            _txt('<span class="text-large text-500">Equipe de Apoio</span>'),
        ], margin_y="1/"),
        _sec([
            {"type": "slider_funcionarios", "tags": [], "title": "Prestadores de Serviço",
             "theme_primary": "blue-secondary", "theme_foreground": "yang", "theme_secondary": "blue",
             "size": "small", "limit": 30}
        ], container=False, inside_bottom=True, classes="margin-b-3"),
    ]


def page_robotica():
    return [
        {
            "type": "section",
            "bg": "blue-secondary",
            "main": {"container": True, "desktop:flex": True, "classes": "padding-y-4"},
            "border_details": [
                {"type": "rcb", "color": "blue-secondary", "position": "bottom right", "spin": True, "container": True, "desktop_only": True}
            ],
            "components": [
                {
                    "type": "section",
                    "main": {"container": False},
                    "border_details": [],
                    "components": [
                        _txt('<span class="text-small text-400 text-yang">EVENTO NACIONAL</span>', "yang"),
                        _txt('<span class="text-xxxxlarge text-900"><i>Robótica</i></span>', "yang"),
                        _txt('<span class="text-large text-300 text-yang">A maior reunião de robótica e inteligência artificial do Brasil e da América Latina</span>', "yang"),
                        _btn_rounded("Robótica 2026 → João Pessoa", "/sede/2026", "yang"),
                    ]
                },
                {"type": "imagem", "imagem": "/media/arquivos/2026.png", "titulo": "Robótica 2026",
                 "clicavel": True, "href": "/sede/2026", "rounded": True,
                 "classes": "h-5 object-contain"},
            ]
        },
        _sec([
            _txt("""## O Que é o Evento Robótica?

O **Robótica** é o maior evento de robótica e inteligência artificial da América Latina. Realizado anualmente desde 2007, ele reúne simultaneamente três grandes competições/mostras nacionais:

- 🏅 **OBR** — Olimpíada Brasileira de Robótica: para alunos do ensino fundamental ao médio
- 🤖 **CBR** — Competição Brasileira de Robótica: para universitários e pesquisadores
- 📋 **MNR** — Mostra Nacional de Robótica: para apresentação de trabalhos de todos os níveis

O evento é realizado em uma cidade diferente a cada ano, escolhida por suas condições de infraestrutura e pelo compromisso dos representantes locais com a robótica."""),
        ], margin_y="2"),
        _sec([
            _txt('<span class="text-xxlarge text-700">Edições do Evento</span>'),
        ], margin_y="1/"),
        _sec([
            {"type": "slider_sedes", "title": "Sedes do Robótica",
             "theme_primary": "blue", "theme_foreground": "yang", "theme_secondary": "blue-secondary",
             "limit": 30}
        ], container=False, inside_bottom=True),
        _sec([
            _btn_inline("Ver Robótica 2026", "/sede/2026", color="blue"),
            _btn_inline("Participe pelo Sistema Olimpo", "https://olimpo.robocup.org.br/", color="blue-secondary"),
        ], gap="1", margin_y="2"),
    ]


def page_sede_passada(ano, cidade, estado):
    return [
        _sec([
            _txt(f'<span class="text-xxlarge text-700">Robótica {ano}</span>', "yang"),
            _txt(f'<span class="text-large">{cidade} — {estado}</span>', "yang"),
            _txt('<span class="text-medium text-300">Este evento já aconteceu. As informações desta edição estão sendo organizadas e serão disponibilizadas em breve.</span>', "yang"),
        ], bg="blue-secondary",
        border_details=[{"type": "rcb", "color": "blue-secondary", "position": "bottom right", "spin": True, "container": True, "desktop_only": True}]),
    ]


def page_sede_atual():
    """2026 — current year"""
    return [
        {
            "type": "section",
            "bg": "blue",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [
                {"type": "rcb", "color": "blue", "position": "bottom right", "spin": True, "container": True, "desktop_only": True}
            ],
            "components": [
                _txt('<span class="text-small text-yang">EVENTO NACIONAL</span>', "yang"),
                _txt('<span class="text-xxxxlarge text-900 text-yang"><i>Robótica 2026</i></span>', "yang"),
                _txt('<span class="text-xlarge text-yang">João Pessoa — PB</span>', "yang"),
                _btn_rounded("Participe via Sistema Olimpo", "https://olimpo.robocup.org.br/", "yang"),
            ]
        },
        _sec([_txt('<span class="text-xxlarge text-700">Competições da MNR</span>')], margin_y="1/"),
        _sec([
            {"type": "slider_subeventos", "evento": "MNR", "title": "Mostra Nacional de Robótica",
             "theme_primary": "green", "theme_foreground": "yang", "theme_secondary": "green-secondary", "limit": 20}
        ], container=False, inside_bottom=True),
        _sec([_txt('<span class="text-xxlarge text-700">Competições da OBR</span>')], margin_y="1/"),
        _sec([
            {"type": "slider_subeventos", "evento": "OBR", "title": "Olimpíada Brasileira de Robótica",
             "theme_primary": "yellow", "theme_foreground": "yang", "theme_secondary": "yellow-secondary", "limit": 20}
        ], container=False, inside_bottom=True),
        _sec([_txt('<span class="text-xxlarge text-700">Ligas da CBR</span>')], margin_y="1/"),
        _sec([
            {"type": "slider_subeventos", "evento": "CBR", "title": "Competição Brasileira de Robótica",
             "theme_primary": "gray", "theme_foreground": "yang", "theme_secondary": "gray-secondary", "limit": 20}
        ], container=False, inside_bottom=True, classes="margin-b-3"),
    ]


def page_participe():
    return [
        {
            "type": "section",
            "bg": "blue",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [
                {"type": "rcb", "color": "blue", "position": "bottom left", "container": True, "desktop_only": True}
            ],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Participe dos Nossos Eventos</span>', "yang"),
                _txt('<span class="text-large text-300 text-yang">Inscrições pelo Sistema Olimpo — a plataforma oficial da RoboCup Brasil</span>', "yang"),
            ]
        },
        _sec([
            _sq(
                "Sistema Olimpo",
                '<div class="text-large-plus-plus text-300">O <strong>Olimpo</strong> é o sistema de gestão centralizada de inscrições e participação nos eventos da RoboCup Brasil. Nele você pode se inscrever na OBR, CBR e MNR, acompanhar resultados, enviar documentos e muito mais.</div>',
                "/static/images/header/olimpo.png",
                "Acessar o Olimpo",
                "https://olimpo.robocup.org.br/",
                inline_color="blue",
                classes="icon-image",
                image_align_desktop="right",
            ),
        ], margin_y="2"),
        _sec([
            _txt('<span class="text-xxlarge text-700">Como participar</span>'),
            _txt("""**1. Crie sua conta no Olimpo**
Acesse https://olimpo.robocup.org.br/ e registre-se. O cadastro é gratuito e leva menos de 2 minutos.

**2. Escolha seu evento**
Decida em qual competição você quer participar — OBR, CBR ou MNR — e confira os requisitos de cada modalidade.

**3. Realize sua inscrição**
Preencha as informações da sua equipe, envie a documentação necessária e efetue o pagamento das taxas (quando aplicável).

**4. Participe!**
Acompanhe as datas e comunicados pelo sistema e prepare-se para a competição."""),
        ], margin_y="1/"),
        _sec([
            _sq("Olimpíada Brasileira de Robótica", '<span class="text-large-plus text-300">Para alunos do ensino fundamental ao médio. Provas práticas de resgate, artística, virtual e teórica.</span>',
                "/static/images/favicon/obr.png", "Saiba mais sobre a OBR", "/obr",
                inline_color="green-secondary", classes="icon-image", image_align_desktop="left"),
            _sq("Competição Brasileira de Robótica", '<span class="text-large-plus text-300">Para alunos do ensino médio e superior. Ligas da RoboCup Federation e ligas nacionais.</span>',
                "/static/images/favicon/cbr.png", "Saiba mais sobre a CBR", "/cbr",
                inline_color="gray-secondary", classes="icon-image", image_align_desktop="left"),
        ], desktop_flex=True, gap="2", margin_y="2"),
    ]


def page_associados():
    return [
        {
            "type": "section",
            "bg": "blue-secondary",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [
                {"type": "rcb", "color": "blue-secondary", "position": "bottom right", "spin": True, "container": True, "desktop_only": True}
            ],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Programa de Associados</span>', "yang"),
                _txt('<span class="text-large text-yang">Apoie a robótica e a IA no Brasil. Faça parte da RoboCup Brasil.</span>', "yang"),
            ]
        },
        _sec([
            _txt("""## O que é o Programa de Associados?

A RoboCup Brasil é uma associação sem fins lucrativos. Para manter e expandir nossas atividades — que alcançam mais de 200.000 participantes por ano — contamos com o apoio de associados institucionais e individuais.

Ao se tornar associado, você contribui diretamente para:
- A organização e expansão das competições de robótica no Brasil
- O desenvolvimento de novos materiais didáticos e manuais
- A criação de bolsas e premiações para participantes
- A representação do Brasil na RoboCup internacional

## Categorias de Associação

| Categoria | Público-alvo | Valor Anual |
|-----------|-------------|-------------|
| **Associado Estudante** | Estudantes de graduação/pós | R$ 50,00 |
| **Associado Individual** | Profissionais e pesquisadores | R$ 150,00 |
| **Associado Institucional Bronze** | Empresas e inst. de pequeno porte | R$ 1.000,00 |
| **Associado Institucional Prata** | Empresas e inst. de médio porte | R$ 2.500,00 |
| **Associado Institucional Ouro** | Grandes empresas e patrocinadores | R$ 5.000,00 |

## Benefícios

Todos os associados têm acesso a:
- **Voto** nas assembleias da RoboCup Brasil
- **Descontos** nas inscrições de eventos
- **Certificado** de associação
- **Visibilidade** no site e materiais da RCB (institucionais)
- **Acesso antecipado** a editais e chamadas"""),
        ], margin_y="2"),
        _sec([
            _btn_rounded("Associe-se pelo Sistema Olimpo", "https://olimpo.robocup.org.br/", "blue"),
            _btn_inline("Fale Conosco", "/contato", color="blue-secondary"),
        ], gap="1", margin_y="1/"),
    ]


def page_contato():
    return [
        {
            "type": "section",
            "bg": "blue",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [
                {"type": "rcb", "color": "blue", "position": "bottom right", "spin": True, "container": True, "desktop_only": True}
            ],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Fale Conosco</span>', "yang"),
                _txt('<span class="text-large text-yang">Entre em contato com a equipe da RoboCup Brasil</span>', "yang"),
            ]
        },
        _sec([
            _txt("""## Contato Geral

Para assuntos gerais da RoboCup Brasil:

📧 **contato@robocup.org.br**

---

## OBR — Olimpíada Brasileira de Robótica

Para dúvidas sobre inscrições, modalidades, manuais e participação na OBR:

📧 **obr@robocup.org.br**

---

## CBR — Competição Brasileira de Robótica

Para dúvidas sobre ligas, TDP, pagamentos e participação na CBR:

📧 **cbr@robocup.org.br**

---

## MNR — Mostra Nacional de Robótica

Para dúvidas sobre submissão de trabalhos, anais e participação na MNR:

📧 **mnr@robocup.org.br**"""),
        ], margin_y="2"),
        {
            "type": "section",
            "bg": "blue-secondary",
            "main": {"container": True, "classes": "padding-y-3"},
            "border_details": [],
            "components": [
                _txt('<span class="text-xlarge text-700 text-yang">Imprensa</span>', "yang"),
                _txt("""Para solicitações de entrevistas, dados, imagens e informações para a imprensa:

📧 **comunicacao@robocup.org.br**

Por favor, identifique-se como jornalista/veículo de comunicação e descreva brevemente sua pauta.""", "yang"),
            ]
        },
    ]


def page_voluntarios():
    return [
        {
            "type": "section",
            "bg": "blue",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [
                {"type": "rcb", "color": "blue", "position": "bottom right", "spin": True, "container": True, "desktop_only": True}
            ],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Seja Voluntário</span>', "yang"),
                _txt('<span class="text-large text-yang">Ajude a levar a robótica para mais brasileiros</span>', "yang"),
            ]
        },
        _sec([
            _txt("""## Por que ser voluntário?

Participar como voluntário nos eventos da RoboCup Brasil é uma experiência única. Você contribui diretamente para a formação científica e tecnológica de milhares de jovens em todo o Brasil — e ainda ganha muito com isso!

### Benefícios

- ✅ **Horas complementares** reconhecidas por diversas universidades brasileiras
- ✅ **Certificado** oficial de voluntariado emitido pela RoboCup Brasil
- ✅ **Networking** com profissionais e pesquisadores de robótica e IA
- ✅ **Experiência prática** em gestão de grandes eventos científicos
- ✅ **Currículo diferenciado** para o mercado de trabalho e pós-graduação
- ✅ **Missão**: contribuir para a expansão da robótica pelo Brasil

### O que fazem os voluntários?

Os voluntários atuam na organização logística, apoio às competições, recepção de equipes, apoio técnico, comunicação e muito mais. Há espaço para todos os perfis!"""),
        ], margin_y="2"),
        _sec([
            _btn_rounded("Inscrever-se como Voluntário Nacional", "#", "blue"),
        ], margin_y="1/"),
        {
            "type": "section",
            "bg": "blue-secondary",
            "main": {"container": True, "classes": "padding-y-3"},
            "border_details": [],
            "components": [
                _txt('<span class="text-xlarge text-700 text-yang">Voluntários para Eventos Estaduais</span>', "yang"),
                _txt("""Para participar como voluntário em eventos estaduais da OBR e MNR, entre em contato diretamente com o **representante estadual** da sua região.

Os representantes estão listados na página de estados e são responsáveis pela organização das etapas regionais em cada unidade da federação.

📍 [Ver representantes estaduais](/organizacao-regional)""", "yang"),
            ]
        },
    ]


def page_material_divulgacao():
    return [
        {
            "type": "section",
            "bg": "blue",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [
                {"type": "rcb", "color": "blue", "position": "bottom right", "spin": True, "container": True, "desktop_only": True}
            ],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Identidade Visual</span>', "yang"),
                _txt('<span class="text-large text-yang">Logos, cores e fontes da RoboCup Brasil e seus eventos</span>', "yang"),
            ]
        },
        # IDV 2026 files
        _sec([
            _txt('<span class="text-xxlarge text-700">Identidade Visual 2026</span>'),
            _txt('<span class="text-medium text-300">Materiais oficiais da identidade visual da edição 2026</span>'),
        ], margin_y="1/"),
        _sec([
            {"type": "dynamic_arquivos", "tag_ids": [], "pagination": False, "limit": 20,
             "theme_primary": "blue", "theme_secondary": "blue-secondary", "theme_foreground": "yang"}
        ]),
        # Logos
        _sec([
            _txt('<span class="text-xxlarge text-700">Identidade Visual</span>'),
        ], margin_y="1/"),
        # OBR IDV
        _sec([
            _sq("Olimpíada Brasileira de Robótica",
                '<span class="text-large-plus text-300">Materiais de identidade visual da OBR: logos, arquivos vetoriais e guia de marca.</span>',
                "/static/images/favicon/obr.png",
                "Ver Arquivos OBR", "#",
                inline_color="green-secondary", classes="icon-image"),
            {"type": "dynamic_arquivos", "tag_ids": [], "pagination": False, "limit": 10,
             "theme_primary": "green", "theme_secondary": "green-secondary", "theme_foreground": "yang"}
        ], desktop_flex=True, gap="2", margin_y="1/"),
        # CBR IDV
        _sec([
            _sq("Competição Brasileira de Robótica",
                '<span class="text-large-plus text-300">Materiais de identidade visual da CBR: logos, arquivos vetoriais e guia de marca.</span>',
                "/static/images/favicon/cbr.png",
                "Ver Arquivos CBR", "#",
                inline_color="gray-secondary", classes="icon-image"),
            {"type": "dynamic_arquivos", "tag_ids": [], "pagination": False, "limit": 10,
             "theme_primary": "gray", "theme_secondary": "gray-secondary", "theme_foreground": "yang"}
        ], desktop_flex=True, gap="2", margin_y="1/"),
        # MNR IDV
        _sec([
            _sq("Mostra Nacional de Robótica",
                '<span class="text-large-plus text-300">Materiais de identidade visual da MNR: logos, arquivos vetoriais e guia de marca.</span>',
                "/static/images/header/mnr.png",
                "Ver Arquivos MNR", "#",
                inline_color="green", classes="icon-image"),
            {"type": "dynamic_arquivos", "tag_ids": [], "pagination": False, "limit": 10,
             "theme_primary": "green", "theme_secondary": "green-secondary", "theme_foreground": "yang"}
        ], desktop_flex=True, gap="2", margin_y="1/"),
        # Cores
        _sec([_txt('<span class="text-xxlarge text-700">Paleta de Cores</span>')], margin_y="2"),
        # Color swatches via html component
        {"type": "section", "main": {"container": True, "gap": "1/"}, "border_details": [], "classes": "margin-b-2",
         "components": [
             {"type": "html", "html": """<div style="display:flex;flex-wrap:wrap;gap:1rem;">
  <div style="background:#2c2e35;color:#f4fcfc;padding:2rem 1.5rem;border-radius:.5rem;flex:1;min-width:140px;text-align:center">
    <div style="font-size:1.75rem;font-weight:700;text-shadow:0 0 8px rgba(255,255,255,.3)">Yin</div>
    <div style="font-size:.875rem;margin-top:.5rem">#2c2e35</div>
  </div>
  <div style="background:#1a1c21;color:#f4fcfc;padding:2rem 1.5rem;border-radius:.5rem;flex:1;min-width:140px;text-align:center">
    <div style="font-size:1.5rem;font-weight:600;text-shadow:0 0 8px rgba(255,255,255,.3)">Yin Secundário</div>
    <div style="font-size:.875rem;margin-top:.5rem">#000000</div>
  </div>
  <div style="background:#f4fcfc;color:#2c2e35;padding:2rem 1.5rem;border-radius:.5rem;flex:1;min-width:140px;text-align:center;border:1px solid #eee">
    <div style="font-size:1.75rem;font-weight:700">Yang</div>
    <div style="font-size:.875rem;margin-top:.5rem">#f4fcfc</div>
  </div>
  <div style="background:#ffffff;color:#2c2e35;padding:2rem 1.5rem;border-radius:.5rem;flex:1;min-width:140px;text-align:center;border:1px solid #eee">
    <div style="font-size:1.5rem;font-weight:600">Yang Secundário</div>
    <div style="font-size:.875rem;margin-top:.5rem">#ffffff</div>
  </div>
</div>
<div style="display:flex;flex-wrap:wrap;gap:1rem;margin-top:2rem;">
  <div style="background:#5F95CF;color:#f4fcfc;padding:2rem 1.5rem;border-radius:.5rem;flex:1;min-width:140px;text-align:center">
    <div style="font-size:1.75rem;font-weight:700;text-shadow:0 2px 4px rgba(0,0,0,.3)">Azul</div>
    <div style="font-size:.875rem;margin-top:.5rem">#5F95CF</div>
  </div>
  <div style="background:#5688BE;color:#f4fcfc;padding:2rem 1.5rem;border-radius:.5rem;flex:1;min-width:140px;text-align:center">
    <div style="font-size:1.5rem;font-weight:600;text-shadow:0 2px 4px rgba(0,0,0,.3)">Azul Secundário</div>
    <div style="font-size:.875rem;margin-top:.5rem">#5688BE</div>
  </div>
  <div style="background:#84C54F;color:#f4fcfc;padding:2rem 1.5rem;border-radius:.5rem;flex:1;min-width:140px;text-align:center;margin-top:1rem">
    <div style="font-size:1.75rem;font-weight:700;text-shadow:0 2px 4px rgba(0,0,0,.3)">Verde</div>
    <div style="font-size:.875rem;margin-top:.5rem">#84C54F</div>
  </div>
  <div style="background:#71B13C;color:#f4fcfc;padding:2rem 1.5rem;border-radius:.5rem;flex:1;min-width:140px;text-align:center;margin-top:1rem">
    <div style="font-size:1.5rem;font-weight:600;text-shadow:0 2px 4px rgba(0,0,0,.3)">Verde Secundário</div>
    <div style="font-size:.875rem;margin-top:.5rem">#71B13C</div>
  </div>
</div>
<div style="display:flex;flex-wrap:wrap;gap:1rem;margin-top:2rem;">
  <div style="background:#E8C347;color:#2c2e35;padding:2rem 1.5rem;border-radius:.5rem;flex:1;min-width:140px;text-align:center">
    <div style="font-size:1.75rem;font-weight:700;text-shadow:0 2px 4px rgba(0,0,0,.2)">Amarelo</div>
    <div style="font-size:.875rem;margin-top:.5rem">#E8C347</div>
  </div>
  <div style="background:#DAB439;color:#2c2e35;padding:2rem 1.5rem;border-radius:.5rem;flex:1;min-width:140px;text-align:center">
    <div style="font-size:1.5rem;font-weight:600;text-shadow:0 2px 4px rgba(0,0,0,.2)">Amarelo Secundário</div>
    <div style="font-size:.875rem;margin-top:.5rem">#DAB439</div>
  </div>
  <div style="background:#EB6047;color:#f4fcfc;padding:2rem 1.5rem;border-radius:.5rem;flex:1;min-width:140px;text-align:center;margin-top:1rem">
    <div style="font-size:1.75rem;font-weight:700;text-shadow:0 2px 4px rgba(0,0,0,.3)">Vermelho</div>
    <div style="font-size:.875rem;margin-top:.5rem">#EB6047</div>
  </div>
  <div style="background:#D7523A;color:#f4fcfc;padding:2rem 1.5rem;border-radius:.5rem;flex:1;min-width:140px;text-align:center;margin-top:1rem">
    <div style="font-size:1.5rem;font-weight:600;text-shadow:0 2px 4px rgba(0,0,0,.3)">Vermelho Secundário</div>
    <div style="font-size:.875rem;margin-top:.5rem">#D7523A</div>
  </div>
</div>
<div style="display:flex;flex-wrap:wrap;gap:1rem;margin-top:2rem;">
  <div style="background:#F5821F;color:#f4fcfc;padding:2rem 1.5rem;border-radius:.5rem;flex:1;min-width:140px;text-align:center">
    <div style="font-size:1.75rem;font-weight:700;text-shadow:0 2px 4px rgba(0,0,0,.3)">Laranja</div>
    <div style="font-size:.875rem;margin-top:.5rem">#F5821F</div>
  </div>
  <div style="background:#E07B25;color:#f4fcfc;padding:2rem 1.5rem;border-radius:.5rem;flex:1;min-width:140px;text-align:center">
    <div style="font-size:1.5rem;font-weight:600;text-shadow:0 2px 4px rgba(0,0,0,.3)">Laranja Secundário</div>
    <div style="font-size:.875rem;margin-top:.5rem">#E07B25</div>
  </div>
  <div style="background:#939598;color:#f4fcfc;padding:2rem 1.5rem;border-radius:.5rem;flex:1;min-width:140px;text-align:center;margin-top:1rem">
    <div style="font-size:1.75rem;font-weight:700;text-shadow:0 2px 4px rgba(0,0,0,.3)">Cinza</div>
    <div style="font-size:.875rem;margin-top:.5rem">#939598</div>
  </div>
  <div style="background:#828282;color:#f4fcfc;padding:2rem 1.5rem;border-radius:.5rem;flex:1;min-width:140px;text-align:center;margin-top:1rem">
    <div style="font-size:1.5rem;font-weight:600;text-shadow:0 2px 4px rgba(0,0,0,.3)">Cinza Secundário</div>
    <div style="font-size:.875rem;margin-top:.5rem">#828282</div>
  </div>
</div>"""}
        ]},
        # Tipografia
        _sec([_txt('<span class="text-xxlarge text-700">Tipografia</span>')], margin_y="2"),
        _sec([
            _txt("""### Nunito

A fonte oficial da RoboCup Brasil é a **Nunito**, uma fonte sans-serif arredondada de alta legibilidade.

| Classe | Tamanho |
|--------|---------|
| `text-xsmall` | 0.75rem |
| `text-small` | 0.875rem |
| `text-default` | 1rem |
| `text-medium` | 1.1rem |
| `text-large` | 1.25rem |
| `text-large-plus` | 1.5rem |
| `text-xlarge` | 2rem |
| `text-xxlarge` | 2.5rem |
| `text-xxxlarge` | 2.75rem |
| `text-xxxxlarge` | 3rem |

**Pesos disponíveis:** `text-200` · `text-300` · `text-400` · `text-500` · `text-600` · `text-700` · `text-800` · `text-900`"""),
        ], margin_y="1/"),
    ]



def page_invista():
    return [
        {
            "type": "section",
            "bg": "blue",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [
                {"type": "rcb", "color": "blue", "position": "bottom right", "spin": True, "container": True, "desktop_only": True}
            ],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Invista na Robótica Brasileira</span>', "yang"),
                _txt('<span class="text-large text-yang">Seja parceiro e patrocinador da RoboCup Brasil</span>', "yang"),
            ]
        },
        _sec([
            _txt("""## Por que investir na RoboCup Brasil?

A RoboCup Brasil é o maior produtor de eventos de robótica e inteligência artificial do país. Com mais de **200.000 participantes anuais** e presença em todos os estados brasileiros, somos a principal porta de entrada de jovens talentos na área de CTIS.

### Números que impressionam

- 🎓 **+200.000** participantes por ano
- 🏫 **+15.000** escolas e universidades participantes
- 🗺️ **27 estados** com presença ativa
- 📅 **+18 anos** de história
- 🌎 Representação do Brasil na **RoboCup mundial**

### Impacto social e científico

Os eventos da RoboCup Brasil são, por princípio, ações de **Divulgação Científica**. Ao patrocinar a RCB, sua empresa investe diretamente em:

- Formação de novos engenheiros, cientistas e tecnólogos
- Desenvolvimento de soluções inovadoras para desafios nacionais
- Democratização do acesso à ciência e tecnologia
- Visibilidade junto a um público qualificado e engajado

### Cotas de patrocínio

| Cota | Investimento | Benefícios |
|------|-------------|-----------|
| **Bronze** | A consultar | Logo no site e materiais |
| **Prata** | A consultar | + Espaço no evento, banner |
| **Ouro** | A consultar | + Naming rights de modalidade |
| **Platina** | A consultar | + Customizado conforme demanda |

Para saber mais sobre as cotas atualizadas e oportunidades de parceria, entre em contato com nossa equipe."""),
        ], margin_y="2"),
        _sec([
            _btn_rounded("Fale com a equipe comercial", "/contato", "blue"),
        ], margin_y="1/"),
    ]


def page_obr_home():
    return [
        {
            "type": "section",
            "bg": "yellow-secondary",
            "main": {"container": True, "classes": "padding-y-5"},
            "border_details": [
                {"type": "obr", "color": "yellow-secondary", "position": "bottom right", "spin": True, "container": True, "desktop_only": True},
                {"type": "obr", "color": "yellow-secondary", "position": "bottom center", "mobile_only": True, "spin": True, "size": "small"},
            ],
            "components": [
                {"type": "imagem", "imagem": "/static/images/header/obr.png", "titulo": "Logo OBR",
                 "clicavel": False, "rounded": False, "classes": "h-3 object-contain"},
                _txt('<span class="text-xxxxlarge text-900 text-yang">Olimpíada Brasileira de Robótica</span>', "yang"),
                _txt('<span class="text-xlarge text-300 text-yang">Uma das maiores competições de robótica do mundo</span>', "yang"),
                _btn_rounded("Participe — Inscreva-se no Olimpo", "https://olimpo.robocup.org.br/", "yang"),
            ]
        },
        _sec([
            _txt("""## O que é a OBR?

A **Olimpíada Brasileira de Robótica (OBR)** é uma das maiores competições de robótica do mundo, com mais de **200.000 participantes** por ano. Voltada para jovens do ensino fundamental, médio e técnico, a OBR estimula o aprendizado de robótica, programação, matemática e física de forma prática e divertida."""),
        ], margin_y="2"),
        _sec([
            _sq("Modalidade Teórica", '<span class="text-large-plus text-300">Prova de múltipla escolha sobre robótica, programação e inteligência artificial. Aplica-se em escolas de todo o Brasil.</span>',
                "/static/images/favicon/obr.png", "Saiba mais", "/obr/modalidades",
                inline_color="yellow-secondary", classes="icon-image"),
            _sq("Modalidades Práticas", '<span class="text-large-plus text-300">Robótica de Resgate, Artística e Virtual — equipes constroem e programam robôs para completar desafios.</span>',
                "/static/images/favicon/obr.png", "Saiba mais", "/obr/modalidades",
                inline_color="green-secondary", classes="icon-image"),
        ], desktop_flex=True, gap="2", margin_y="2"),
        _sec([
            {"type": "slider_arquivos", "tags": [], "title": "Fotos da OBR",
             "theme_primary": "yellow", "theme_foreground": "yang", "theme_secondary": "yellow-secondary", "limit": 10}
        ], container=False, inside_bottom=True),
        _sec([
            _hdr("Notícias OBR", theme="obr", alignment="start"),
        ], margin_y="1/"),
        _sec([
            {"type": "dynamic_noticias", "tag_ids": [1], "pagination": False, "limit": 3,
             "theme_foreground": "yang", "theme_primary": "yellow", "theme_secondary": "yellow-secondary"},
            _btn_inline("Todas as Notícias OBR", "/obr/noticias", color="yellow-secondary"),
        ], gap="1"),
    ]


def page_obr_sobre():
    return [
        {
            "type": "section",
            "bg": "yellow-secondary",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [
                {"type": "obr", "color": "yellow-secondary", "position": "bottom right", "spin": True, "container": True, "desktop_only": True}
            ],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Sobre a OBR</span>', "yang"),
                _txt('<span class="text-large text-yang">Olimpíada Brasileira de Robótica — história, missão e estrutura</span>', "yang"),
            ]
        },
        _sec([
            _txt("""## Sobre a Olimpíada Brasileira de Robótica

A **Olimpíada Brasileira de Robótica (OBR)** é uma competição científica de âmbito nacional que visa estimular o interesse de estudantes do ensino fundamental, médio e técnico pela robótica e áreas correlatas.

Realizada anualmente desde 2008, a OBR é organizada pela **RoboCup Brasil** e conta com o apoio de diversas instituições de ensino e pesquisa do país. A competição envolve dois tipos de provas: a **Modalidade Teórica**, aplicada em escolas de todo o Brasil, e as **Modalidades Práticas** (Resgate, Artística e Virtual), realizadas nas etapas regionais e na fase nacional.

## Modalidades

**🔬 Modalidade Teórica**
Prova de múltipla escolha aplicada nas escolas, com questões sobre robótica, matemática, física e raciocínio lógico. Os melhores alunos passam para a fase nacional.

**🤖 Robótica de Resgate**
Robôs autônomos devem percorrer um labirinto e resgatar "vítimas". Estimula programação, eletrônica e resolução de problemas.

**🎨 Robótica Artística**
Robôs realizam uma apresentação artística e coreografada. Criatividade e precisão andam lado a lado.

**💻 Robótica Virtual**
Simulação em computador de tarefas de robótica. Acessível a equipes de todo o Brasil sem necessidade de hardware físico."""),
        ], margin_y="2"),
        _sec([
            {"type": "slider_arquivos", "tags": [], "title": "Fotos OBR",
             "theme_primary": "yellow", "theme_foreground": "yang", "theme_secondary": "yellow-secondary", "limit": 8}
        ], container=False, inside_bottom=True),
    ]


def page_obr_manuais():
    return [
        {
            "type": "section",
            "bg": "yellow-secondary",
            "main": {"container": True, "classes": "padding-y-3"},
            "border_details": [],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Manuais OBR</span>', "yang"),
                _txt('<span class="text-large text-yang">Documentação oficial das modalidades da OBR</span>', "yang"),
            ]
        },
        _sec([
            _txt('<span class="text-xxlarge text-700">Documentos Gerais</span>'),
        ], margin_y="1/"),
        _sec([
            {"type": "dynamic_arquivos", "tag_ids": [], "pagination": False, "limit": 10,
             "theme_primary": "yellow", "theme_secondary": "yellow-secondary", "theme_foreground": "yang"}
        ]),
        _sec([
            _txt('<span class="text-xxlarge text-700">Modalidade Teórica</span>'),
        ], margin_y="1/"),
        _sec([
            {"type": "dynamic_arquivos", "tag_ids": [], "pagination": False, "limit": 10,
             "theme_primary": "yellow", "theme_secondary": "yellow-secondary", "theme_foreground": "yang"}
        ]),
        _sec([
            _txt('<span class="text-xxlarge text-700">Robótica de Resgate</span>'),
        ], margin_y="1/"),
        _sec([
            {"type": "dynamic_arquivos", "tag_ids": [], "pagination": False, "limit": 10,
             "theme_primary": "yellow", "theme_secondary": "yellow-secondary", "theme_foreground": "yang"}
        ]),
        _sec([
            _txt('<span class="text-xxlarge text-700">Robótica Artística</span>'),
        ], margin_y="1/"),
        _sec([
            {"type": "dynamic_arquivos", "tag_ids": [], "pagination": False, "limit": 10,
             "theme_primary": "yellow", "theme_secondary": "yellow-secondary", "theme_foreground": "yang"}
        ]),
        _sec([
            _txt('<span class="text-xxlarge text-700">Robótica Virtual</span>'),
        ], margin_y="1/"),
        _sec([
            {"type": "dynamic_arquivos", "tag_ids": [], "pagination": False, "limit": 10,
             "theme_primary": "yellow", "theme_secondary": "yellow-secondary", "theme_foreground": "yang"}
        ]),
        _sec([
            _txt('<span class="text-xxlarge text-700">Aplicável à Nacional</span>'),
        ], margin_y="1/"),
        _sec([
            {"type": "dynamic_arquivos", "tag_ids": [], "pagination": False, "limit": 10,
             "theme_primary": "yellow", "theme_secondary": "yellow-secondary", "theme_foreground": "yang"}
        ]),
    ]


def page_obr_modalidades():
    return [
        {
            "type": "section",
            "bg": "yellow-secondary",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [
                {"type": "obr", "color": "yellow-secondary", "position": "bottom right", "spin": True, "container": True, "desktop_only": True}
            ],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Conheça Nossas Modalidades</span>', "yang"),
                _txt('<span class="text-large text-yang">Da teórica às práticas — há um desafio para cada perfil</span>', "yang"),
            ]
        },
        _sec([
            _txt("""## Modalidades da OBR

A OBR conta com quatro modalidades de competição, cada uma com suas próprias regras, desafios e categorias por nível de ensino."""),
        ], margin_y="2"),
        _sec([
            _sq("Modalidade Teórica",
                '<span class="text-large-plus text-300">Prova de múltipla escolha aplicada nas escolas, abrangendo robótica, programação, física e matemática. Os melhores classificados avançam para a fase nacional.</span>',
                "/static/images/favicon/obr.png",
                "Ir para Teórica", "/obr/modalidades",
                inline_color="yellow-secondary", classes="icon-image"),
        ], margin_y="1/"),
        _sec([
            _sq("Robótica de Resgate",
                '<span class="text-large-plus text-300">Robôs autônomos percorrem labirintos e resgartam "vítimas". Uma das modalidades mais técnicas e disputadas da OBR.</span>',
                "/static/images/favicon/obr.png",
                "Ver subevento", "/obr/modalidades",
                inline_color="green-secondary", classes="icon-image"),
            _sq("Robótica Artística",
                '<span class="text-large-plus text-300">Criatividade e precisão: robôs realizam performances artísticas e coreografias programadas pelas equipes.</span>',
                "/static/images/favicon/obr.png",
                "Ver subevento", "/obr/modalidades",
                inline_color="orange", classes="icon-image"),
        ], desktop_flex=True, gap="2", margin_y="1/"),
        _sec([
            _sq("Robótica Virtual",
                '<span class="text-large-plus text-300">Simulação computacional de tarefas robóticas. Modalidade acessível a equipes de qualquer estado, sem necessidade de hardware.</span>',
                "/static/images/favicon/obr.png",
                "Ver subevento", "/obr/modalidades",
                inline_color="blue", classes="icon-image"),
        ], margin_y="1/"),
        _sec([
            _txt('<span class="text-xxlarge text-700">Modalidade Teórica — Provas e Gabaritos</span>'),
        ], margin_y="2"),
        {
            "type": "tabs",
            "tabs": [
                {
                    "id": "tab-provas",
                    "label": "Provas",
                    "content": '<div class="container"><p class="text-medium text-300">Abaixo você encontra as provas das edições anteriores da Modalidade Teórica.</p></div>'
                },
                {
                    "id": "tab-gabaritos",
                    "label": "Gabaritos",
                    "content": '<div class="container"><p class="text-medium text-300">Gabaritos oficiais das provas da Modalidade Teórica.</p></div>'
                }
            ],
            "style": "obr"
        },
    ]


def page_obr_participante():
    return [
        {
            "type": "section",
            "bg": "yellow-secondary",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Área do Participante</span>', "yang"),
                _txt('<span class="text-large text-yang">Tudo o que você precisa para participar da OBR</span>', "yang"),
            ]
        },
        _sec([
            _txt("""## Como participar da OBR?

**1.** Acesse o **Sistema Olimpo** e crie sua conta em https://olimpo.robocup.org.br/

**2.** Encontre o evento da **OBR** da sua região e modalidade preferida

**3.** Forme sua equipe (quando necessário) e realize a inscrição

**4.** Aguarde as comunicações do seu representante estadual ou coordenador de modalidade

**5.** Prepare-se e divirta-se! 🤖

## Materiais de Apoio"""),
        ], margin_y="2"),
        _sec([
            {"type": "dynamic_arquivos", "tag_ids": [], "pagination": False, "limit": 10,
             "theme_primary": "yellow", "theme_secondary": "yellow-secondary", "theme_foreground": "yang"}
        ]),
        _sec([
            _btn_rounded("Inscreva-se no Olimpo", "https://olimpo.robocup.org.br/", "yellow-secondary"),
        ], margin_y="1/"),
    ]


def page_obr_faq():
    return [
        {
            "type": "section",
            "bg": "yellow-secondary",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Perguntas Frequentes</span>', "yang"),
                _txt('<span class="text-large text-yang">Tire suas dúvidas sobre a OBR</span>', "yang"),
            ]
        },
        {
            "type": "accordion",
            "items": [
                {
                    "title": "Quem pode participar da OBR?",
                    "content": "A OBR é aberta a alunos do ensino fundamental, médio e técnico de todo o Brasil. Cada modalidade tem suas próprias faixas etárias e categorias."
                },
                {
                    "title": "A participação é gratuita?",
                    "content": "A Modalidade Teórica é gratuita para os alunos. As modalidades práticas podem ter taxas de inscrição variáveis por edição. Consulte o edital do ano vigente."
                },
                {
                    "title": "Como me inscrever?",
                    "content": "As inscrições são realizadas pelo Sistema Olimpo (https://olimpo.robocup.org.br/). Crie sua conta, localize o evento OBR e siga as instruções."
                },
                {
                    "title": "Preciso saber programar para participar?",
                    "content": "Para a Modalidade Teórica, não é necessário saber programar. Para as modalidades práticas, é recomendado ter conhecimentos básicos de programação e eletrônica, mas os manuais orientam passo a passo."
                },
                {
                    "title": "Quantos alunos formam uma equipe?",
                    "content": "O número de integrantes varia por modalidade. Consulte o manual da modalidade de interesse para verificar as regras de formação de equipes."
                },
                {
                    "title": "Como funciona a fase nacional?",
                    "content": "Os melhores classificados nas etapas regionais são convocados para a fase nacional, realizada durante o Evento Robótica. Em 2026, a fase nacional será em João Pessoa, PB."
                },
                {
                    "title": "Onde encontro os manuais?",
                    "content": "Os manuais estão disponíveis na seção Manuais do site (/obr/manuais) e também no Sistema Olimpo."
                },
                {
                    "title": "Minha escola pode se inscrever?",
                    "content": "Sim! A escola pode se cadastrar como instituição participante no Olimpo. Professores e coordenadores pedagógicos podem gerenciar as inscrições dos alunos."
                },
            ],
            "theme": "obr"
        },
        _sec([
            _btn_inline("Contato OBR", "/contato", color="yellow-secondary"),
            _btn_inline("Inscreva-se", "https://olimpo.robocup.org.br/", color="yellow"),
        ], gap="1", margin_y="2"),
    ]


def page_obr_nacional():
    return [
        {
            "type": "section",
            "bg": "yellow-secondary",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [
                {"type": "obr", "color": "yellow-secondary", "position": "bottom right", "spin": True, "container": True, "desktop_only": True}
            ],
            "components": [
                _txt('<span class="text-small text-yang text-500">EVENTO NACIONAL OBR</span>', "yang"),
                _txt('<span class="text-xxxxlarge text-900 text-yang"><i>Robótica 2026</i></span>', "yang"),
                _txt('<span class="text-xlarge text-yang">João Pessoa — PB • Fase Nacional da OBR</span>', "yang"),
                _btn_rounded("Mais informações sobre a sede", "/sede/2026", "yang"),
            ]
        },
        {
            "type": "tabs",
            "tabs": [
                {
                    "id": "tab-resgate",
                    "label": "Resgate",
                    "content": '<div class="container padding-y-2"><h3>Robótica de Resgate — Fase Nacional</h3><p class="text-medium text-300">A fase nacional da modalidade de Resgate acontece durante o Evento Robótica em João Pessoa. As equipes classificadas nas etapas regionais se enfrentam em desafios de labirinto ao vivo.</p></div>'
                },
                {
                    "id": "tab-artistica",
                    "label": "Artística",
                    "content": '<div class="container padding-y-2"><h3>Robótica Artística — Fase Nacional</h3><p class="text-medium text-300">As equipes apresentam suas performances artísticas para uma banca de avaliadores. Criatividade, sincronização e programação são os critérios avaliados.</p></div>'
                },
                {
                    "id": "tab-virtual",
                    "label": "Virtual",
                    "content": '<div class="container padding-y-2"><h3>Robótica Virtual — Fase Nacional</h3><p class="text-medium text-300">A modalidade virtual pode ser realizada presencialmente ou à distância, conforme as regras do edital vigente. Consulte o manual da modalidade.</p></div>'
                },
                {
                    "id": "tab-teorica",
                    "label": "Teórica",
                    "content": '<div class="container padding-y-2"><h3>Modalidade Teórica — Fase Nacional</h3><p class="text-medium text-300">Os melhores classificados na fase regional são convocados para a prova nacional, realizada presencialmente durante o Evento Robótica.</p></div>'
                },
                {
                    "id": "tab-docs",
                    "label": "Documentos",
                    "content": '<div class="container padding-y-2"><h3>Documentos da Fase Nacional</h3><p class="text-medium text-300">Consulte os documentos e manuais aplicáveis à fase nacional da OBR.</p></div>'
                },
            ],
            "style": "obr"
        },
    ]


def page_obr_mundo_robotica():
    return [
        {
            "type": "section",
            "bg": "yellow-secondary",
            "main": {"container": True, "classes": "padding-y-3"},
            "border_details": [],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Mundo Robótica</span>', "yang"),
                _txt('<span class="text-large text-yang">A revista oficial da RoboCup Brasil — divulgação científica para todos os públicos</span>', "yang"),
            ]
        },
        _sec([
            _txt("""## Sobre a Revista Mundo Robótica

A **Mundo Robótica** é a publicação oficial da RoboCup Brasil, com conteúdo acessível sobre robótica, inteligência artificial, tecnologia e inovação. Leia online as edições anteriores abaixo."""),
        ], margin_y="1/"),
        _sec([
            {"type": "dynamic_arquivos", "tag_ids": [], "pagination": True, "limit": 12,
             "theme_primary": "yellow", "theme_secondary": "yellow-secondary", "theme_foreground": "yang"}
        ]),
    ]



def page_cbr_home():
    return [
        {
            "type": "section",
            "bg": "gray-secondary",
            "main": {"container": True, "classes": "padding-y-5"},
            "border_details": [
                {"type": "cbr", "color": "gray-secondary", "position": "bottom left", "container": True, "desktop_only": True}
            ],
            "components": [
                {"type": "imagem", "imagem": "/static/images/header/cbr.png", "titulo": "Logo CBR",
                 "clicavel": False, "rounded": False, "classes": "h-3 object-contain"},
                _txt('<span class="text-xxxxlarge text-900 text-yang">Competição Brasileira de Robótica</span>', "yang"),
                _txt('<span class="text-xlarge text-300 text-yang">A mais importante competição de robótica da América Latina</span>', "yang"),
                _btn_rounded("Participe — Inscreva-se no Olimpo", "https://olimpo.robocup.org.br/", "yang"),
            ]
        },
        _sec([
            _txt("""## O que é a CBR?

A **Competição Brasileira de Robótica (CBR)** é a principal competição de robótica para alunos do ensino médio e superior da América Latina. Com ligas da **RoboCup Federation** e ligas nacionais, a CBR reúne quase **200 universidades** e centenas de equipes de todo o Brasil."""),
        ], margin_y="2"),
        _sec([
            {"type": "slider_subeventos", "evento": "CBR", "title": "Ligas da CBR",
             "theme_primary": "gray", "theme_foreground": "yang", "theme_secondary": "gray-secondary", "limit": 20}
        ], container=False, inside_bottom=True),
        _sec([
            {"type": "slider_arquivos", "tags": [], "title": "Fotos CBR",
             "theme_primary": "yin", "theme_foreground": "yang", "theme_secondary": "gray", "limit": 8}
        ], container=False, inside_bottom=True),
        _sec([
            _hdr("Notícias CBR", theme="cbr", alignment="start"),
        ], margin_y="1/"),
        _sec([
            {"type": "dynamic_noticias", "tag_ids": [2], "pagination": False, "limit": 3,
             "theme_foreground": "yang", "theme_primary": "gray", "theme_secondary": "gray-secondary"},
            _btn_inline("Todas as Notícias CBR", "/cbr/noticias", color="gray-secondary"),
        ], gap="1"),
    ]


def page_cbr_sobre():
    return [
        {
            "type": "section",
            "bg": "gray-secondary",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [
                {"type": "cbr", "color": "gray-secondary", "position": "bottom left", "container": True, "desktop_only": True}
            ],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Sobre a CBR</span>', "yang"),
                _txt('<span class="text-large text-yang">Competição Brasileira de Robótica — história e estrutura</span>', "yang"),
            ]
        },
        _sec([
            _txt("""## Sobre a CBR

A **Competição Brasileira de Robótica (CBR)** é um evento anual realizado pela RoboCup Brasil que reúne equipes de alunos do ensino médio e superior para competir em diversas ligas de robótica.

A CBR conta com ligas da **RoboCup Federation** — a organização mundial de robótica — e ligas nacionais criadas especificamente para o contexto brasileiro. As competições abrangem desde futebol de robôs e robótica doméstica até drones e robótica industrial.

## Estrutura

As ligas da CBR são organizadas em categorias de complexidade e autonomia crescente, cobrindo os principais sub-campos da robótica:

- **Ligas de Futebol de Robôs**: Small Size, Simulation 2D/3D, Humanoid
- **Ligas de Serviço**: RoboCup@Home, RoboCup@Work
- **Ligas Nacionais**: Flying Robots, RCB Challenge
- **Ligas Junior**: Rescue Maze, Rescue Simulation, Soccer Lightweight/Open"""),
        ], margin_y="2"),
        _sec([
            {"type": "slider_arquivos", "tags": [], "title": "Fotos CBR",
             "theme_primary": "gray", "theme_foreground": "yang", "theme_secondary": "gray-secondary", "limit": 8}
        ], container=False, inside_bottom=True),
    ]


def page_cbr_ligas():
    ligas = [
        ("RoboCup Small Size Soccer", "/static/images/management/default_files/placeholder.png"),
        ("RoboCup Simulation 2D", "/static/images/management/default_files/placeholder.png"),
        ("RoboCup Simulation 3D", "/static/images/management/default_files/placeholder.png"),
        ("RoboCup Humanoid League", "/static/images/management/default_files/placeholder.png"),
        ("RoboCup@Work", "/static/images/management/default_files/placeholder.png"),
        ("RoboCup@Home", "/static/images/management/default_files/placeholder.png"),
        ("RCB Flying Robots League", "/static/images/management/default_files/placeholder.png"),
        ("RCB Challenge", "/static/images/management/default_files/placeholder.png"),
        ("RoboCupJunior Rescue Maze", "/static/images/management/default_files/placeholder.png"),
        ("RoboCupJunior Rescue Simulation", "/static/images/management/default_files/placeholder.png"),
        ("RoboCupJunior Soccer Lightweight", "/static/images/management/default_files/placeholder.png"),
        ("RoboCupJunior Soccer Open", "/static/images/management/default_files/placeholder.png"),
    ]
    cards_html = ""
    for nome, _ in ligas:
        cards_html += f"""<a href="/evento/{slugify(nome, allow_unicode=True)}" style="display:flex;flex-direction:column;align-items:center;gap:.75rem;padding:1.5rem;background:#f4fcfc;border-radius:1rem;box-shadow:0 0 4px rgba(0,0,0,.1);text-decoration:none;color:#2c2e35;transition:all .3s ease;min-width:200px;flex:1">
  <img src="/static/images/management/default_files/placeholder.png" style="height:4rem;width:4rem;object-fit:contain;opacity:.6" alt="{nome}">
  <span style="font-weight:600;text-align:center;font-size:.95rem">{nome}</span>
</a>"""
    return [
        {
            "type": "section",
            "bg": "gray-secondary",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [
                {"type": "cbr", "color": "gray-secondary", "position": "bottom right", "container": True, "desktop_only": True}
            ],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Ligas da CBR</span>', "yang"),
                _txt('<span class="text-large text-yang">Conheça todas as modalidades competitivas da Competição Brasileira de Robótica</span>', "yang"),
            ]
        },
        _sec([
            _txt("""## Ligas da CBR

Cada liga tem suas próprias regras, categorias e calendário. Clique em uma liga para ver mais informações sobre ela."""),
        ], margin_y="1/"),
        {
            "type": "section",
            "main": {"container": True},
            "border_details": [],
            "classes": "margin-y-2",
            "components": [
                {"type": "html", "html": f'<div style="display:flex;flex-wrap:wrap;gap:1rem;">{cards_html}</div>'}
            ]
        }
    ]


def page_cbr_tdp():
    return [
        {
            "type": "section",
            "bg": "gray-secondary",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [
                {"type": "cbr", "color": "gray-secondary", "position": "bottom left", "container": True, "desktop_only": True}
            ],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Team Description Paper</span>', "yang"),
                _txt('<span class="text-large text-yang">O documento técnico que apresenta sua equipe e tecnologia</span>', "yang"),
            ]
        },
        _sec([
            _txt("""## O que é o TDP?

O **Team Description Paper (TDP)** é um documento técnico obrigatório para as equipes participantes da CBR. Nele, a equipe descreve suas tecnologias, abordagens de programação, arquitetura do robô e resultados esperados.

## Por que o TDP é importante?

- É um requisito de inscrição na maioria das ligas da CBR
- Permite que os juízes conheçam sua equipe antes da competição
- Contribui para o registro científico das competições de robótica no Brasil
- É uma ótima oportunidade de exercitar a escrita técnica e científica

## Estrutura do TDP

Um TDP típico inclui:
1. **Resumo** da equipe e objetivos
2. **Descrição do hardware** — mecânica e eletrônica do robô
3. **Descrição do software** — algoritmos, linguagens e frameworks utilizados
4. **Estratégias de jogo/desempenho**
5. **Resultados de testes** e experimentos
6. **Trabalhos futuros**

## Modelo Oficial"""),
        ], margin_y="2"),
        _sec([
            {"type": "dynamic_arquivos", "tag_ids": [], "pagination": False, "limit": 5,
             "theme_primary": "gray", "theme_secondary": "gray-secondary", "theme_foreground": "yang"}
        ]),
        _sec([
            _btn_rounded("Submeter TDP no Olimpo", "https://olimpo.robocup.org.br/", "gray"),
        ], margin_y="1/"),
    ]


def page_cbr_pagamentos():
    return [
        {
            "type": "section",
            "bg": "gray-secondary",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Pagamentos e Taxas</span>', "yang"),
                _txt('<span class="text-large text-yang">Valores de inscrição por modalidade e período</span>', "yang"),
            ]
        },
        _sec([
            _txt("""## Taxas de Inscrição CBR

Os valores de inscrição da CBR variam conforme o **período de registro** e o **tipo de participante**. Registros antecipados têm desconto.

### Períodos de Registro

| Período | Datas (aproximadas) | Desconto |
|---------|-------------------|---------|
| **Early Registration** | Até 3 meses antes do evento | ~30% off |
| **Regular Registration** | Até 1 mês antes do evento | Preço cheio |
| **Late Registration** | Última semana | +10% |

---

### Taxas por Categoria (valores indicativos — consulte o edital vigente)

**Participante Individual**

| Período | Estudante | Profissional |
|---------|-----------|-------------|
| Early | R$ 80,00 | R$ 120,00 |
| Regular | R$ 110,00 | R$ 160,00 |
| Late | R$ 130,00 | R$ 180,00 |

**Por Equipe (taxa por liga)**

| Período | Equipe Junior | Equipe Adulto |
|---------|--------------|--------------|
| Early | R$ 150,00 | R$ 200,00 |
| Regular | R$ 200,00 | R$ 260,00 |
| Late | R$ 240,00 | R$ 300,00 |

---

> ⚠️ **Atenção:** Os valores acima são indicativos. Consulte sempre o **edital oficial** no Sistema Olimpo para os valores exatos da edição vigente.

## Como Pagar

Os pagamentos são realizados exclusivamente pelo **Sistema Olimpo** (https://olimpo.robocup.org.br/). São aceitos boleto bancário, PIX e cartão de crédito."""),
        ], margin_y="2"),
        _sec([
            _btn_rounded("Realizar Inscrição no Olimpo", "https://olimpo.robocup.org.br/", "gray"),
        ], margin_y="1/"),
    ]


def page_mnr_home():
    return [
        {
            "type": "section",
            "bg": "green-secondary",
            "main": {"container": True, "classes": "padding-y-5"},
            "border_details": [
                {"type": "mnr", "color": "green-secondary", "position": "bottom center"},
            ],
            "components": [
                {"type": "imagem", "imagem": "/static/images/header/mnr.png", "titulo": "Logo MNR",
                 "clicavel": False, "rounded": False, "classes": "h-3 object-contain"},
                _txt('<span class="text-xxxxlarge text-900 text-yang">Mostra Nacional de Robótica</span>', "yang"),
                _txt('<span class="text-xlarge text-300 text-yang">A mais importante mostra de trabalhos de robótica da América Latina</span>', "yang"),
                _btn_rounded("Participe — Inscreva-se no Olimpo", "https://olimpo.robocup.org.br/", "yang"),
            ]
        },
        _sec([
            _txt("""## O que é a MNR?

A **Mostra Nacional de Robótica (MNR)** é a mais importante mostra de trabalhos acadêmicos e científicos de robótica da América Latina. Seus anais reúnem mais de **2.000 trabalhos** do ensino fundamental à pós-graduação.

Na MNR, estudantes e pesquisadores apresentam projetos de robótica, automação, inteligência artificial e áreas afins. É o espaço ideal para divulgar pesquisas, trocar experiências e se conectar com a comunidade científica."""),
        ], margin_y="2"),
        _sec([
            {"type": "slider_arquivos", "tags": [], "title": "Fotos MNR",
             "theme_primary": "green", "theme_foreground": "yang", "theme_secondary": "green-secondary", "limit": 8}
        ], container=False, inside_bottom=True),
        _sec([
            _hdr("Notícias MNR", theme="mnr", alignment="start"),
        ], margin_y="1/"),
        _sec([
            {"type": "dynamic_noticias", "tag_ids": [3], "pagination": False, "limit": 3,
             "theme_foreground": "yang", "theme_primary": "green", "theme_secondary": "green-secondary"},
            _btn_inline("Todas as Notícias MNR", "/mnr/noticias", color="green"),
        ], gap="1"),
    ]


def page_mnr_sobre():
    return [
        {
            "type": "section",
            "bg": "green-secondary",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [
                {"type": "mnr", "color": "green-secondary", "position": "bottom center"},
            ],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Sobre a MNR</span>', "yang"),
                _txt('<span class="text-large text-yang">Mostra Nacional de Robótica — história, missão e estrutura</span>', "yang"),
            ]
        },
        _sec([
            _txt("""## Sobre a Mostra Nacional de Robótica

A **Mostra Nacional de Robótica (MNR)** é um evento científico anual que promove a divulgação de projetos de robótica, automação e inteligência artificial para estudantes de todos os níveis de ensino.

Desde sua criação, a MNR vem crescendo e se consolidando como o principal espaço de intercâmbio científico em robótica do Brasil. O evento é composto por duas modalidades:

### Modalidades

**🖥️ Mostra Virtual**
Apresentação de trabalhos em formato online, permitindo a participação de equipes de todo o Brasil e do exterior.

**🏛️ Mostra Presencial**
Apresentação presencial de projetos durante o Evento Robótica, com avaliação por banca de especialistas.

### Anais

Os trabalhos aprovados são publicados nos **Anais da MNR**, um dos maiores repositórios de produção científica em robótica do Brasil, com mais de 2.000 trabalhos indexados."""),
        ], margin_y="2"),
        _sec([
            {"type": "slider_arquivos", "tags": [], "title": "Fotos MNR",
             "theme_primary": "green", "theme_foreground": "yang", "theme_secondary": "green-secondary", "limit": 8}
        ], container=False, inside_bottom=True),
    ]


def page_mnr_documentos():
    return [
        {
            "type": "section",
            "bg": "green-secondary",
            "main": {"container": True, "classes": "padding-y-3"},
            "border_details": [],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Documentos MNR</span>', "yang"),
                _txt('<span class="text-large text-yang">Manuais, regulamentos e formulários oficiais da MNR</span>', "yang"),
            ]
        },
        _sec([
            _txt('<span class="text-xxlarge text-700">Documentos Gerais</span>'),
        ], margin_y="1/"),
        _sec([
            {"type": "dynamic_arquivos", "tag_ids": [], "pagination": False, "limit": 15,
             "theme_primary": "green", "theme_secondary": "green-secondary", "theme_foreground": "yang"}
        ]),
        _sec([
            _txt('<span class="text-xxlarge text-700">Modelos de Documentos</span>'),
        ], margin_y="1/"),
        _sec([
            {"type": "dynamic_arquivos", "tag_ids": [], "pagination": False, "limit": 10,
             "theme_primary": "green-secondary", "theme_secondary": "green", "theme_foreground": "yang"}
        ]),
    ]


def page_mnr_anais():
    return [
        {
            "type": "section",
            "bg": "green-secondary",
            "main": {"container": True, "classes": "padding-y-3"},
            "border_details": [],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Anais da MNR</span>', "yang"),
                _txt('<span class="text-large text-yang">Repositório de trabalhos científicos em robótica — do fundamental à pós-graduação</span>', "yang"),
            ]
        },
        _sec([
            _txt("""## Anais da Mostra Nacional de Robótica

Os anais da MNR reúnem os trabalhos científicos aprovados e apresentados em cada edição do evento. É o maior repositório de produção científica em robótica do Brasil, com mais de **2.000 trabalhos** indexados.

Utilize os filtros abaixo para encontrar trabalhos por edição, categoria ou tema."""),
        ], margin_y="1/"),
        _sec([
            {"type": "dynamic_arquivos", "tag_ids": [], "pagination": True, "limit": 12,
             "theme_primary": "green", "theme_secondary": "green-secondary", "theme_foreground": "yang"}
        ]),
    ]


def page_mnr_avaliador():
    return [
        {
            "type": "section",
            "bg": "green-secondary",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Seja Avaliador da MNR</span>', "yang"),
                _txt('<span class="text-large text-yang">Contribua com sua expertise para a avaliação dos trabalhos científicos</span>', "yang"),
            ]
        },
        _sec([
            _txt("""## O processo de avaliação

A MNR conta com um rigoroso processo de avaliação por pares, realizado por pesquisadores e profissionais da área de robótica, automação e inteligência artificial.

Cada trabalho submetido é avaliado por ao menos dois avaliadores independentes, que analisam:
- Qualidade científica e metodológica
- Originalidade e inovação
- Clareza e organização da apresentação
- Relevância para a área

## Por que ser avaliador?

- Contribuir para o desenvolvimento da pesquisa em robótica no Brasil
- Receber certificado de avaliador emitido pela RoboCup Brasil
- Contato com os projetos mais inovadores de todo o país
- Integrar a comunidade científica da RoboCup Brasil

## Como se tornar avaliador?

Para confirmar sua participação como avaliador da MNR, envie um e-mail para:

📧 **mnr@robocup.org.br**

Inclua seu nome completo, titulação, área de expertise e currículo Lattes."""),
        ], margin_y="2"),
        _sec([
            _btn_rounded("Contato MNR", "mailto:mnr@robocup.org.br", "green"),
        ], margin_y="1/"),
    ]


def page_mnr_bolsista():
    return [
        {
            "type": "section",
            "bg": "green-secondary",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [
                {"type": "mnr", "color": "green-secondary", "position": "bottom center"},
            ],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Bolsistas da MNR</span>', "yang"),
                _txt('<span class="text-large text-yang">Programa de bolsas para participantes da Mostra Nacional de Robótica</span>', "yang"),
            ]
        },
        _sec([
            _txt("""## Bolsas para Participantes

A MNR oferece bolsas para auxiliar na participação presencial de estudantes e equipes com dificuldades financeiras para comparecer ao evento nacional.

## Quem pode solicitar?

Equipes classificadas para a fase presencial da MNR que apresentem necessidade financeira comprovada podem solicitar auxílio de bolsas para:
- Passagens aéreas ou terrestres
- Hospedagem durante o evento
- Alimentação durante os dias de competição

## Como solicitar?

O processo de solicitação de bolsas é realizado após a classificação para a fase nacional, seguindo o edital específico publicado no Sistema Olimpo.

Principais etapas:
1. Classificar-se para a fase presencial da MNR
2. Acessar o sistema Olimpo e verificar se há edital de bolsas aberto
3. Preencher o formulário de solicitação com os documentos requeridos
4. Aguardar análise e resposta da equipe organizadora

## Critérios de seleção

A seleção leva em conta:
- Classificação na fase regional
- Distância entre a cidade de origem e a sede do evento
- Situação socioeconômica comprovada
- Histórico de participação na MNR

## Mais informações

Para dúvidas sobre o programa de bolsas, entre em contato:

📧 **mnr@robocup.org.br**"""),
        ], margin_y="2"),
        _sec([
            _btn_rounded("Acessar o Olimpo", "https://olimpo.robocup.org.br/", "green"),
        ], margin_y="1/"),
    ]


def page_chamadas():
    return [
        {
            "type": "section",
            "bg": "blue",
            "main": {"container": True, "classes": "padding-y-4"},
            "border_details": [
                {"type": "rcb", "color": "blue", "position": "bottom right", "spin": True, "container": True, "desktop_only": True}
            ],
            "components": [
                _txt('<span class="text-xxxlarge text-700 text-yang">Chamadas</span>', "yang"),
                _txt('<span class="text-large text-yang">Chamadas para organizadores, representantes e voluntários dos eventos RoboCup Brasil</span>', "yang"),
            ]
        },
        _sec([
            _txt("""## Chamadas Abertas

Esta página reúne as chamadas ativas para organizadores locais, representantes estaduais e demais colaboradores dos eventos da RoboCup Brasil.

### Chamada para Organizador Nacional (LOC) — Robótica 2027

A RoboCup Brasil abre chamada para propostas de sede para o **Evento Robótica 2027**. Cidades e instituições interessadas devem enviar proposta conforme o edital disponível.

**Documentos necessários:**
- Carta de intenção assinada pela instituição parceira
- Proposta de local para realização do evento (capacidade mínima: 1.500 participantes simultâneos)
- Carta de apoio da prefeitura ou governo estadual
- Curriculum da equipe organizadora local

**Prazo de submissão:** A definir

---

### Chamada para Representantes Estaduais — OBR/MNR 2026

A RoboCup Brasil busca representantes estaduais para coordenar as etapas regionais da OBR e MNR nos estados sem representação ativa.

**Perfil buscado:**
- Docente ou pesquisador vinculado a instituição de ensino
- Experiência com organização de eventos científicos ou competições
- Comprometimento com o calendário da RoboCup Brasil

Para se candidatar, envie e-mail para **contato@robocup.org.br** com o assunto *"Chamada Representante Estadual 2026 — [SEU ESTADO]"*."""),
        ], margin_y="2"),
    ]



# ─── Command class ─────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = "Create default sedes, subeventos, tags, pages and global config"

    def handle(self, *args, **options):
        with transaction.atomic():
            self.create_sedes()
            self.create_subeventos()
            self.create_tags()
            self.create_paginas_estados()
            self.create_configuracao_global()
            self.create_paginas_dinamicas()
            self.create_arquivos()
            self.create_menus()
            self.create_funcionarios_dummy()
            self.create_arquivos_dummy()
            self.create_datas_dummy()

        self.stdout.write(self.style.SUCCESS("Default data setup completed successfully!"))

    # ── Sedes ─────────────────────────────────────────────────────────────────

    def create_sedes(self):
        import os
        from django.core.files.base import ContentFile

        sedes = [
            ('2007', 'Florianópolis', 'SC'),
            ('2008', 'Salvador', 'BA'),
            ('2009', 'Brasília', 'DF'),
            ('2010', 'São Bernardo do Campo', 'SP'),
            ('2011', 'São João del Rei', 'MG'),
            ('2012', 'Fortaleza', 'CE'),
            ('2013', 'Fortaleza', 'CE'),
            ('2014', 'São Carlos', 'SP'),
            ('2015', 'Uberlândia', 'MG'),
            ('2016', 'Recife', 'PE'),
            ('2017', 'Curitiba', 'PR'),
            ('2018', 'João Pessoa', 'PB'),
            ('2019', 'Rio Grande', 'RS'),
            ('2022', 'São Bernardo do Campo', 'SP'),
            ('2023', 'Salvador', 'BA'),
            ('2024', 'Goiânia', 'GO'),
            ('2025', 'Vitória', 'ES'),
            ('2026', 'João Pessoa', 'PB'),
            ('2027', 'Porto Alegre', 'RS'),
        ]

        placeholder_path = os.path.join(
            settings.BASE_DIR, 'app', 'management', 'default_files', 'placeholder.png'
        )

        created = 0
        for ano, cidade, estado in sedes:
            if ano == '2026':
                componentes = page_sede_atual()
            else:
                componentes = page_sede_passada(ano, cidade, estado)

            obj, c = Sede.objects.update_or_create(
                ano=ano,
                defaults={'cidade': cidade, 'estado': estado, 'componentes': componentes}
            )
            # Set placeholder photo if not already set
            if not obj.foto and os.path.isfile(placeholder_path):
                try:
                    with open(placeholder_path, 'rb') as f:
                        obj.foto.save(f'sede_{ano}.png', ContentFile(f.read()), save=True)
                except Exception:
                    pass
            if c:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Sedes ensured ({created} created/updated)."))

    # ── Subeventos ────────────────────────────────────────────────────────────

    def create_subeventos(self):
        import os
        from django.core.files.base import ContentFile

        subeventos = [
            ('Mostra Virtual', 'MNR'),
            ('Mostra Presencial', 'MNR'),
            ('Modalidade Teórica', 'OBR'),
            ('Robótica de Resgate', 'OBR'),
            ('Robótica Virtual', 'OBR'),
            ('Robótica Artística', 'OBR'),
            ('RoboCup Small Size Soccer', 'CBR'),
            ('RoboCup Simulation 2D', 'CBR'),
            ('RoboCup Simulation 3D', 'CBR'),
            ('RoboCup Humanoid League', 'CBR'),
            ('RoboCup@Work', 'CBR'),
            ('RoboCup@Home', 'CBR'),
            ('RCB Flying Robots League', 'CBR'),
            ('RCB Challenge', 'CBR'),
            ('RoboCupJunior Rescue Maze', 'CBR'),
            ('RoboCupJunior Rescue Simulation', 'CBR'),
            ('RoboCupJunior Soccer Lightweight', 'CBR'),
            ('RoboCupJunior Soccer Open', 'CBR'),
        ]

        placeholder_path = os.path.join(
            settings.BASE_DIR, 'app', 'management', 'default_files', 'placeholder.png'
        )

        created = 0
        for nome, evento in subeventos:
            obj, c = Subevento.objects.update_or_create(
                nome=nome, defaults={'evento': evento, 'componentes': []}
            )
            if not obj.icone and os.path.isfile(placeholder_path):
                try:
                    with open(placeholder_path, 'rb') as f:
                        obj.icone.save(f'{slugify(nome)}.png', ContentFile(f.read()), save=True)
                except Exception:
                    pass
            if c:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Subeventos ensured ({created} created/updated)."))

    # ── Tags ──────────────────────────────────────────────────────────────────

    def create_tags(self):
        from app.models import Regiao
        tag_arquivos = [
            'Design do Site',
            'Material do Organizador Regional (REP)',
            'Material do Organizador Nacional (LOC)',
            'Material de Divulgação IDV',
            'Material IDV OBR',
            'Material IDV CBR',
            'Material IDV MNR',
            'Material Extra OBR',
            'Material Edição 2026',
            'Manual OBR Documentos Gerais',
            'Manual OBR Teórica',
            'Manual OBR Prática Resgate',
            'Manual OBR Prática Artística',
            'Manual OBR Prática Virtual',
            'Manual OBR Aplicável à Nacional',
            'Gabarito OBR',
            'Prova OBR',
            'Documento Genérico MNR',
            'Modelo MNR',
            'TDP CBR',
            'Anais MNR',
            'Revista Mundo Robótica',
            'Fotos CBR',
            'Fotos OBR',
            'Fotos MNR',
        ]
        tag_datas = [
            'OBR', 'CBR', 'MNR', 'evento local', 'evento nacional', 'inscrição',
            'envio de tdp', 'envio de artigo/resumo', 'correção', 'aplicação de provas',
            '2ª fase', 'evento associado', 'evento patrocinador', 'LARS'
        ]
        tag_funcionarios = [
            'OBR', 'CBR', 'MNR', 'Presidência', 'Vice-Presidência', 'Curador (Trustee)',
            'Chair / Coordenador de Modalidade', 'General Chair / Coordenação de Evento',
            'Representante Local', 'Secretaria', 'TI', 'Comunicação',
            'Coordenação Administrativa', 'Prestador de Serviço',
        ]
        tag_noticias = [
            'OBR', 'CBR', 'MNR', 'LARS', 'Inscrições', 'Resultados', 'Editais',
            'Notas Oficiais', 'Internacional', 'Calendário', 'Institucional',
            'Pós-Evento', 'Tecnologia', 'Voluntariado', 'Patrocinador'
        ]

        for nome in tag_arquivos:
            TagArquivo.objects.get_or_create(nome=nome)
        for nome in tag_datas:
            TagData.objects.get_or_create(nome=nome)
        for code, name in Regiao.choices:
            TagData.objects.get_or_create(nome=name)
        for nome in tag_funcionarios:
            TagFuncionario.objects.get_or_create(nome=nome)
        for nome in tag_noticias:
            TagNoticia.objects.get_or_create(nome=nome)

        self.stdout.write(self.style.SUCCESS("Tags ensured."))

    # ── PaginaEstado ──────────────────────────────────────────────────────────

    def create_paginas_estados(self):
        from app.models import Regiao
        created = 0
        default_components = [
            _sec([
                _txt("# Página do Representante Estadual\n\nAqui, o representante estadual poderá publicar datas, calendário e informações relevantes para sua região.")
            ])
        ]
        for code, name in Regiao.choices:
            obj, c = PaginaEstado.objects.update_or_create(
                estado=code,
                defaults={'componentes': default_components}
            )
            if c:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Páginas de estados ensured ({created} created)."))

    # ── ConfiguracaoGlobal ────────────────────────────────────────────────────

    def create_configuracao_global(self):
        defaults = {
            'descricao': "Principal associação e maior produtora de eventos de robótica e inteligência artificial do país. Inclui desde o famoso futebol de robôs à simulações de resgate e robôs domésticos, capacitando estudantes do ensino fundamental à pós-graduação.",
            'instagram': "https://www.instagram.com/robocupbrasil/",
            'facebook': "https://www.facebook.com/robocupbrasil/",
            'youtube': "https://www.youtube.com/robocupbrasil",
            'linkedin': "https://www.linkedin.com/company/robocupbrasil/",
            'email_contato': "contato@robocup.org.br",
            'outros_emails': "obr@robocup.org.br cbr@robocup.org.br mnr@robocup.org.br",
            'logo_link_cbr': "/cbr",
            'logo_link_mnr': "/mnr",
            'logo_link_obr': "/obr",
        }

        obj, created = ConfiguracaoGlobal.objects.update_or_create(defaults=defaults)

        atalhos = [
            ('Página Inicial', '/'),
            ('Identidade Visual', '/material-de-divulgacao'),
            ('Associados', '/associados'),
            ('OBR', '/obr'),
            ('CBR', '/cbr'),
            ('MNR', '/mnr'),
        ]

        for nome, link in atalhos:
            AtalhoGlobal.objects.get_or_create(config=obj, nome=nome, defaults={'link': link})

        if created:
            self.stdout.write(self.style.SUCCESS("Configuração global created."))
        else:
            self.stdout.write(self.style.SUCCESS("Configuração global exists."))

    # ── Páginas dinâmicas ─────────────────────────────────────────────────────

    def create_paginas_dinamicas(self):
        index_componentes = [{"type":"section","bg":"","main":{"container":False},"components":[{"type":"carousel","style":"yin blue-secondary","tabs":[{"id":"slide-1","label":"Slide 1","image":"/media/arquivos/nao.jpg","content":"<div class=\"container\">\n<br><br><br><br><br><br><br><br><br><br>\n<span class=\"text-xlarge text-700\">Ciência, Tecnologia e Inovação aliadas à <i>Educação</i></span>\n\n<span class=\"text-large text-500\">A RoboCup busca fornecer desafios padrão nas quais uma ampla gama de tecnologias pode ser integrada, testada e avaliada.</span>\n<br><br><br><br><br><br><br><br><br><br>\n</div>"},{"id":"tab-2","label":"Slide 2","icon":"","content":"<div class=\"container\">\n<br><br><br><br><br><br><br><br><br><br>\n<span class=\"text-xlarge text-700\">Robótica e Inteligência Artificial ao alcance do <i>grande público</i></span>\n\n<span class=\"text-large text-500\">As ações da RoboCup são, por princípio, ações de Divulgação Científica, que buscam levar o limiar da C,T&I para próximo do grande público </span>\n<br><br><br><br><br><br><br><br><br><br>\n</div>","image":"/media/arquivos/msl.jpg"},{"id":"tab-3","label":"Slide 3","icon":"","content":"<div class=\"container\">\n<br><br><br><br><br><br><br><br><br><br>\n<span class=\"text-xlarge text-700\">Desenvolvimento de novas tecnologias para as necessidades do <i>futuro</i></span>\n\n<span class=\"text-large text-500\">As provas da RoboCup estimulam o desenvolvimento conjunto da mecânica, elétrica e computação, em compasso com os novos desafios da modernindade.</span>\n<br><br><br><br><br><br><br><br><br><br>\n</div>","image":"/media/arquivos/drone.jpg"},{"id":"tab-4","label":"Slide 4","icon":"","content":"<div class=\"container\">\n<br><br><br><br><br><br><br><br><br><br>\n<span class=\"text-xlarge text-700\">Desafios personalizados com a <i>cara do Brasil</i></span>\n\n<span class=\"text-large text-500\">A Robocup Brasil desenvolve parcerias com empresas nacionais para estimular o desenvolvimento de C,T&I voltadas para as necessidades da indústria nacional.</span>\n<br><br><br><br><br><br><br><br><br><br>\n</div>","image":"/media/arquivos/arenadrone.jpg"},{"id":"tab-5","label":"Slide 5","icon":"","content":"<div class=\"container\">\n<br><br><br><br><br><br><br><br><br><br>\n<span class=\"text-xlarge text-700\">Levando a prática da robótica a <i>milhares de escolas</i> em todo o país</span>\n\n<span class=\"text-large text-500\">A RoboCup possui provas práticas estimulantes para jovens a partir do ensino fundamental.</span>\n<br><br><br><br><br><br><br><br><br><br>\n</div>","image":"/media/arquivos/obr.jpg"}]}],"border_details":[{"type":"rcb","color":"blue","position":"bottom right","spin":True,"container":True,"desktop_only":True}],"padding":"0","container":False,"padding_x":"1/"},{"type":"section","bg":"","main":{"container":True},"components":[{"type":"header","titulo":"Nossos Projetos","theme":"rcb","alignment":"start","size":"xxlarge"}],"border_details":[],"margin_t":"4","margin_b":"5","classes":"margin-t-3/ margin-b-5"},{"type":"section","bg":"yin","main":{"container":True},"components":[{"type":"dynamic_texto","theme_foreground":"yang","conteudo":"<span class=\"text-large-plus\">Para alunos do ensino médio e superior:</span>"}],"border_details":[{"type":"cbr","color":"yin","position":"bottom center","mobile_only":True,"size":"small"},{"type":"cbr","color":"yin","position":"bottom left","container":True,"desktop_only":True}],"classes":"margin-t-3 margin-b-5 desktop:margin-b-0"},{"type":"section","bg":"","main":{"container":True,"gap":"1/"},"components":[{"type":"header","theme":"cbr","alignment":"end","titulo":"Competição Brasileira de Robótica PETROBRAS","classes":"text-600"}],"border_details":[],"classes":"padding-t-2/ desktop:padding-t-4"},{"type":"section","bg":"","main":{"container":True},"components":[{"type":"conteudo_square","imagem":"/static/images/favicon/cbr.png","descricao":"<div class=\"text-300 margin-b-1 text-large-plus-plus\">A mais importante competição de robótica da América Latina. Com a participação de quase 200 Universidades e com provas da RoboCup Federation.</div>","text_align":"start","image_align_mobile":"top","image_align_desktop":"right","inline_text":"Conheça e Participe","inline_href":"/cbr","theme_primary":"yang","theme_secondary":"yang","classes":"icon-image","theme_foreground":"yin","inline_color":"gray-secondary","inline_theme":"yang","titulo":" "}],"border_details":[],"margin_y":"1/"},{"type":"section","main":{"container":False,"classes":"padding-y-3"},"components":[{"type":"slider_arquivos","tags":[23],"title":"Imagens CBR","theme_primary":"yin","theme_secondary":"gray","theme_foreground":"yang"}],"border_details":[],"container":False,"inside_bottom":True},{"type":"section","bg":"green-secondary","main":{"container":True,"classes":"padding-t-2 desktop:padding-t-3 margin-b-0"},"components":[{"type":"dynamic_texto","theme_foreground":"yang","conteudo":"<span class=\"text-large-plus\">Para alunos de todos os níveis:</span>"}],"border_details":[]},{"type":"section","bg":"green-secondary","main":{"container":True,"bg":"yang","classes":"border-radius margin-t-0 padding-y-3","padding":"1"},"components":[{"type":"imagem","imagem":"/static/images/header/mnr.png","titulo":"Logo MNR","clicavel":True,"href":"/mnr","rounded":False,"classes":"h-4 object-contain"},{"type":"dynamic_texto","conteudo":"<div class=\"text-align-center text-700 margin-t-1 text-xlarge\">\n<a href=\"/mnr\" style=\"color:inherit\">Mostra Nacional de Robótica</a>\n</div>","theme_foreground":"blue-secondary"}],"border_details":[{"type":"mnr","color":"green-secondary","position":"bottom center"}],"classes":"padding-b-2"},{"type":"section","bg":"","main":{"container":True},"components":[{"type":"conteudo_square","imagem":"/media/arquivos/mnr-home.jpeg","descricao":"<div class=\"text-300 text-large-plus-plus\">Mais importante mostra de trabalhos de Robótica da América Latina. Seus anais contém mais de 2.000 trabalhos do ensino fundamental à pós-graduação.</div>","text_align":"start","image_align_mobile":"bottom","image_align_desktop":"left","inline_text":"Conheça e Participe","inline_href":"/mnr","theme_primary":"yang","theme_secondary":"yang","theme_foreground":"yin","inline_color":"green","inline_theme":"yang","titulo":" "}],"border_details":[],"classes":"padding-b-2 padding-t-5"},{"type":"section","main":{"container":False,"classes":"padding-b-1/"},"components":[{"type":"slider_arquivos","tags":[24],"title":"Imagens OBR","theme_primary":"yellow","theme_secondary":"yellow-secondary","theme_foreground":"yang"}],"border_details":[],"container":False,"inside_bottom":True},{"type":"section","bg":"yellow-secondary","main":{"container":True,"classes":"padding-t-3/ desktop:padding-t-4/"},"components":[{"type":"dynamic_texto","theme_foreground":"yang","conteudo":"<span class=\"text-large-plus\">Para alunos do ensino fundamental ao médio:</span>"}],"border_details":[{"type":"obr","color":"yellow-secondary","position":"bottom right","spin":True,"container":True,"margin_t":"margin-t-5","desktop_only":True},{"type":"obr","color":"yellow-secondary","position":"bottom center","mobile_only":True,"spin":True,"size":"small"}]},{"type":"section","main":{"container":True,"gap":"2"},"components":[{"type":"header","titulo":"Olimpíada Brasileira de Robótica","theme":"obr","alignment":"start","fullwidth":True,"classes":"text-600"}],"border_details":[],"margin_y":"2/","classes":"padding-t-3 desktop:padding-t-0"},{"type":"section","main":{"container":True,"gap":"2"},"components":[{"type":"conteudo_square","imagem":"/static/images/favicon/obr.png","descricao":"<div class=\"text-300 margin-b-1 text-large-plus-plus\">Uma das maiores competições de Robótica do mundo, com mais de 200.000 participantes ano. Voltada para jovens do ensino fundamental, médio e técnico.</div>","text_align":"start","image_align_mobile":"top","image_align_desktop":"right","inline_text":"Conheça e Participe","inline_href":"/obr","theme_primary":"yang","theme_secondary":"yang","classes":"icon-image","theme_foreground":"yin","inline_color":"green-secondary","inline_theme":"yang","titulo":" "}],"border_details":[]},{"type":"section","bg":"","main":{"container":True,"desktop:flex":True,"gap":"2"},"components":[{"type":"conteudo_square","imagem":"/media/arquivos/2026.png","titulo":"Evento Robótica","text_align":"start","image_align_mobile":"top","image_align_desktop":"top","inline_href":"/sede/2026","inline_text":"Mais Informações","descricao":"<span class=\"text-large\">O Robótica reúne competições e congressos nas áreas de robótica e inteligência artificial (IA), com mais de 500 instituições do Brasil e exterior. Em 2026, o evento acontece em João Pessoa, na Paraíba!</span>","color_secondary":"orange","inline_theme":"yang","inline_color":"red-secondary","theme_secondary":"red-secondary","theme_foreground":"yin","classes":"icon-image"},{"type":"conteudo_square","imagem":"/static/images/favicon/olimpo.png","titulo":"Sistema Olimpo","text_align":"start","image_align_mobile":"top","image_align_desktop":"top","inline_href":"https://olimpo.robocup.org.br/","inline_text":"Mais Informações","descricao":"<span class=\"text-large\">O primeiro sistema online especialmente desenvolvido no país para a gestão centralizada de Olimpíadas e eventos científicos de grande porte. Participe já de eventos RoboCup Brasil acessando o Olimpo.</span>","color_secondary":"orange","inline_theme":"yang","inline_color":"blue-secondary","theme_secondary":"blue-secondary","theme_foreground":"yin","classes":"icon-image margin-t-2 desktop:margin-t-0"}],"border_details":[],"container":False},{"type":"section","bg":"","main":{"container":True},"components":[{"type":"header","titulo":"Notícias","theme":"rcb","alignment":"start","size":"xxlarge"}],"border_details":[],"margin_y":"1/"},{"type":"section","bg":"","main":{"container":True,"gap":"3"},"components":[{"type":"dynamic_noticias","tag_ids":[],"pagination":False,"limit":3,"theme_foreground":"yang","theme_primary":"blue","theme_secondary":"blue-secondary"},{"type":"button_inline","texto":"Todas as Notícias","theme":"yin","color":"blue","href":"/noticias","shrink":True,"icon":"newspaper-o"}],"border_details":[]},{"type":"section","bg":"","main":{"container":True},"components":[{"type":"dynamic_calendar","tag_ids":[],"theme_primary":"blue","theme_secondary":"blue-secondary"}],"border_details":[]}]

        pages = [
            {'nome': 'Índice', 'slug': '', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos', 'componentes': index_componentes},
            {'nome': 'Sobre', 'slug': 'sobre', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos', 'componentes': page_sobre_rcb()},
            {'nome': 'Notícias', 'slug': 'noticias', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos', 'componentes': _noticias_page([], "rcb")},
            {'nome': 'Participe', 'slug': 'participe', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos', 'componentes': page_participe()},
            {'nome': 'Associados', 'slug': 'associados', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos', 'componentes': page_associados()},
            {'nome': 'Invista', 'slug': 'invista', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos', 'componentes': page_invista()},
            {'nome': 'Contato', 'slug': 'contato', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos', 'componentes': page_contato()},
            {'nome': 'Voluntários', 'slug': 'voluntarios', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos', 'componentes': page_voluntarios()},
            {'nome': 'Material de Divulgação', 'slug': 'material-de-divulgacao', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos', 'componentes': page_material_divulgacao()},
            {'nome': 'Chamadas', 'slug': 'chamadas', 'header_type': 'RCB', 'privada': True, 'evento_associado': 'Todos', 'componentes': page_chamadas()},
            {'nome': 'Organização Regional', 'slug': 'organizacao-regional', 'header_type': 'RCB', 'privada': True, 'evento_associado': 'Todos', 'componentes': []},
            {'nome': 'Organização Nacional', 'slug': 'organizacao-nacional', 'header_type': 'RCB', 'privada': True, 'evento_associado': 'Todos', 'componentes': []},
        ]

        for p in pages:
            try:
                obj, c = Pagina.objects.update_or_create(
                    slug=p['slug'], parent=None,
                    defaults={
                        'nome': p['nome'], 'parent': None, 'header_type': p['header_type'],
                        'privada': p['privada'], 'evento_associado': p['evento_associado'],
                        'componentes': p['componentes'],
                    }
                )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipping page '{p['slug']}' — {e}"))

        # Parent pages
        parents = [
            {'nome': 'Olimpíada Brasileira de Robótica', 'slug': 'obr', 'header_type': 'OBR', 'evento_associado': 'OBR', 'componentes': page_obr_home()},
            {'nome': 'Competição Brasileira de Robótica', 'slug': 'cbr', 'header_type': 'CBR', 'evento_associado': 'CBR', 'componentes': page_cbr_home()},
            {'nome': 'Mostra Nacional de Robótica', 'slug': 'mnr', 'header_type': 'MNR', 'evento_associado': 'MNR', 'componentes': page_mnr_home()},
            {'nome': 'Robótica', 'slug': 'robotica', 'header_type': 'RCB', 'evento_associado': 'Todos', 'componentes': page_robotica()},
        ]

        for p in parents:
            try:
                Pagina.objects.update_or_create(
                    slug=p['slug'], parent=None,
                    defaults={
                        'nome': p['nome'], 'parent': None, 'header_type': p['header_type'],
                        'componentes': p['componentes'], 'privada': False,
                        'evento_associado': p['evento_associado']
                    }
                )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipping parent '{p['slug']}' — {e}"))

        # Child pages
        children = [
            # OBR
            {'slug': 'sobre', 'parent_slug': 'obr', 'nome': 'Sobre', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR', 'componentes': page_obr_sobre()},
            {'slug': 'manuais', 'parent_slug': 'obr', 'nome': 'Manuais', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR', 'componentes': page_obr_manuais()},
            {'slug': 'participante', 'parent_slug': 'obr', 'nome': 'Participante', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR', 'componentes': page_obr_participante()},
            {'slug': 'noticias', 'parent_slug': 'obr', 'nome': 'Notícias', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR', 'componentes': _noticias_page([1], "obr", "yellow", "yellow-secondary")},
            {'slug': 'modalidades', 'parent_slug': 'obr', 'nome': 'Conheça Nossas Modalidades', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR', 'componentes': page_obr_modalidades()},
            {'slug': 'nacional', 'parent_slug': 'obr', 'nome': 'Evento Nacional', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR', 'componentes': page_obr_nacional()},
            {'slug': 'faq', 'parent_slug': 'obr', 'nome': 'Perguntas Frequentes', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR', 'componentes': page_obr_faq()},
            {'slug': 'mundo-robotica', 'parent_slug': 'obr', 'nome': 'Mundo Robótica', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR', 'componentes': page_obr_mundo_robotica()},
            # CBR
            {'slug': 'sobre', 'parent_slug': 'cbr', 'nome': 'Sobre', 'header_type': 'CBR', 'privada': False, 'evento_associado': 'CBR', 'componentes': page_cbr_sobre()},
            {'slug': 'ligas', 'parent_slug': 'cbr', 'nome': 'Ligas', 'header_type': 'CBR', 'privada': False, 'evento_associado': 'CBR', 'componentes': page_cbr_ligas()},
            {'slug': 'noticias', 'parent_slug': 'cbr', 'nome': 'Notícias', 'header_type': 'CBR', 'privada': False, 'evento_associado': 'CBR', 'componentes': _noticias_page([2], "cbr", "gray", "gray-secondary")},
            {'slug': 'pagamentos', 'parent_slug': 'cbr', 'nome': 'Pagamentos', 'header_type': 'CBR', 'privada': False, 'evento_associado': 'CBR', 'componentes': page_cbr_pagamentos()},
            {'slug': 'tdp', 'parent_slug': 'cbr', 'nome': 'TDP', 'header_type': 'CBR', 'privada': False, 'evento_associado': 'CBR', 'componentes': page_cbr_tdp()},
            # MNR
            {'slug': 'sobre', 'parent_slug': 'mnr', 'nome': 'Sobre', 'header_type': 'MNR', 'privada': False, 'evento_associado': 'MNR', 'componentes': page_mnr_sobre()},
            {'slug': 'documentos', 'parent_slug': 'mnr', 'nome': 'Documentos', 'header_type': 'MNR', 'privada': False, 'evento_associado': 'MNR', 'componentes': page_mnr_documentos()},
            {'slug': 'anais', 'parent_slug': 'mnr', 'nome': 'Anais', 'header_type': 'MNR', 'privada': False, 'evento_associado': 'MNR', 'componentes': page_mnr_anais()},
            {'slug': 'noticias', 'parent_slug': 'mnr', 'nome': 'Notícias', 'header_type': 'MNR', 'privada': False, 'evento_associado': 'MNR', 'componentes': _noticias_page([3], "mnr", "green", "green-secondary")},
            {'slug': 'avaliador', 'parent_slug': 'mnr', 'nome': 'Avaliador', 'header_type': 'MNR', 'privada': False, 'evento_associado': 'MNR', 'componentes': page_mnr_avaliador()},
            {'slug': 'bolsista', 'parent_slug': 'mnr', 'nome': 'Bolsista', 'header_type': 'MNR', 'privada': False, 'evento_associado': 'MNR', 'componentes': page_mnr_bolsista()},
        ]

        for ch in children:
            try:
                parent = Pagina.objects.get(slug=ch['parent_slug'], parent=None)
            except Pagina.DoesNotExist:
                parent = None
            try:
                Pagina.objects.update_or_create(
                    slug=ch['slug'], parent=parent,
                    defaults={
                        'nome': ch['nome'], 'parent': parent, 'header_type': ch['header_type'],
                        'privada': ch['privada'], 'evento_associado': ch['evento_associado'],
                        'componentes': ch['componentes'],
                    }
                )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipping child '{ch['parent_slug']}/{ch['slug']}' — {e}"))

        self.stdout.write(self.style.SUCCESS("Páginas dinâmicas ensured."))

    # ── Arquivos ──────────────────────────────────────────────────────────────

    def create_arquivos(self):
        import os
        default_files_dir = os.path.join(settings.BASE_DIR, 'app', 'management', 'default_files')

        if not os.path.isdir(default_files_dir):
            self.stdout.write(self.style.SUCCESS("No default_files directory found. Skipping arquivo setup."))
            return

        tag_mapping = {
            'design-do-site': 'Design do Site',
            'material-do-organizador-regional-rep': 'Material do Organizador Regional (REP)',
            'material-do-organizador-nacional-loc': 'Material do Organizador Nacional (LOC)',
            'material-de-divulgacao-idv': 'Material de Divulgação IDV',
            'material-extra-obr': 'Material Extra OBR',
            'material-edicao-2026': 'Material Edição 2026',
            'manual-obr-documentos-gerais': 'Manual OBR Documentos Gerais',
            'manual-obr-teorica': 'Manual OBR Teórica',
            'manual-obr-pratica-resgate': 'Manual OBR Prática Resgate',
            'manual-obr-pratica-artistica': 'Manual OBR Prática Artística',
            'manual-obr-pratica-virtual': 'Manual OBR Prática Virtual',
            'manual-obr-aplicavel-a-nacional': 'Manual OBR Aplicável à Nacional',
            'documento-generico-mnr': 'Documento Genérico MNR',
            'modelo-mnr': 'Modelo MNR',
            'tdp-cbr': 'TDP CBR',
            'anais-mnr': 'Anais MNR',
            'revista-mundo-robotica': 'Revista Mundo Robótica',
            'fotos-cbr': 'Fotos CBR',
            'fotos-obr': 'Fotos OBR',
            'fotos-mnr': 'Fotos MNR',
        }

        created = 0
        for folder_slug, tag_name in tag_mapping.items():
            folder_path = os.path.join(default_files_dir, folder_slug)
            if not os.path.isdir(folder_path):
                continue
            try:
                tag = TagArquivo.objects.get(nome=tag_name)
            except TagArquivo.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Tag '{tag_name}' not found. Skipping."))
                continue
            for filename in os.listdir(folder_path):
                filepath = os.path.join(folder_path, filename)
                if not os.path.isfile(filepath) or filename == 'dummy.txt':
                    continue
                obj, c = Arquivo.objects.get_or_create(nome=filename)
                if c:
                    try:
                        with open(filepath, 'rb') as f:
                            obj.arquivo.save(filename, ContentFile(f.read()), save=False)
                            obj.save()
                        obj.tags.add(tag)
                        created += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Error processing '{filename}': {e}"))
                        obj.delete()

        self.stdout.write(self.style.SUCCESS(f"Arquivos ensured ({created} created/updated)."))

    # ── Menus ─────────────────────────────────────────────────────────────────

    def create_menus(self):
        config = ConfiguracaoGlobal.objects.first()
        if not config:
            return

        escondidos = [
            'Modalidade Teórica', 'Modalidades Práticas', 'Perguntas Frequentes',
            'Mundo Robótica', 'Associados', 'Invista', 'Contato', 'Voluntários',
            'Material de Divulgação', 'Avaliador', 'Bolsista',
        ]

        pages_rcb = [
            {'nome': 'Sobre', 'slug': 'sobre'},
            {'nome': 'Evento Robótica', 'slug': 'robotica'},
            {'nome': 'Notícias', 'slug': 'noticias'},
            {'nome': 'Associados', 'slug': 'associados'},
            {'nome': 'Participe', 'slug': 'participe'},
            {'nome': 'Invista', 'slug': 'invista'},
            {'nome': 'Contato', 'slug': 'contato'},
            {'nome': 'Voluntários', 'slug': 'voluntarios'},
            {'nome': 'Material de Divulgação', 'slug': 'material-de-divulgacao'},
        ]
        for p in pages_rcb:
            link = f"/{p['slug']}" if p['slug'] else "/"
            is_hidden = p['nome'] in escondidos
            ItemMenu.objects.get_or_create(
                config=config, header_type='RCB', nome=p['nome'],
                defaults={'link': link, 'escondido': is_hidden}
            )

        children_data = [
            # OBR
            {'slug': 'sobre', 'parent_slug': 'obr', 'nome': 'Sobre', 'header_type': 'OBR'},
            {'slug': 'manuais', 'parent_slug': 'obr', 'nome': 'Manuais', 'header_type': 'OBR'},
            {'slug': 'participante', 'parent_slug': 'obr', 'nome': 'Participante', 'header_type': 'OBR'},
            {'slug': 'noticias', 'parent_slug': 'obr', 'nome': 'Notícias', 'header_type': 'OBR'},
            {'slug': 'modalidades', 'parent_slug': 'obr', 'nome': 'Modalidades Práticas', 'header_type': 'OBR'},
            {'slug': 'faq', 'parent_slug': 'obr', 'nome': 'Perguntas Frequentes', 'header_type': 'OBR'},
            {'slug': 'mundo-robotica', 'parent_slug': 'obr', 'nome': 'Mundo Robótica', 'header_type': 'OBR'},
            # CBR
            {'slug': 'sobre', 'parent_slug': 'cbr', 'nome': 'Sobre', 'header_type': 'CBR'},
            {'slug': 'ligas', 'parent_slug': 'cbr', 'nome': 'Ligas', 'header_type': 'CBR'},
            {'slug': 'noticias', 'parent_slug': 'cbr', 'nome': 'Notícias', 'header_type': 'CBR'},
            {'slug': 'pagamentos', 'parent_slug': 'cbr', 'nome': 'Pagamentos', 'header_type': 'CBR'},
            {'slug': 'tdp', 'parent_slug': 'cbr', 'nome': 'TDP', 'header_type': 'CBR'},
            # MNR
            {'slug': 'sobre', 'parent_slug': 'mnr', 'nome': 'Sobre', 'header_type': 'MNR'},
            {'slug': 'documentos', 'parent_slug': 'mnr', 'nome': 'Documentos', 'header_type': 'MNR'},
            {'slug': 'anais', 'parent_slug': 'mnr', 'nome': 'Anais', 'header_type': 'MNR'},
            {'slug': 'noticias', 'parent_slug': 'mnr', 'nome': 'Notícias', 'header_type': 'MNR'},
            {'slug': 'avaliador', 'parent_slug': 'mnr', 'nome': 'Avaliador', 'header_type': 'MNR'},
            {'slug': 'bolsista', 'parent_slug': 'mnr', 'nome': 'Bolsista', 'header_type': 'MNR'},
        ]
        for item in children_data:
            link = f"/{item['parent_slug']}/{item['slug']}"
            is_hidden = item['nome'] in escondidos
            ItemMenu.objects.get_or_create(
                config=config, header_type=item['header_type'], nome=item['nome'],
                defaults={'link': link, 'escondido': is_hidden}
            )

        self.stdout.write(self.style.SUCCESS("Menus ensured."))

    # ── Funcionários dummy ────────────────────────────────────────────────────

    def create_funcionarios_dummy(self):
        leadership = [
            ('Presidente da RCB', 'Presidência'),
            ('Vice-Presidente de Financeiro', 'Vice-Presidência'),
            ('Vice-Presidente de Eventos', 'Vice-Presidência'),
            ('Vice-Presidente de Comunicação', 'Vice-Presidência'),
            ('Vice-Presidente de Relações Institucionais', 'Vice-Presidência'),
        ]
        created = 0
        for nome, tag_name in leadership:
            try:
                tag = TagFuncionario.objects.get(nome=tag_name)
                obj, c = Funcionario.objects.get_or_create(nome=nome, defaults={'cargo': nome})
                if c:
                    obj.tags.add(tag)
                    created += 1
            except TagFuncionario.DoesNotExist:
                pass

        try:
            curator_tag = TagFuncionario.objects.get(nome='Curador (Trustee)')
            for i in range(1, 9):
                nome = f'Curador {i}'
                obj, c = Funcionario.objects.get_or_create(nome=nome, defaults={'cargo': 'Curador (Trustee)'})
                if c:
                    obj.tags.add(curator_tag)
                    created += 1
        except TagFuncionario.DoesNotExist:
            pass

        try:
            prestador_tag = TagFuncionario.objects.get(nome='Prestador de Serviço')
            for i in range(1, 5):
                nome = f'Prestador de Serviço {i}'
                obj, c = Funcionario.objects.get_or_create(nome=nome, defaults={'cargo': 'Prestador de Serviço'})
                if c:
                    obj.tags.add(prestador_tag)
                    created += 1
        except TagFuncionario.DoesNotExist:
            pass

        other_tags = [
            'OBR', 'CBR', 'MNR', 'Chair / Coordenador de Modalidade',
            'General Chair / Coordenação de Evento', 'Representante Local',
            'Secretaria', 'TI', 'Comunicação', 'Coordenação Administrativa'
        ]
        for tag_name in other_tags:
            try:
                tag = TagFuncionario.objects.get(nome=tag_name)
                for i in range(1, 4):
                    nome = f'{tag_name} {i}'
                    obj, c = Funcionario.objects.get_or_create(nome=nome, defaults={'cargo': tag_name})
                    if c:
                        obj.tags.add(tag)
                        created += 1
            except TagFuncionario.DoesNotExist:
                pass

        self.stdout.write(self.style.SUCCESS(f"Funcionários dummy ensured ({created} created)."))

    # ── Arquivos dummy ────────────────────────────────────────────────────────

    def create_arquivos_dummy(self):
        photo_tags = ['Fotos CBR', 'Fotos OBR', 'Fotos MNR']
        pdf_content = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >>\nendobj\n4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n5 0 obj\n<< /Length 44 >>\nstream\nBT /F1 12 Tf 100 700 Td (Placeholder PDF) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000273 00000 n\n0000000352 00000 n\ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n446\n%%EOF'

        created = 0
        for tag_obj in TagArquivo.objects.all():
            if tag_obj.nome in photo_tags:
                continue
            nome = f"Arquivo — {tag_obj.nome}"
            obj, c = Arquivo.objects.get_or_create(nome=nome, defaults={'descricao': f'Placeholder — {tag_obj.nome}'})
            if c:
                try:
                    obj.arquivo.save('placeholder.pdf', ContentFile(pdf_content), save=False)
                    obj.save()
                    obj.tags.add(tag_obj)
                    created += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error creating arquivo for tag '{tag_obj.nome}': {e}"))
                    obj.delete()

        self.stdout.write(self.style.SUCCESS(f"Arquivos dummy ensured ({created} created)."))

    # ── Datas dummy ───────────────────────────────────────────────────────────

    def create_datas_dummy(self):
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#FFD700']
        march_dates = [5, 15, 25]
        created = 0
        for i, tag_obj in enumerate(TagData.objects.all()):
            for day in march_dates:
                try:
                    date_obj = datetime(2026, 3, day).date()
                    descricao = f"{tag_obj.nome} — {date_obj.strftime('%d/%m/%Y')}"
                    color = colors[i % len(colors)]
                    obj, c = Data.objects.get_or_create(
                        descricao=descricao, data=date_obj, defaults={'cor': color}
                    )
                    if c:
                        obj.tags.add(tag_obj)
                        created += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error creating date for '{tag_obj.nome}': {e}"))

        self.stdout.write(self.style.SUCCESS(f"Datas dummy ensured ({created} created)."))