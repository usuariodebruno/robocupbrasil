from django.contrib import admin
from .models import (
    TagFuncionario, Funcionario,
    TagNoticia, Noticia,
    TagData, Data,
    TagArquivo, Arquivo,
    Subevento,
    ConfiguracaoGlobal,
    UserProfile,
    Pagina,
    Sede,
    PaginaEstado,
)

@admin.register(TagFuncionario)
class TagFuncionarioAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cargo', 'evento', 'user']
    list_filter = ['evento', 'tags']
    search_fields = ['nome', 'cargo', 'user__username', 'user__email']
    raw_id_fields = ['user']

@admin.register(TagNoticia)
class TagNoticiaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'evento', 'data', 'get_tags', 'header_type']
    list_filter = ['header_type', 'evento', 'tags']
    search_fields = ['titulo', 'conteudo']
    date_hierarchy = 'data'
    list_per_page = 20

    def get_tags(self, obj):
        return ", ".join([tag.nome for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'

@admin.register(TagData)
class TagDataAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']

@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'data', 'cor', 'action_link']
    list_filter = ['data', 'tags']
    search_fields = ['descricao']
    date_hierarchy = 'data'

@admin.register(TagArquivo)
class TagArquivoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']

@admin.register(Arquivo)
class ArquivoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'evento', 'arquivo', 'get_tags']
    list_filter = ['evento', 'tags']
    search_fields = ['nome']

    def get_tags(self, obj):
        return ", ".join([tag.nome for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'

@admin.register(Subevento)
class SubeventoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'evento']
    list_filter = ['evento']
    search_fields = ['nome']

@admin.register(ConfiguracaoGlobal)
class ConfiguracaoGlobalAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'patrocinio_imagem']

    def has_add_permission(self, request):
        return not ConfiguracaoGlobal.objects.exists()

@admin.register(Pagina)
class PaginaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'parent', 'header_type', 'mostrar_no_menu', 'evento_associado']
    list_filter = ['header_type', 'mostrar_no_menu', 'evento_associado']
    search_fields = ['nome', 'slug']
    fieldsets = (
        (None, {
            'fields': ('nome', 'slug', 'parent', 'header_type', 'mostrar_no_menu', 'evento_associado'),
        }),
        ('Componentes (ordem importa!)', {
            'fields': ('componentes',),
            'description': 'Lista JSON ordenada. A ordem dos itens define a sequência na página.'
        }),
    )

@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ['ano', 'cidade', 'estado']
    ordering = ['ano']

@admin.register(PaginaEstado)
class PaginaEstadoAdmin(admin.ModelAdmin):
    list_display = ['estado', 'get_estado_display']
    search_fields = ['estado']
    fieldsets = (
        (None, {
            'fields': ('estado','texto'),
        }),
    )

    def get_estado_display(self, obj):
        return obj.get_estado_display()
    get_estado_display.short_description = "Nome do Estado"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'estado', 'grupo_extra']
    list_filter = ['estado', 'grupo_extra']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']