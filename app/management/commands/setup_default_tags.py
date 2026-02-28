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

    def create_sedes(self):
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
        created = 0
        for ano, cidade, estado in sedes:
            obj, c = Sede.objects.update_or_create(ano=ano, defaults={'cidade': cidade, 'estado': estado})
            if c:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Sedes ensured ({created} created/updated)."))

    def create_subeventos(self):
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
        created = 0
        for nome, evento in subeventos:
            obj, c = Subevento.objects.update_or_create(nome=nome, defaults={'evento': evento})
            if c:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Subeventos ensured ({created} created/updated)."))

    def create_tags(self):
        from app.models import Regiao
        tag_arquivos = [
            'Design do Site',
            'Material do Organizador Regional (REP)',
            'Material do Organizador Nacional (LOC)',
            'Material de Divulgação IDV',
            'Material Extra OBR',
            'Material Edição 2026',
            'Manual OBR Documentos Gerais',
            'Manual OBR Teórica',
            'Manual OBR Prática Resgate',
            'Manual OBR Prática Artística',
            'Manual OBR Prática Virtual',
            'Manual OBR Aplicável à Nacional',
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
            'OBR', 'CBR', 'MNR', 'evento local', 'evento nacional', 'inscrição', 'envio de tdp',
            'envio de artigo/resumo', 'correção', 'aplicação de provas', '2ª fase', 'evento associado', 'evento patrocinador', 'LARS'
        ]
        tag_funcionarios = [
            'OBR', 'CBR', 'MNR', 'Presidência', 'Vice-Presidência', 'Curador (Trustee)', 'Chair / Coordenador de Modalidade',
            'General Chair / Coordenação de Evento', 'Representante Local', 'Secretaria', 'TI', 'Comunicação', 'Coordenação Administrativa'
        ]
        tag_noticias = [
            'OBR', 'CBR', 'MNR', 'LARS', 'Inscrições', 'Resultados', 'Editais', 'Notas Oficiais', 'Internacional',
            'Calendário', 'Institucional', 'Pós-Evento', 'Tecnologia', 'Voluntariado', 'Patrocinador'
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

    def create_paginas_estados(self):
        # Create a PaginaEstado for each state with a starter component
        from app.models import Regiao
        created = 0
        default_components = [
            {
                "type": "section",
                "main": {"container": True},
                "components": [
                    {
                        "type": "dynamic_texto",
                        "conteudo": "# Página do Representante Estadual\n\nAqui, o representante estadual da MNR/OBR poderá colocar datas, um calendário, e entre outras informações.",
                        "theme_foreground": "yin"
                    }
                ]
            }
        ]
        for code, name in Regiao.choices:
            obj, c = PaginaEstado.objects.update_or_create(
                estado=code,
                defaults={'componentes': default_components}
            )
            if c:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Páginas de estados ensured ({created} created).") )

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

    def create_paginas_dinamicas(self):
        # Top-level pages RCB
        pages = [
            {'nome': 'Índice', 'slug': '', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos', 'componentes': [{"type":"section","bg":"","main":{"container":False},"components":[{"type":"carousel","style":"yin blue-secondary","tabs":[{"id":"slide-1","label":"Slide 1","image":"/media/arquivos/nao.jpg","content":"<div class=\"container\">\n<br><br><br><br><br><br><br><br><br><br>\n<span class=\"text-xlarge text-700\">Ciência, Tecnologia e Inovação aliadas à <i>Educação</i></span>\n\n<span class=\"text-large text-500\">A RoboCup busca fornecer desafios padrão nas quais uma ampla gama de tecnologias pode ser integrada, testada e avaliada.</span>\n<br><br><br><br><br><br><br><br><br><br>\n</div>"},{"id":"tab-2","label":"Slide 2","icon":"","content":"<div class=\"container\">\n<br><br><br><br><br><br><br><br><br><br>\n<span class=\"text-xlarge text-700\">Robótica e Inteligência Artificial ao alcance do <i>grande público</i></span>\n\n<span class=\"text-large text-500\">As ações da RoboCup são, por princípio, ações de Divulgação Científica, que buscam levar o limiar da C,T&I para próximo do grande público </span>\n<br><br><br><br><br><br><br><br><br><br>\n</div>","image":"/media/arquivos/msl.jpg"},{"id":"tab-3","label":"Slide 3","icon":"","content":"<div class=\"container\">\n<br><br><br><br><br><br><br><br><br><br>\n<span class=\"text-xlarge text-700\">Desenvolvimento de novas tecnologias para as necessidades do <i>futuro</i></span>\n\n<span class=\"text-large text-500\">As provas da RoboCup estimulam o desenvolvimento conjunto da mecânica, elétrica e computação, em compasso com os novos desafios da modernindade.</span>\n<br><br><br><br><br><br><br><br><br><br>\n</div>","image":"/media/arquivos/drone.jpg"},{"id":"tab-4","label":"Slide 4","icon":"","content":"<div class=\"container\">\n<br><br><br><br><br><br><br><br><br><br>\n<span class=\"text-xlarge text-700\">Desafios personalizados com a <i>cara do Brasil</i></span>\n\n<span class=\"text-large text-500\">A Robocup Brasil desenvolve parcerias com empresas nacionais para estimular o desenvolvimento de C,T&I voltadas para as necessidades da indústria nacional.</span>\n<br><br><br><br><br><br><br><br><br><br>\n</div>","image":"/media/arquivos/arenadrone.jpg"},{"id":"tab-5","label":"Slide 5","icon":"","content":"<div class=\"container\">\n<br><br><br><br><br><br><br><br><br><br>\n<span class=\"text-xlarge text-700\">Levando a prática da robótica a <i>milhares de escolas</i> em todo o país</span>\n\n<span class=\"text-large text-500\">A RoboCup possui provas práticas estimulantes para jovens a partir do ensino fundamental.</span>\n<br><br><br><br><br><br><br><br><br><br>\n</div>","image":"/media/arquivos/obr.jpg"}]}],"border_details":[{"type":"rcb","color":"blue","position":"bottom right","spin":True,"container":True,"desktop_only":True}],"padding":"0","container":False,"padding_x":"1/"},{"type":"section","bg":"","main":{"container":True},"components":[{"type":"header","titulo":"Nossos Projetos","theme":"rcb","alignment":"start","size":"xxlarge"}],"border_details":[],"margin_t":"4","margin_b":"5","classes":"margin-t-3/ margin-b-5"},{"type":"section","bg":"yin","main":{"container":True},"components":[{"type":"dynamic_texto","theme_foreground":"yang","conteudo":"<span class=\"text-large-plus\">Para alunos do ensino médio e superior:</span>"}],"border_details":[{"type":"cbr","color":"yin","position":"bottom center","mobile_only":True,"size":"small"},{"type":"cbr","color":"yin","position":"bottom left","container":True,"desktop_only":True}],"classes":"margin-t-3 margin-b-5 desktop:margin-b-0"},{"type":"section","bg":"","main":{"container":True,"gap":"1/"},"components":[{"type":"header","theme":"cbr","alignment":"end","titulo":"Competição Brasileira de Robótica PETROBRAS","classes":"text-600"}],"border_details":[],"classes":"padding-t-2/ desktop:padding-t-4"},{"type":"section","bg":"","main":{"container":True},"components":[{"type":"conteudo_square","imagem":"/static/images/favicon/cbr.png","descricao":"<div class=\"text-300 margin-b-1 text-large-plus-plus\">A mais importante competição de robótica da América Latina. Com a participação de quase 200 Universidades e com provas da RoboCup Federation.</div>","text_align":"start","image_align_mobile":"top","image_align_desktop":"right","inline_text":"Conheça e Participe","inline_href":"/cbr","theme_primary":"yang","theme_secondary":"yang","classes":"icon-image","theme_foreground":"yin","inline_color":"gray-secondary","inline_theme":"yang","titulo":" "}],"border_details":[],"margin_y":"1/"},{"type":"section","main":{"container":False,"classes":"padding-y-3"},"components":[{"type":"slider_arquivos","tags":[18],"title":"Imagens CBR","theme_primary":"yin","theme_secondary":"gray","theme_foreground":"yang"}],"border_details":[],"container":False,"inside_bottom":True},{"type":"section","bg":"green-secondary","main":{"container":True,"classes":"padding-t-2 desktop:padding-t-3 margin-b-0"},"components":[{"type":"dynamic_texto","theme_foreground":"yang","conteudo":"<span class=\"text-large-plus\">Para alunos de todos os níveis:</span>"}],"border_details":[]},{"type":"section","bg":"green-secondary","main":{"container":True,"bg":"yang","classes":"border-radius margin-t-0 padding-y-3","padding":"1"},"components":[{"type":"imagem","imagem":"/static/images/header/mnr.png","titulo":"Logo MNR","clicavel":False,"rounded":False,"classes":"h-4 object-contain"},{"type":"dynamic_texto","conteudo":"<div class=\"text-align-center text-700 margin-t-1 text-xlarge\">\nMostra Nacional de Robótica\n</div>","theme_foreground":"blue-secondary"}],"border_details":[{"type":"mnr","color":"green-secondary","position":"bottom center"}],"classes":"padding-b-2"},{"type":"section","bg":"","main":{"container":True},"components":[{"type":"conteudo_square","imagem":"/media/arquivos/mnr-home.jpeg","descricao":"<div class=\"text-300 text-large-plus-plus\">Mais importante mostra de trabalhos de Robótica da América Latina. Seus anais contém mais de 2.000 trabalhos do ensino fundamental à pós-graduação.</div>","text_align":"start","image_align_mobile":"bottom","image_align_desktop":"left","inline_text":"Conheça e Participe","inline_href":"/mnr","theme_primary":"yang","theme_secondary":"yang","theme_foreground":"yin","inline_color":"green","inline_theme":"yang","titulo":" "}],"border_details":[],"classes":"padding-b-2 padding-t-5"},{"type":"section","main":{"container":False,"classes":"padding-b-1/"},"components":[{"type":"slider_arquivos","tags":[19],"title":"Imagens OBR","theme_primary":"yellow","theme_secondary":"yellow-secondary","theme_foreground":"yang"}],"border_details":[],"container":False,"inside_bottom":True},{"type":"section","bg":"yellow-secondary","main":{"container":True,"classes":"padding-t-3/ desktop:padding-t-4/"},"components":[{"type":"dynamic_texto","theme_foreground":"yang","conteudo":"<span class=\"text-large-plus\">Para alunos do ensino fundamental ao médio:</span>"}],"border_details":[{"type":"obr","color":"yellow-secondary","position":"bottom right","spin":True,"container":True,"margin_t":"margin-t-5","desktop_only":True},{"type":"obr","color":"yellow-secondary","position":"bottom center","mobile_only":True,"spin":True,"size":"small"}]},{"type":"section","main":{"container":True,"gap":"2"},"components":[{"type":"header","titulo":"Olimpíada Brasileira de Robótica","theme":"obr","alignment":"start","fullwidth":True,"classes":"text-600"}],"border_details":[],"margin_y":"2/","classes":"padding-t-3 desktop:padding-t-0"},{"type":"section","main":{"container":True,"gap":"2"},"components":[{"type":"conteudo_square","imagem":"/static/images/favicon/obr.png","descricao":"<div class=\"text-300 margin-b-1 text-large-plus-plus\">Uma das maiores competições de Robótica do mundo, com mais de 200.000 participantes ano. Voltada para jovens do ensino fundamental, médio e técnico.</div>","text_align":"start","image_align_mobile":"top","image_align_desktop":"right","inline_text":"Conheça e Participe","inline_href":"/obr","theme_primary":"yang","theme_secondary":"yang","classes":"icon-image","theme_foreground":"yin","inline_color":"green-secondary","inline_theme":"yang","titulo":" "}],"border_details":[]},{"type":"section","bg":"","main":{"container":True,"desktop:flex":True,"gap":"2"},"components":[{"type":"conteudo_square","imagem":"/media/arquivos/2026.png","titulo":"Evento Robótica","text_align":"start","image_align_mobile":"top","image_align_desktop":"top","inline_href":"/sede/2026","inline_text":"Mais Informações","descricao":"<span class=\"text-large\">O Robótica reúne competições e congressos nas áreas de robótica e inteligência artificial (IA), com mais de 500 instituições do Brasil e exterior. Em 2026, o evento acontece em João Pessoa, na Paraíba!</span>","color_secondary":"orange","inline_theme":"yang","inline_color":"red-secondary","theme_secondary":"red-secondary","theme_foreground":"yin","classes":"icon-image"},{"type":"conteudo_square","imagem":"/static/images/favicon/olimpo.png","titulo":"Sistema Olimpo","text_align":"start","image_align_mobile":"top","image_align_desktop":"top","inline_href":"https://olimpo.robocup.org.br/","inline_text":"Mais Informações","descricao":"<span class=\"text-large\">O primeiro sistema online especialmente desenvolvido no país para a gestão centralizada de Olimpíadas e eventos científicos de grande porte. Participe já de eventos RoboCup Brasil acessando o Olimpo.</span>","color_secondary":"orange","inline_theme":"yang","inline_color":"blue-secondary","theme_secondary":"blue-secondary","theme_foreground":"yin","classes":"icon-image margin-t-2 desktop:margin-t-0"}],"border_details":[],"container":False},{"type":"section","bg":"","main":{"container":True},"components":[{"type":"header","titulo":"Notícias","theme":"rcb","alignment":"start","size":"xxlarge"}],"border_details":[],"margin_y":"1/"},{"type":"section","bg":"","main":{"container":True,"gap":"3"},"components":[{"type":"dynamic_noticias","tag_ids":[],"pagination":False,"limit":3,"theme_foreground":"yang","theme_primary":"blue","theme_secondary":"blue-secondary"},{"type":"button_inline","texto":"Todas as Notícias","theme":"yin","color":"blue","href":"/noticias","shrink":True,"icon":"newspaper-o"}],"border_details":[]},{"type":"section","bg":"","main":{"container":True},"components":[{"type":"dynamic_calendar","tag_ids":[],"theme_primary":"blue","theme_secondary":"blue-secondary"}],"border_details":[]}]},
            {'nome': 'Sobre', 'slug': 'sobre', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos', 'componentes': []},
            {'nome': 'Notícias', 'slug': 'noticias', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos', 'componentes': [{"type":"section","bg":"","main":{"container":True},"components":[{"type":"header","titulo":"Todas as Notícias","theme":"rcb","alignment":"start","size":"xxlarge","fullwidth":True}],"border_details":[],"margin_y":"1/"},{"type":"section","bg":"","main":{"container":True,"gap":"3"},"components":[{"type":"dynamic_noticias","tag_ids":[],"pagination":True,"theme_foreground":"yang","theme_primary":"blue","theme_secondary":"blue-secondary","limit":12}],"border_details":[]}]},
            {'nome': 'Participe', 'slug': 'participe', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos', 'componentes': []},
            {'nome': 'Associados', 'slug': 'associados', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos', 'componentes': []},
            {'nome': 'Invista', 'slug': 'invista', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos', 'componentes': []},
            {'nome': 'Contato', 'slug': 'contato', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos', 'componentes': []},
            {'nome': 'Voluntários', 'slug': 'voluntarios', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos', 'componentes': []},
            {'nome': 'Material de Divulgação', 'slug': 'material-de-divulgacao', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos', 'componentes': []},
            {'nome': 'Organização Regional', 'slug': 'organizacao-regional', 'header_type': 'RCB', 'privada': True, 'evento_associado': 'Todos', 'componentes': []},
            {'nome': 'Organização Nacional', 'slug': 'organizacao-nacional', 'header_type': 'RCB', 'privada': True, 'evento_associado': 'Todos', 'componentes': []},
        ]

        for p in pages:
            try:
                obj, c = Pagina.objects.update_or_create(slug=p['slug'], parent=None, defaults={
                    'nome': p['nome'], 'parent': None, 'header_type': p['header_type'],
                    'privada': p['privada'], 'evento_associado': p['evento_associado']
                })
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipping page with slug '{p['slug']}' - {e}"))

        # Parent pages
        parents = [
            {'nome': 'Olimpíada Brasileira de Robótica', 'slug': 'obr', 'header_type': 'OBR', 'evento_associado': 'OBR'},
            {'nome': 'Competição Brasileira de Robótica', 'slug': 'cbr', 'header_type': 'CBR', 'evento_associado': 'CBR'},
            {'nome': 'Mostra Nacional de Robótica', 'slug': 'mnr', 'header_type': 'MNR', 'evento_associado': 'MNR'},
            {'nome': 'Robótica', 'slug': 'robotica', 'header_type': 'RCB', 'evento_associado': 'Todos'},
        ]

        for p in parents:
            try:
                obj, c = Pagina.objects.update_or_create(slug=p['slug'], parent=None, defaults={
                    'nome': p['nome'], 'parent': None, 'header_type': p['header_type'],
                    'componentes': [], 'privada': False, 'evento_associado': p['evento_associado']
                })
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipping parent page with slug '{p['slug']}' - {e}"))

        # Child pages mapping
        children = [
            # OBR children
            {'slug': 'sobre', 'parent_slug': 'obr', 'nome': 'Sobre', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR', 'componentes': []},
            {'slug': 'manuais', 'parent_slug': 'obr', 'nome': 'Manuais', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR', 'componentes': []},
            {'slug': 'participante', 'parent_slug': 'obr', 'nome': 'Participante', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR', 'componentes': []},
            {'slug': 'noticias', 'parent_slug': 'obr', 'nome': 'Notícias', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR', 'componentes': [{"type":"section","bg":"","main":{"container":True},"components":[{"type":"header","titulo":"Todas as Notícias","theme":"obr","alignment":"start","size":"xxlarge","fullwidth":True}],"border_details":[],"margin_y":"1/"},{"type":"section","bg":"","main":{"container":True,"gap":"3"},"components":[{"type":"dynamic_noticias","tag_ids":[1],"pagination":True,"theme_foreground":"yang","theme_primary":"blue","theme_secondary":"blue-secondary","limit":12}],"border_details":[]}]},
            {'slug': 'modalidades', 'parent_slug': 'obr', 'nome': 'Conheça Nossas Modalidades', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR', 'componentes': []},
            {'slug': 'nacional', 'parent_slug': 'obr', 'nome': 'Evento Nacional', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR', 'componentes': []},
            {'slug': 'faq', 'parent_slug': 'obr', 'nome': 'Perguntas Frequentes', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR', 'componentes': []},
            {'slug': 'mundo-robotica', 'parent_slug': 'obr', 'nome': 'Mundo Robótica', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR', 'componentes': []},
            # CBR children
            {'slug': 'sobre', 'parent_slug': 'cbr', 'nome': 'Sobre', 'header_type': 'CBR', 'privada': False, 'evento_associado': 'CBR', 'componentes': []},
            {'slug': 'ligas', 'parent_slug': 'cbr', 'nome': 'Ligas', 'header_type': 'CBR', 'privada': False, 'evento_associado': 'CBR', 'componentes': []},
            {'slug': 'noticias', 'parent_slug': 'cbr', 'nome': 'Notícias', 'header_type': 'CBR', 'privada': False, 'evento_associado': 'CBR', 'componentes': [{"type":"section","bg":"","main":{"container":True},"components":[{"type":"header","titulo":"Todas as Notícias","theme":"cbr","alignment":"start","size":"xxlarge","fullwidth":True}],"border_details":[],"margin_y":"1/"},{"type":"section","bg":"","main":{"container":True,"gap":"3"},"components":[{"type":"dynamic_noticias","tag_ids":[2],"pagination":True,"theme_foreground":"yang","theme_primary":"blue","theme_secondary":"blue-secondary","limit":12}],"border_details":[]}]},
            {'slug': 'pagamentos', 'parent_slug': 'cbr', 'nome': 'Pagamentos', 'header_type': 'CBR', 'privada': False, 'evento_associado': 'CBR', 'componentes': []},
            {'slug': 'tdp', 'parent_slug': 'cbr', 'nome': 'TDP', 'header_type': 'CBR', 'privada': False, 'evento_associado': 'CBR', 'componentes': []},
            # MNR children
            {'slug': 'sobre', 'parent_slug': 'mnr', 'nome': 'Sobre', 'header_type': 'MNR', 'privada': False, 'evento_associado': 'MNR', 'componentes': []},
            {'slug': 'documentos', 'parent_slug': 'mnr', 'nome': 'Documentos', 'header_type': 'MNR', 'privada': False, 'evento_associado': 'MNR', 'componentes': []},
            {'slug': 'anais', 'parent_slug': 'mnr', 'nome': 'Anais', 'header_type': 'MNR', 'privada': False, 'evento_associado': 'MNR', 'componentes': []},
            {'slug': 'noticias', 'parent_slug': 'mnr', 'nome': 'Notícias', 'header_type': 'MNR', 'privada': False, 'evento_associado': 'MNR', 'componentes': [{"type":"section","bg":"","main":{"container":True},"components":[{"type":"header","titulo":"Todas as Notícias","theme":"mnr","alignment":"start","size":"xxlarge","fullwidth":True}],"border_details":[],"margin_y":"1/"},{"type":"section","bg":"","main":{"container":True,"gap":"3"},"components":[{"type":"dynamic_noticias","tag_ids":[3],"pagination":True,"theme_foreground":"yang","theme_primary":"blue","theme_secondary":"blue-secondary","limit":12}],"border_details":[]}]},
            {'slug': 'avaliador', 'parent_slug': 'mnr', 'nome': 'Avaliador', 'header_type': 'MNR', 'privada': False, 'evento_associado': 'MNR', 'componentes': []},
            {'slug': 'bolsista', 'parent_slug': 'mnr', 'nome': 'Bolsista', 'header_type': 'MNR', 'privada': False, 'evento_associado': 'MNR', 'componentes': []},
        ]

        for ch in children:
            try:
                parent = Pagina.objects.get(slug=ch['parent_slug'], parent=None)
            except Pagina.DoesNotExist:
                parent = None
            defaults = {
                'nome': ch['nome'], 'parent': parent, 'header_type': ch['header_type'],
                'privada': ch['privada'], 'evento_associado': ch['evento_associado']
            }
            
            try:
                obj, c = Pagina.objects.update_or_create(slug=ch['slug'], parent=parent, defaults=defaults)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipping child page with slug '{ch['slug']}' - {e}"))

        self.stdout.write(self.style.SUCCESS("Páginas dinâmicas ensured."))

    def create_arquivos(self):
        """Create default Arquivo objects from files in media/default_files/ subdirectories"""
        import os
        from django.core.files.base import ContentFile

        # default files are stored inside the management folder (versioned)
        default_files_dir = os.path.join(settings.BASE_DIR, 'app', 'management', 'default_files')

        if not os.path.isdir(default_files_dir):
            self.stdout.write(self.style.SUCCESS("No default_files directory found. Skipping arquivo setup."))
            return

        # Mapeamento de slugs de pastas para nomes de tags
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
                self.stdout.write(self.style.WARNING(f"Tag '{tag_name}' not found. Skipping folder '{folder_slug}'."))
                continue

            # Processa cada arquivo na pasta
            for filename in os.listdir(folder_path):
                filepath = os.path.join(folder_path, filename)
                
                # Ignora pastas e arquivos dummy.txt
                if not os.path.isfile(filepath) or filename == 'dummy.txt':
                    continue

                # Get or create arquivo
                obj, c = Arquivo.objects.get_or_create(nome=filename)

                if c:
                    # Read the file and assign to arquivo field
                    try:
                        with open(filepath, 'rb') as f:
                            content = f.read()
                            obj.arquivo.save(filename, ContentFile(content), save=False)
                            obj.save()
                        obj.tags.add(tag)
                        created += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Error processing file '{filename}' in '{folder_slug}': {e}"))
                        obj.delete()

        self.stdout.write(self.style.SUCCESS(f"Arquivos ensured ({created} created/updated)."))

    def create_menus(self):
        config = ConfiguracaoGlobal.objects.first()
        if not config:
            return

        escondidos = [
            'Modalidade Teórica', 'Modalidades Práticas', 'Perguntas Frequentes', 'Mundo Robótica',
            'Associados', 'Invista', 'Contato', 'Voluntários', 'Material de Divulgação', 'Avaliador', 'Bolsista'
        ]

        # RCB Menu
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
            ItemMenu.objects.get_or_create(config=config, header_type='RCB', nome=p['nome'], defaults={'link': link, 'escondido': is_hidden})

        # Children Menus
        children_data = [
            # OBR
            {'slug': 'sobre', 'parent_slug': 'obr', 'nome': 'Sobre', 'header_type': 'OBR', 'componentes': []},
            {'slug': 'manuais', 'parent_slug': 'obr', 'nome': 'Manuais', 'header_type': 'OBR', 'componentes': []},
            {'slug': 'participante', 'parent_slug': 'obr', 'nome': 'Participante', 'header_type': 'OBR', 'componentes': []},
            {'slug': 'noticias', 'parent_slug': 'obr', 'nome': 'Notícias', 'header_type': 'OBR', 'componentes': []},
            {'slug': 'modalidade-teorica', 'parent_slug': 'obr', 'nome': 'Modalidade Teórica', 'header_type': 'OBR', 'componentes': []},
            {'slug': 'modalidades-praticas', 'parent_slug': 'obr', 'nome': 'Modalidades Práticas', 'header_type': 'OBR', 'componentes': []},
            {'slug': 'faq', 'parent_slug': 'obr', 'nome': 'Perguntas Frequentes', 'header_type': 'OBR', 'componentes': []},
            {'slug': 'mundo-robotica', 'parent_slug': 'obr', 'nome': 'Mundo Robótica', 'header_type': 'OBR', 'componentes': []},
            # CBR
            {'slug': 'sobre', 'parent_slug': 'cbr', 'nome': 'Sobre', 'header_type': 'CBR', 'componentes': []},
            {'slug': 'ligas', 'parent_slug': 'cbr', 'nome': 'Ligas', 'header_type': 'CBR', 'componentes': []},
            {'slug': 'noticias', 'parent_slug': 'cbr', 'nome': 'Notícias', 'header_type': 'CBR', 'componentes': []},
            {'slug': 'pagamentos', 'parent_slug': 'cbr', 'nome': 'Pagamentos', 'header_type': 'CBR', 'componentes': []},
            {'slug': 'tdp', 'parent_slug': 'cbr', 'nome': 'TDP', 'header_type': 'CBR', 'componentes': []},
            # MNR
            {'slug': 'sobre', 'parent_slug': 'mnr', 'nome': 'Sobre', 'header_type': 'MNR', 'componentes': []},
            {'slug': 'documentos', 'parent_slug': 'mnr', 'nome': 'Documentos', 'header_type': 'MNR', 'componentes': []},
            {'slug': 'anais', 'parent_slug': 'mnr', 'nome': 'Anais', 'header_type': 'MNR', 'componentes': []},
            {'slug': 'noticias', 'parent_slug': 'mnr', 'nome': 'Notícias', 'header_type': 'MNR', 'componentes': []},
            {'slug': 'avaliador', 'parent_slug': 'mnr', 'nome': 'Avaliador', 'header_type': 'MNR', 'componentes': []},
            {'slug': 'bolsista', 'parent_slug': 'mnr', 'nome': 'Bolsista', 'header_type': 'MNR', 'componentes': []},
        ]
        
        for item in children_data:
            link = f"/{item['parent_slug']}/{item['slug']}"
            is_hidden = item['nome'] in escondidos
            ItemMenu.objects.get_or_create(config=config, header_type=item['header_type'], nome=item['nome'], defaults={'link': link, 'escondido': is_hidden})
            
        self.stdout.write(self.style.SUCCESS("Menus ensured."))

    def create_funcionarios_dummy(self):
        """Create dummy funcionários with placeholder data"""
        # Líderes principais
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
        
        # Curadores
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
        
        # Outros funcionários (4 por tag)
        other_tags = [
            'OBR', 'CBR', 'MNR', 'Chair / Coordenador de Modalidade',
            'General Chair / Coordenação de Evento', 'Representante Local', 'Secretaria', 'TI', 'Comunicação', 'Coordenação Administrativa'
        ]
        
        for tag_name in other_tags:
            try:
                tag = TagFuncionario.objects.get(nome=tag_name)
                for i in range(1, 5):
                    nome = f'{tag_name} {i}'
                    obj, c = Funcionario.objects.get_or_create(nome=nome, defaults={'cargo': tag_name})
                    if c:
                        obj.tags.add(tag)
                        created += 1
            except TagFuncionario.DoesNotExist:
                pass
        
        self.stdout.write(self.style.SUCCESS(f"Funcionários dummy ensured ({created} created)."))

    def create_arquivos_dummy(self):
        """Create dummy arquivos with placeholder.pdf for non-photo tags"""
        # Tags de fotos que devem ser ignoradas
        photo_tags = ['Fotos CBR', 'Fotos OBR', 'Fotos MNR']
        
        # Gerar PDF placeholder (conteúdo mínimo)
        pdf_content = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >>\nendobj\n4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n5 0 obj\n<< /Length 44 >>\nstream\nBT /F1 12 Tf 100 700 Td (Placeholder PDF) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000273 00000 n\n0000000352 00000 n\ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n446\n%%EOF'
        
        created = 0
        for tag_obj in TagArquivo.objects.all():
            if tag_obj.nome in photo_tags:
                continue
            
            nome = f"Arquivo - {tag_obj.nome}"
            descricao = f"Arquivo placeholder da tag {tag_obj.nome}"
            
            obj, c = Arquivo.objects.get_or_create(nome=nome, defaults={'descricao': descricao})
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

    def create_datas_dummy(self):
        """Create dummy dates in March for each data tag (3 dates per tag)"""
        # Cores para as datas
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#FFD700']
        color_index = 0
        
        # Datas dummy em março de 2026 (alguns dias antes, durante e depois)
        march_dates = [5, 15, 25]  # dias do mês
        
        created = 0
        for tag_obj in TagData.objects.all():
            for day in march_dates:
                try:
                    date_obj = datetime(2026, 3, day).date()
                    descricao = f"{tag_obj.nome} - {date_obj.strftime('%d/%m/%Y')}"
                    color = colors[color_index % len(colors)]
                    
                    obj, c = Data.objects.get_or_create(
                        descricao=descricao,
                        data=date_obj,
                        defaults={'cor': color}
                    )
                    if c:
                        obj.tags.add(tag_obj)
                        created += 1
                    
                    color_index += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error creating date for tag '{tag_obj.nome}': {e}"))
        
        self.stdout.write(self.style.SUCCESS(f"Datas dummy ensured ({created} created)."))
