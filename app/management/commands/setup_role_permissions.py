"""
Management command to create and configure role-based permissions.
Runs after initial migration to set up default groups with hardcoded permissions.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from app.models import (
    Funcionario, TagFuncionario,
    Noticia, TagNoticia,
    Arquivo, TagArquivo,
    Data, TagData,
    Subevento,
    ConfiguracaoGlobal,
    Pagina,
    Sede,
    PaginaEstado,
)


class Command(BaseCommand):
    help = "Create and configure role-based permission groups"

    def handle(self, *args, **options):
        roles_config = {
            'SECRETARIA': {
                'display_name': 'Secretaria',
                'permissions': [
                    ('add_user', 'auth', 'user'),
                    ('change_user', 'auth', 'user'),
                    ('delete_user', 'auth', 'user'),
                    ('view_user', 'auth', 'user'),
                    ('delete_logentry', 'admin', 'logentry'),
                    ('add_funcionario', 'app', 'funcionario'),
                    ('change_funcionario', 'app', 'funcionario'),
                    ('delete_funcionario', 'app', 'funcionario'),
                    ('view_funcionario', 'app', 'funcionario'),
                    ('add_tagfuncionario', 'app', 'tagfuncionario'),
                    ('change_tagfuncionario', 'app', 'tagfuncionario'),
                    ('delete_tagfuncionario', 'app', 'tagfuncionario'),
                    ('view_tagfuncionario', 'app', 'tagfuncionario'),
                    ('add_noticia', 'app', 'noticia'),
                    ('change_noticia', 'app', 'noticia'),
                    ('delete_noticia', 'app', 'noticia'),
                    ('view_noticia', 'app', 'noticia'),
                    ('add_tagnoticia', 'app', 'tagnoticia'),
                    ('change_tagnoticia', 'app', 'tagnoticia'),
                    ('delete_tagnoticia', 'app', 'tagnoticia'),
                    ('view_tagnoticia', 'app', 'tagnoticia'),
                    ('add_arquivo', 'app', 'arquivo'),
                    ('change_arquivo', 'app', 'arquivo'),
                    ('delete_arquivo', 'app', 'arquivo'),
                    ('view_arquivo', 'app', 'arquivo'),
                    ('add_tagarquivo', 'app', 'tagarquivo'),
                    ('change_tagarquivo', 'app', 'tagarquivo'),
                    ('delete_tagarquivo', 'app', 'tagarquivo'),
                    ('view_tagarquivo', 'app', 'tagarquivo'),
                    ('add_data', 'app', 'data'),
                    ('change_data', 'app', 'data'),
                    ('delete_data', 'app', 'data'),
                    ('view_data', 'app', 'data'),
                    ('add_tagdata', 'app', 'tagdata'),
                    ('change_tagdata', 'app', 'tagdata'),
                    ('delete_tagdata', 'app', 'tagdata'),
                    ('view_tagdata', 'app', 'tagdata'),
                    ('add_subevento', 'app', 'subevento'),
                    ('change_subevento', 'app', 'subevento'),
                    ('delete_subevento', 'app', 'subevento'),
                    ('view_subevento', 'app', 'subevento'),
                    ('add_configuracaoglobal', 'app', 'configuracaoglobal'),
                    ('change_configuracaoglobal', 'app', 'configuracaoglobal'),
                    ('view_configuracaoglobal', 'app', 'configuracaoglobal'),
                    ('add_pagina', 'app', 'pagina'),
                    ('change_pagina', 'app', 'pagina'),
                    ('delete_pagina', 'app', 'pagina'),
                    ('view_pagina', 'app', 'pagina'),
                    ('add_sede', 'app', 'sede'),
                    ('change_sede', 'app', 'sede'),
                    ('delete_sede', 'app', 'sede'),
                    ('view_sede', 'app', 'sede'),
                    ('add_paginaestado', 'app', 'paginaestado'),
                    ('change_paginaestado', 'app', 'paginaestado'),
                    ('delete_paginaestado', 'app', 'paginaestado'),
                    ('view_paginaestado', 'app', 'paginaestado'),
                    ('add_userprofile', 'app', 'userprofile'),
                    ('change_userprofile', 'app', 'userprofile'),
                    ('view_userprofile', 'app', 'userprofile'),
                ]
            },
            'COORD': {
                'display_name': 'Coordenador de Subevento',
                'permissions': [
                    ('view_subevento', 'app', 'subevento'),
                    ('add_noticia', 'app', 'noticia'),
                    ('change_noticia', 'app', 'noticia'),
                    ('view_noticia', 'app', 'noticia'),
                    ('add_arquivo', 'app', 'arquivo'),
                    ('change_arquivo', 'app', 'arquivo'),
                    ('view_arquivo', 'app', 'arquivo'),
                    ('add_tagarquivo', 'app', 'tagarquivo'),
                    ('change_tagarquivo', 'app', 'tagarquivo'),
                    ('view_tagarquivo', 'app', 'tagarquivo'),
                    ('add_pagina', 'app', 'pagina'),
                    ('change_pagina', 'app', 'pagina'),
                    ('view_pagina', 'app', 'pagina'),
                ]
            },
            'REPRESENTANTE': {
                'display_name': 'Representante Local',
                'permissions': [
                    ('add_paginaestado', 'app', 'paginaestado'),
                    ('change_paginaestado', 'app', 'paginaestado'),
                    ('view_paginaestado', 'app', 'paginaestado'),
                    ('add_arquivo', 'app', 'arquivo'),
                    ('view_arquivo', 'app', 'arquivo'),
                ]
            },
            'MARKETING': {
                'display_name': 'Marketing',
                'permissions': [
                    ('add_configuracaoglobal', 'app', 'configuracaoglobal'),
                    ('change_configuracaoglobal', 'app', 'configuracaoglobal'),
                    ('view_configuracaoglobal', 'app', 'configuracaoglobal'),
                    ('add_arquivo', 'app', 'arquivo'),
                    ('change_arquivo', 'app', 'arquivo'),
                    ('view_arquivo', 'app', 'arquivo'),
                    ('add_tagarquivo', 'app', 'tagarquivo'),
                    ('change_tagarquivo', 'app', 'tagarquivo'),
                    ('view_tagarquivo', 'app', 'tagarquivo'),
                    ('add_data', 'app', 'data'),
                    ('change_data', 'app', 'data'),
                    ('view_data', 'app', 'data'),
                    ('add_tagdata', 'app', 'tagdata'),
                    ('change_tagdata', 'app', 'tagdata'),
                    ('view_tagdata', 'app', 'tagdata'),
                    ('add_sede', 'app', 'sede'),
                    ('view_sede', 'app', 'sede'),
                ]
            },
        }

        for role_key, role_data in roles_config.items():
            group, created = Group.objects.get_or_create(name=role_data['display_name'])
            group.permissions.clear()

            for perm_codename, app_label, model_name in role_data['permissions']:
                try:
                    perm = Permission.objects.get(
                        content_type__app_label=app_label,
                        content_type__model=model_name,
                        codename=perm_codename
                    )
                    group.permissions.add(perm)
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Permission {perm_codename} for {app_label}.{model_name} not found"
                        )
                    )

            status = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"{status} group: {role_data['display_name']} with {group.permissions.count()} permissions"
                )
            )

        self.stdout.write(self.style.SUCCESS("Role permissions setup completed successfully!"))
