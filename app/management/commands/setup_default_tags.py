"""
Management command to create default tags, sedes, subeventos, dynamic pages and global config.
Idempotent: safe to run multiple times.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from app.models import (
    Sede, Subevento, TagArquivo, TagData, TagFuncionario, TagNoticia,
    PaginaEstado, ConfiguracaoGlobal, Pagina, AtalhoGlobal, ItemMenu,
)
from django.conf import settings
from django.utils.text import slugify


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
            self.create_menus()

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
            obj, c = Subevento.objects.update_or_create(nome=nome, defaults={'evento': evento, 'quadro_avisos': ''})
            if c:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Subeventos ensured ({created} created/updated)."))

    def create_tags(self):
        tag_arquivos = [
            'Revista Mundo Robótica',
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
            'Manual OBR aplicável à Nacional',
            'Documento Genérico MNR',
            'Modelo MNR',
            'Anais MNR',
            'TDP CBR',
        ]
        tag_datas = [
            'OBR', 'CBR', 'MNR', 'evento local', 'evento nacional', 'inscrição', 'envio de tdp',
            'envio de artigo/resumo', 'correção', 'aplicação de provas', '2ª fase', 'evento associado', 'evento patrocinador', 'LARS'
        ]
        tag_funcionarios = [
            'OBR', 'CBR', 'MNR', 'Presidência', 'Curador (Trustee)', 'Chair / Coordenador de Modalidade',
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
        for nome in tag_funcionarios:
            TagFuncionario.objects.get_or_create(nome=nome)
        for nome in tag_noticias:
            TagNoticia.objects.get_or_create(nome=nome)

        self.stdout.write(self.style.SUCCESS("Tags ensured."))

    def create_paginas_estados(self):
        # Create a PaginaEstado for each state
        from app.models import Regiao
        created = 0
        for code, name in Regiao.choices:
            obj, c = PaginaEstado.objects.get_or_create(estado=code)
            if c:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Páginas de estados ensured ({created} created)."))

    def create_configuracao_global(self):
        defaults = {
            'descricao': "Principal associação e maior produtora de eventos de robótica e inteligência artificial do país. Inclui desde o famoso futebol de robôs à simulações de resgate e robôs domésticos, capacitando estudantes do ensino fundamental à pós-graduação.",
            'instagram': "https://www.instagram.com/robocupbrasil/",
            'facebook': "https://www.facebook.com/robocupbrasil/",
            'youtube': "https://www.youtube.com/robocupbrasil",
            'linkedin': "https://www.linkedin.com/company/robocupbrasil/",
            'email_contato': "contato@robocup.org.br",
            'outros_emails': "obr@robocup.org.br cbr@robocup.org.br mnr@robocup.org.br",
            'logo_link_rcb': "/",
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
            {'nome': 'Índice', 'slug': '', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos'},
            {'nome': 'Sobre', 'slug': 'sobre', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos'},
            {'nome': 'Notícias', 'slug': 'noticias', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos'},
            {'nome': 'Participe', 'slug': 'participe', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos'},
            {'nome': 'Associados', 'slug': 'associados', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos'},
            {'nome': 'Invista', 'slug': 'invista', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos'},
            {'nome': 'Contato', 'slug': 'contato', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos'},
            {'nome': 'Voluntários', 'slug': 'voluntarios', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos'},
            {'nome': 'Material de Divulgação', 'slug': 'material-de-divulgacao', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos'},
            {'nome': 'Organização Regional', 'slug': 'organizacao-regional', 'header_type': 'RCB', 'privada': True, 'evento_associado': 'Todos'},
            {'nome': 'Organização Nacional', 'slug': 'organizacao-nacional', 'header_type': 'RCB', 'privada': True, 'evento_associado': 'Todos'},
        ]

        for p in pages:
            try:
                obj, c = Pagina.objects.update_or_create(slug=p['slug'], defaults={
                    'nome': p['nome'], 'parent': None, 'header_type': p['header_type'],
                    'componentes': [], 'privada': p['privada'], 'evento_associado': p['evento_associado']
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
                obj, c = Pagina.objects.update_or_create(slug=p['slug'], defaults={
                    'nome': p['nome'], 'parent': None, 'header_type': p['header_type'],
                    'componentes': [], 'privada': False, 'evento_associado': p['evento_associado']
                })
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipping parent page with slug '{p['slug']}' - {e}"))

        # Child pages mapping
        children = [
            # OBR children
            {'slug': 'sobre', 'parent_slug': 'obr', 'nome': 'Sobre', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR'},
            {'slug': 'manuais', 'parent_slug': 'obr', 'nome': 'Manuais', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR'},
            {'slug': 'participante', 'parent_slug': 'obr', 'nome': 'Participante', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR'},
            {'slug': 'noticias', 'parent_slug': 'obr', 'nome': 'Notícias', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR'},
            {'slug': 'modalidade-teorica', 'parent_slug': 'obr', 'nome': 'Modalidade Teórica', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR'},
            {'slug': 'modalidades-praticas', 'parent_slug': 'obr', 'nome': 'Modalidades Práticas', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR'},
            {'slug': 'faq', 'parent_slug': 'obr', 'nome': 'Perguntas Frequentes', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR'},
            {'slug': 'mundo-robotica', 'parent_slug': 'obr', 'nome': 'Mundo Robótica', 'header_type': 'OBR', 'privada': False, 'evento_associado': 'OBR'},
            # CBR children
            {'slug': 'sobre', 'parent_slug': 'cbr', 'nome': 'Sobre', 'header_type': 'CBR', 'privada': False, 'evento_associado': 'CBR'},
            {'slug': 'ligas', 'parent_slug': 'cbr', 'nome': 'Ligas', 'header_type': 'CBR', 'privada': False, 'evento_associado': 'CBR'},
            {'slug': 'noticias', 'parent_slug': 'cbr', 'nome': 'Notícias', 'header_type': 'CBR', 'privada': False, 'evento_associado': 'CBR'},
            {'slug': 'pagamentos', 'parent_slug': 'cbr', 'nome': 'Pagamentos', 'header_type': 'CBR', 'privada': False, 'evento_associado': 'CBR'},
            {'slug': 'tdp', 'parent_slug': 'cbr', 'nome': 'TDP', 'header_type': 'CBR', 'privada': False, 'evento_associado': 'CBR'},
            # MNR children
            {'slug': 'sobre', 'parent_slug': 'mnr', 'nome': 'Sobre', 'header_type': 'MNR', 'privada': False, 'evento_associado': 'MNR'},
            {'slug': 'documentos', 'parent_slug': 'mnr', 'nome': 'Documentos', 'header_type': 'MNR', 'privada': False, 'evento_associado': 'MNR'},
            {'slug': 'anais', 'parent_slug': 'mnr', 'nome': 'Anais', 'header_type': 'MNR', 'privada': False, 'evento_associado': 'MNR'},
            {'slug': 'noticias', 'parent_slug': 'mnr', 'nome': 'Notícias', 'header_type': 'MNR', 'privada': False, 'evento_associado': 'MNR'},
            {'slug': 'avaliador', 'parent_slug': 'mnr', 'nome': 'Avaliador', 'header_type': 'MNR', 'privada': False, 'evento_associado': 'MNR'},
            {'slug': 'bolsista', 'parent_slug': 'mnr', 'nome': 'Bolsista', 'header_type': 'MNR', 'privada': False, 'evento_associado': 'MNR'},
            # Robótica children
            {'slug': 'edicoes', 'parent_slug': 'robotica', 'nome': 'Edições', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos'},
            {'slug': 'participantes', 'parent_slug': 'robotica', 'nome': 'Página do Participante', 'header_type': 'RCB', 'privada': False, 'evento_associado': 'Todos'},
        ]

        for ch in children:
            try:
                parent = Pagina.objects.get(slug=ch['parent_slug'])
            except Pagina.DoesNotExist:
                parent = None
            defaults = {
                'nome': ch['nome'], 'parent': parent, 'header_type': ch['header_type'],
                'componentes': [], 'privada': ch['privada'], 'evento_associado': ch['evento_associado']
            }
            
            try:
                obj, c = Pagina.objects.update_or_create(slug=ch['slug'], parent=parent, defaults=defaults)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipping child page with slug '{ch['slug']}' - {e}"))

        self.stdout.write(self.style.SUCCESS("Páginas dinâmicas ensured."))

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
            {'nome': 'Robótica', 'slug': 'robotica'},
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
            {'slug': 'sobre', 'parent_slug': 'obr', 'nome': 'Sobre', 'header_type': 'OBR'},
            {'slug': 'manuais', 'parent_slug': 'obr', 'nome': 'Manuais', 'header_type': 'OBR'},
            {'slug': 'participante', 'parent_slug': 'obr', 'nome': 'Participante', 'header_type': 'OBR'},
            {'slug': 'noticias', 'parent_slug': 'obr', 'nome': 'Notícias', 'header_type': 'OBR'},
            {'slug': 'modalidade-teorica', 'parent_slug': 'obr', 'nome': 'Modalidade Teórica', 'header_type': 'OBR'},
            {'slug': 'modalidades-praticas', 'parent_slug': 'obr', 'nome': 'Modalidades Práticas', 'header_type': 'OBR'},
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
            ItemMenu.objects.get_or_create(config=config, header_type=item['header_type'], nome=item['nome'], defaults={'link': link, 'escondido': is_hidden})
            
        self.stdout.write(self.style.SUCCESS("Menus ensured."))
