"""
Management command to create default tags, sedes, subeventos, dynamic pages and global config.
Idempotent: safe to run multiple times.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from app.models import (
    Sede, Subevento, TagArquivo, TagData, TagFuncionario, TagNoticia,
    PaginaEstado, ConfiguracaoGlobal, Pagina,
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
        obj, created = ConfiguracaoGlobal.objects.get_or_create()
        if created:
            self.stdout.write(self.style.SUCCESS("Configuração global created."))
        else:
            self.stdout.write(self.style.SUCCESS("Configuração global exists."))

    def create_paginas_dinamicas(self):
        # Top-level pages
        pages = [
            {'nome': 'Índice', 'slug': '', 'header_type': 'RCB', 'privada': False, 'mostrar_no_menu': False, 'evento_associado': 'Todos'},
            {'nome': 'Sobre', 'slug': 'sobre', 'header_type': 'RCB', 'privada': False, 'mostrar_no_menu': True, 'evento_associado': 'Todos'},
            {'nome': 'Associados', 'slug': 'associados', 'header_type': 'RCB', 'privada': False, 'mostrar_no_menu': True, 'evento_associado': 'Todos'},
            {'nome': 'Contato', 'slug': 'contato', 'header_type': 'RCB', 'privada': False, 'mostrar_no_menu': True, 'evento_associado': 'Todos'},
            {'nome': 'Invista', 'slug': 'invista', 'header_type': 'RCB', 'privada': False, 'mostrar_no_menu': True, 'evento_associado': 'Todos'},
            {'nome': 'Notícias', 'slug': 'noticias', 'header_type': 'RCB', 'privada': False, 'mostrar_no_menu': True, 'evento_associado': 'Todos'},
            {'nome': 'Participe', 'slug': 'participe', 'header_type': 'RCB', 'privada': False, 'mostrar_no_menu': True, 'evento_associado': 'Todos'},
            {'nome': 'Voluntários', 'slug': 'voluntarios', 'header_type': 'RCB', 'privada': False, 'mostrar_no_menu': True, 'evento_associado': 'Todos'},
            {'nome': 'Material de Divulgação', 'slug': 'material-de-divulgacao', 'header_type': 'RCB', 'privada': False, 'mostrar_no_menu': False, 'evento_associado': 'Todos'},
            {'nome': 'Organização Regional', 'slug': 'organizacao-regional', 'header_type': 'RCB', 'privada': True, 'mostrar_no_menu': False, 'evento_associado': 'Todos'},
            {'nome': 'Organização Nacional', 'slug': 'organizacao-nacional', 'header_type': 'RCB', 'privada': True, 'mostrar_no_menu': False, 'evento_associado': 'Todos'},
        ]

        for p in pages:
            try:
                obj, c = Pagina.objects.update_or_create(slug=p['slug'], defaults={
                    'nome': p['nome'], 'parent': None, 'header_type': p['header_type'],
                    'componentes': [], 'mostrar_no_menu': p['mostrar_no_menu'], 'privada': p['privada'], 'evento_associado': p['evento_associado']
                })
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipping page with slug '{p['slug']}' - {e}"))

        # Parent pages
        parents = [
            {'nome': 'Olimpíada Brasileira de Robótica', 'slug': 'obr', 'header_type': 'OBR', 'evento_associado': 'OBR'},
            {'nome': 'Competição Brasileira de Robótica', 'slug': 'cbr', 'header_type': 'CBR', 'evento_associado': 'CBR'},
            {'nome': 'Mostra Nacional de Robótica', 'slug': 'mnr', 'header_type': 'MNR', 'evento_associado': 'MNR'},
            {'nome': 'Evento Robótica', 'slug': 'robotica', 'header_type': 'RCB', 'evento_associado': 'Todos'},
        ]

        for p in parents:
            try:
                obj, c = Pagina.objects.update_or_create(slug=p['slug'], defaults={
                    'nome': p['nome'], 'parent': None, 'header_type': p['header_type'],
                    'componentes': [], 'mostrar_no_menu': False, 'privada': False, 'evento_associado': p['evento_associado']
                })
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipping parent page with slug '{p['slug']}' - {e}"))

        # Child pages mapping
        children = [
            # OBR children
            {'slug': 'faq', 'parent_slug': 'obr', 'nome': 'Perguntas Frequentes', 'header_type': 'OBR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'OBR'},
            {'slug': 'manuais', 'parent_slug': 'obr', 'nome': 'Manuais', 'header_type': 'OBR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'OBR'},
            {'slug': 'modalidade-teorica', 'parent_slug': 'obr', 'nome': 'Modalidade Teórica', 'header_type': 'OBR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'OBR'},
            {'slug': 'modalidades-praticas', 'parent_slug': 'obr', 'nome': 'Modalidades Práticas', 'header_type': 'OBR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'OBR'},
            {'slug': 'mundo-robotica', 'parent_slug': 'obr', 'nome': 'Mundo Robótica', 'header_type': 'OBR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'OBR'},
            {'slug': 'noticias', 'parent_slug': 'obr', 'nome': 'Notícias', 'header_type': 'OBR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'OBR'},
            {'slug': 'participante', 'parent_slug': 'obr', 'nome': 'Participante', 'header_type': 'OBR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'OBR'},
            {'slug': 'sobre', 'parent_slug': 'obr', 'nome': 'Sobre', 'header_type': 'OBR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'OBR'},
            # CBR children
            {'slug': 'ligas', 'parent_slug': 'cbr', 'nome': 'Ligas', 'header_type': 'CBR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'CBR'},
            {'slug': 'noticias', 'parent_slug': 'cbr', 'nome': 'Notícias', 'header_type': 'CBR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'CBR'},
            {'slug': 'pagamentos', 'parent_slug': 'cbr', 'nome': 'Pagamentos', 'header_type': 'CBR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'CBR'},
            {'slug': 'sobre', 'parent_slug': 'cbr', 'nome': 'Sobre', 'header_type': 'CBR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'CBR'},
            {'slug': 'tdp', 'parent_slug': 'cbr', 'nome': 'TDP', 'header_type': 'CBR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'CBR'},
            # MNR children
            {'slug': 'anais', 'parent_slug': 'mnr', 'nome': 'Anais', 'header_type': 'MNR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'MNR'},
            {'slug': 'avaliador', 'parent_slug': 'mnr', 'nome': 'Avaliador', 'header_type': 'MNR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'MNR'},
            {'slug': 'bolsista', 'parent_slug': 'mnr', 'nome': 'Bolsista', 'header_type': 'MNR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'MNR'},
            {'slug': 'documentos', 'parent_slug': 'mnr', 'nome': 'Documentos', 'header_type': 'MNR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'MNR'},
            {'slug': 'noticias', 'parent_slug': 'mnr', 'nome': 'Notícias', 'header_type': 'MNR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'MNR'},
            {'slug': 'sobre', 'parent_slug': 'mnr', 'nome': 'Sobre', 'header_type': 'MNR', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'MNR'},
            # Evento Robótica children
            {'slug': 'edicoes', 'parent_slug': 'robotica', 'nome': 'Edições', 'header_type': 'RCB', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'Todos'},
            {'slug': 'participantes', 'parent_slug': 'robotica', 'nome': 'Página do Participante', 'header_type': 'RCB', 'mostrar_no_menu': True, 'privada': False, 'evento_associado': 'Todos'},
        ]

        for ch in children:
            try:
                parent = Pagina.objects.get(slug=ch['parent_slug'])
            except Pagina.DoesNotExist:
                parent = None
            defaults = {
                'nome': ch['nome'], 'parent': parent, 'header_type': ch['header_type'],
                'componentes': [], 'mostrar_no_menu': ch['mostrar_no_menu'], 'privada': ch['privada'], 'evento_associado': ch['evento_associado']
            }
            Pagina.objects.update_or_create(slug=ch['slug'] + '-' + (ch['parent_slug'] or ''), defaults=defaults)  # avoid slug dupes by combining parent

        self.stdout.write(self.style.SUCCESS("Páginas dinâmicas ensured."))
