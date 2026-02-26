from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.admin.models import LogEntry
from .models import (
    TagFuncionario, Funcionario,
    TagNoticia, Noticia,
    TagData, Data,
    TagArquivo, Arquivo,
    Subevento,
    ConfiguracaoGlobal,
    AtalhoGlobal,
    ItemMenu, ItemMenuRCB, ItemMenuCBR, ItemMenuMNR, ItemMenuOBR,
    UserProfile,
    Pagina,
    Sede,
    PaginaEstado,
)
from .permissions import RolePermissionMixin

_original_get_app_list = admin.sites.AdminSite.get_app_list

def _get_app_list_with_avancado(self, request):
    app_list = _original_get_app_list(self, request)
    
    groups_def = [
        {
            'name': 'Conteúdo',
            'slug': 'conteudo',
            'icon': 'fa-solid fa-newspaper',
            'models': {'Noticia', 'Data'}
        },
        {
            'name': 'Páginas',
            'slug': 'paginas',
            'icon': 'fa-solid fa-mouse-pointer',
            'models': {'PaginaEstado', 'Subevento', 'Pagina'}
        },
        {
            'name': 'Cadastros',
            'slug': 'cadastros',
            'icon': 'fa-solid fa-folder-open',
            'models': {'Arquivo', 'ConfiguracaoGlobal', 'Funcionario', 'Sede'}
        },
        {
            'name': 'Avançado',
            'slug': 'avancado',
            'icon': 'fa-solid fa-gear',
            'models': {'TagArquivo', 'TagData', 'TagFuncionario', 'TagNoticia'}
        }
    ]
    
    buckets = {g['name']: [] for g in groups_def}
    model_to_group = {}
    for g in groups_def:
        for m in g['models']:
            model_to_group[m] = g['name']

    for app in list(app_list):
        models = app.get('models', [])
        kept = []
        for m in models:
            obj_name = m.get('object_name')
            if obj_name in model_to_group:
                buckets[model_to_group[obj_name]].append(m)
            else:
                kept.append(m)
        if kept != models:
            if kept:
                app['models'] = kept
            else:
                app_list.remove(app)

    for g in groups_def:
        models = buckets[g['name']]
        if models:
            models.sort(key=lambda x: x['name'])
            app_list.append({
                'name': g['name'],
                'app_label': g['slug'],
                'app_url': models[0].get('admin_url', '') if models else '',
                'has_module_perms': True,
                'models': models,
                'icon': g['icon'],
            })

    return app_list

admin.site.get_app_list = _get_app_list_with_avancado.__get__(admin.site, admin.sites.AdminSite)

from django.forms.models import BaseInlineFormSet
from django.db import IntegrityError

class OneToOneInlineFormSet(BaseInlineFormSet):
    def save_new(self, form, commit=True):
        try:
            existing = self.model.objects.get(user=self.instance)
        except self.model.DoesNotExist:
            existing = None

        if existing:
            form.instance.pk = existing.pk

        try:
            return super().save_new(form, commit=commit)
        except IntegrityError:
            existing = self.model.objects.get(user=self.instance)
            form.instance.pk = existing.pk
            return super().save_new(form, commit=commit)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    formset = OneToOneInlineFormSet
    extra = 1
    max_num = 1
    can_delete = False
    fields = ('estado', 'ligas', 'grupo_extra')
    filter_horizontal = ['ligas']
    verbose_name = "Dados Extras do Usuário"
    verbose_name_plural = "Dados Extras do Usuário"

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == "ligas":
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
            field.widget.can_view_related = False
        return field

class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)


    def get_list_display(self, request):
        return ['username', 'first_name', 'get_grupo', 'get_estado']

    def get_grupo(self, obj):
        profile = getattr(obj, 'userprofile', None)
        if profile:
            return profile.get_grupo_extra_display()
        return "—"
    get_grupo.short_description = "Permissão"

    def get_estado(self, obj):
        profile = getattr(obj, 'userprofile', None)
        if profile and profile.estado:
            return profile.get_estado_display()
        return "—"
    get_estado.short_description = "Estado"

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        new = []
        for name, opts in fieldsets:
            fields = list(opts.get('fields', ()))
            filtered = tuple(f for f in fields if f not in (
                'groups', 'user_permissions', 'last_login', 'date_joined',
                'is_active', 'is_staff', 'is_superuser'
            ))
            if filtered:
                new_opts = opts.copy()
                new_opts['fields'] = filtered
                new.append((name, new_opts))
        return new

    def save_model(self, request, obj, form, change):
        if not change:
            obj.is_staff = True
            obj.is_active = True

        if obj.is_superuser and obj.pk:
            other_supers = User.objects.filter(is_superuser=True).exclude(pk=obj.pk)
            if other_supers.exists():
                raise ValidationError("Já existe um Superusuário. Só pode haver um.")
        elif obj.is_superuser and not obj.pk:
            if User.objects.filter(is_superuser=True).exists():
                raise ValidationError("Já existe um Superusuário. Só pode haver um.")

        super().save_model(request, obj, form, change)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

@admin.register(TagFuncionario)
class TagFuncionarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'id']
    search_fields = ['nome']
    list_per_page = 50

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cargo', 'get_tags']
    list_filter = ['tags']
    search_fields = ['nome', 'cargo']
    list_per_page = 50
    filter_horizontal = ['tags']

    def get_tags(self, obj):
        return ";ㅤ".join([f"{tag.id} - {tag.nome}" for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == "tags":
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
            field.widget.can_view_related = False
        return field

@admin.register(TagNoticia)
class TagNoticiaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'id']
    search_fields = ['nome']
    list_per_page = 50

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'data', 'get_tags', 'header_type', 'view_link']
    list_filter = ['header_type', 'tags']
    search_fields = ['titulo', 'conteudo']
    date_hierarchy = 'data'
    filter_horizontal = ['tags']
    list_per_page = 50

    def view_link(self, obj):
        if obj.permalink:
            url = obj.get_absolute_url()
            return mark_safe(f"<a href='{url}' target='_blank' rel='noopener'><i class='fa fa-eye'></i></a>")
        return ''
    view_link.short_description = 'Ver'

    def get_tags(self, obj):
        return "; ".join([f"{tag.id} - {tag.nome}" for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == "tags":
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
            field.widget.can_view_related = False
        return field

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['conteudo'].widget.attrs['placeholder'] = """Formatação básica:
**negrito** → negrito
_itálico_ → itálico
# Título → Título grande
## Título 2 → Título médio
[texto](https://link.com) → Link clicável
- item → Lista com marcador

Imagens:
![descrição](https://url-da-imagem.png) → Imagem simples
[![descrição](https://url-da-imagem.png)](https://link.com) → Imagem clicável"""
        return form

@admin.register(TagData)
class TagDataAdmin(RolePermissionMixin, admin.ModelAdmin):
    list_display = ['nome', 'id']
    search_fields = ['nome']
    list_per_page = 50

    def has_delete_permission(self, request, obj=None):
        role = self.get_user_role(request)
        if role == 'MARKETING':
            return False
        return super().has_delete_permission(request, obj)

class DataAdminForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = '__all__'
        widgets = {
            'cor': forms.TextInput(attrs={'type': 'color'}),
        }
        
@admin.register(Data)
class DataAdmin(RolePermissionMixin, admin.ModelAdmin):
    form = DataAdminForm
    list_display = ['descricao', 'data', 'cor', 'action_link', 'get_tags']
    list_filter = ['data', 'tags']
    search_fields = ['descricao']
    date_hierarchy = 'data'
    filter_horizontal = ['tags']
    list_per_page = 50

    def get_tags(self, obj):
        return "; ".join([f"{tag.id} - {tag.nome}" for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == "tags":
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
            field.widget.can_view_related = False
        return field

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        role = self.get_user_role(request)
        if role in ['REPRESENTANTE', 'COORD']:
            return qs.filter(owner=request.user)
        return qs

    def has_add_permission(self, request):
        role = self.get_user_role(request)
        if role in ['REPRESENTANTE', 'COORD']:
            return True
        return role not in ['COORD', 'MARKETING'] or super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        role = self.get_user_role(request)
        if role in ['REPRESENTANTE', 'COORD']:
            if obj is None:
                return True
            return obj.owner == request.user
        return super().has_change_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not change and hasattr(request, 'user'):
            obj.owner = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        role = self.get_user_role(request)
        if role == 'MARKETING' or role == 'REPRESENTANTE':
            return False
        return super().has_delete_permission(request, obj)

@admin.register(TagArquivo)
class TagArquivoAdmin(RolePermissionMixin, admin.ModelAdmin):
    list_display = ['nome', 'id']
    search_fields = ['nome']
    list_per_page = 50

    def has_delete_permission(self, request, obj=None):
        role = self.get_user_role(request)
        if role == 'MARKETING':
            return False
        return super().has_delete_permission(request, obj)

@admin.register(Arquivo)
class ArquivoAdmin(RolePermissionMixin, admin.ModelAdmin):
    list_display = ['nome', 'id', 'arquivo', 'get_tags', 'descricao']
    list_filter = ['tags']
    search_fields = ['nome']
    filter_horizontal = ['tags']
    list_per_page = 50

    def get_tags(self, obj):
        return "; ".join([f"{tag.id} - {tag.nome}" for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == "tags":
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
            field.widget.can_view_related = False
        return field

    def has_delete_permission(self, request, obj=None):
        role = self.get_user_role(request)
        if role == 'MARKETING':
            return False
        return super().has_delete_permission(request, obj)

@admin.register(Subevento)
class SubeventoAdmin(RolePermissionMixin, admin.ModelAdmin):
    list_display = ['nome', 'evento', 'view_link']
    list_filter = ['evento']
    search_fields = ['nome']
    list_per_page = 50

    def view_link(self, obj):
        if obj.permalink:
            url = obj.get_absolute_url()
            return mark_safe(f"<a href='{url}' target='_blank' rel='noopener'><i class='fa fa-eye'></i></a>")
        return ''
    view_link.short_description = 'Ver'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        role = self.get_user_role(request)
        
        if role == 'COORD':
            return qs.filter(id__in=request.user.userprofile.ligas.all())
        
        return qs

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'componentes':
            kwargs['widget'] = ComponentesWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # cache no longer stored
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        role = self.get_user_role(request)
        if role == 'COORD':
            if obj is None:
                return True
            return obj in request.user.userprofile.ligas.all()

        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        role = self.get_user_role(request)
        if role in ['COORD', 'REPRESENTANTE', 'MARKETING']:
            return False
        return super().has_delete_permission(request, obj)

class AtalhoGlobalInline(admin.TabularInline):
    model = AtalhoGlobal
    extra = 1
    verbose_name = "Atalho de Rodapé"
    verbose_name_plural = "Rodapé: Atalhos (Links Rápidos)"
    fields = ('nome', 'link')

class ItemMenuInlineBase(admin.TabularInline):
    extra = 0
    fields = ('header_type', 'nome', 'link', 'escondido')
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['header_type'].initial = self.header_type_value
        formset.form.base_fields['header_type'].widget = forms.HiddenInput()
        return formset

class ItemMenuRCBInline(ItemMenuInlineBase):
    model = ItemMenuRCB
    header_type_value = 'RCB'
    verbose_name = "Item de Menu (RCB)"
    verbose_name_plural = "Menu Padrão RCB: Itens"
    def get_queryset(self, request):
        return super().get_queryset(request).filter(header_type='RCB')

class ItemMenuCBRInline(ItemMenuInlineBase):
    model = ItemMenuCBR
    header_type_value = 'CBR'
    verbose_name = "Item de Menu (CBR)"
    verbose_name_plural = "Menu CBR: Itens"
    def get_queryset(self, request):
        return super().get_queryset(request).filter(header_type='CBR')

class ItemMenuMNRInline(ItemMenuInlineBase):
    model = ItemMenuMNR
    header_type_value = 'MNR'
    verbose_name = "Item de Menu (MNR)"
    verbose_name_plural = "Menu MNR: Itens"
    def get_queryset(self, request):
        return super().get_queryset(request).filter(header_type='MNR')

class ItemMenuOBRInline(ItemMenuInlineBase):
    model = ItemMenuOBR
    header_type_value = 'OBR'
    verbose_name = "Item de Menu (OBR)"
    verbose_name_plural = "Menu OBR: Itens"
    def get_queryset(self, request):
        return super().get_queryset(request).filter(header_type='OBR')

@admin.register(ConfiguracaoGlobal)
class ConfiguracaoGlobalAdmin(RolePermissionMixin, admin.ModelAdmin):
    list_display = ['__str__', 'email_contato']
    fieldsets = (
        ('Configurações Gerais', {
            'fields': ('descricao', 'email_contato', 'outros_emails', 'instagram', 'facebook', 'youtube', 'linkedin', 'patrocinio_vertical', 'patrocinio_horizontal')
        }),
        ('Links das Logos (Headers)', {
            'fields': ('logo_link_cbr', 'logo_link_mnr', 'logo_link_obr'),
            'description': 'Defina para onde o usuário será redirecionado ao clicar na logo em cada cabeçalho.'
        }),
    )
    inlines = [AtalhoGlobalInline, ItemMenuRCBInline, ItemMenuCBRInline, ItemMenuMNRInline, ItemMenuOBRInline]

    def has_add_permission(self, request):
        if ConfiguracaoGlobal.objects.exists():
            return False
        return super().has_add_permission(request)

if admin.site.is_registered(LogEntry):
    admin.site.unregister(LogEntry)

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['action_time', 'user', 'content_type', 'object_repr', 'action_flag']
    list_filter = ['action_flag', 'content_type', 'user']
    search_fields = ['object_repr', 'change_message', 'user__username']
    list_per_page = 50

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

class ComponentesWidget(forms.Textarea):
    template_name = 'admin/pagina/component_builder.html'

@admin.register(Pagina)
class PaginaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'parent', 'header_type', 'privada', 'evento_associado', 'view_link']

    def view_link(self, obj):
        url = obj.get_absolute_url()
        return mark_safe(f"<a href='{url}' target='_blank' rel='noopener'><i class='fa fa-eye'></i></a>")
    view_link.short_description = 'Ver'
    list_filter = ['header_type', 'privada', 'evento_associado']
    search_fields = ['nome', 'slug']
    list_per_page = 50
    fieldsets = (
        (None, {
            'fields': ('nome', 'slug', 'parent', 'header_type', 'privada', 'evento_associado'),
        }),
        ('Conteúdo da Página', {
            'fields': ('componentes',),
            'description': 'Lista JSON ordenada. A ordem dos itens define a sequência na página.'
        }),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'componentes':
            kwargs['widget'] = ComponentesWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'parent' in form.base_fields:
            widget = form.base_fields['parent'].widget
            widget.can_add_related = False
            widget.can_change_related = False
            widget.can_delete_related = False
            widget.can_view_related = False
        return form

    def save_model(self, request, obj, form, change):
        # HTML cache no longer used
        super().save_model(request, obj, form, change)

    def has_module_permission(self, request):
        role = None
        if hasattr(request.user, 'userprofile'):
            role = request.user.userprofile.grupo_extra
        if role == 'COORD':
            return False
        return super().has_module_permission(request)

@admin.register(Sede)
class SedeAdmin(RolePermissionMixin, admin.ModelAdmin):
    list_display = ['ano', 'cidade', 'estado', 'view_link']
    fields = ('ano','cidade','estado','foto','componentes')

    def view_link(self, obj):
        url = obj.get_absolute_url()
        return mark_safe(f"<a href='{url}' target='_blank' rel='noopener'><i class='fa fa-eye'></i></a>")
    view_link.short_description = 'Ver'
    ordering = ['-ano']
    list_per_page = 50

    def has_delete_permission(self, request, obj=None):
        role = self.get_user_role(request)
        if role == 'MARKETING':
            return False
        return super().has_delete_permission(request, obj)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'componentes':
            kwargs['widget'] = ComponentesWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # HTML cache no longer used
        super().save_model(request, obj, form, change)

@admin.register(PaginaEstado)
class PaginaEstadoAdmin(RolePermissionMixin, admin.ModelAdmin):
    list_display = ['estado', 'view_link']

    def view_link(self, obj):
        url = obj.get_absolute_url()
        return mark_safe(f"<a href='{url}' target='_blank' rel='noopener'><i class='fa fa-eye'></i></a>")
    view_link.short_description = 'Ver'
    list_display = ['estado', 'get_estado_display']
    search_fields = ['estado']
    list_per_page = 50
    fieldsets = (
        (None, {
            'fields': ('estado','componentes'),
        }),
    )

    class PaginaEstadoForm(forms.ModelForm):
        class Meta:
            model = PaginaEstado
            fields = '__all__'

        def __init__(self, *args, request=None, **kwargs):
            self.request = request
            super().__init__(*args, **kwargs)

        def clean_estado(self):
            estado = self.cleaned_data.get('estado')
            if self.request and hasattr(self.request.user, 'userprofile'):
                role = self.request.user.userprofile.grupo_extra
                if role == 'REPRESENTANTE':
                    user_estado = self.request.user.userprofile.estado
                    if estado != user_estado:
                        raise forms.ValidationError("Representante só pode criar/editar páginas do seu próprio estado.")
            return estado

    def get_form(self, request, obj=None, **kwargs):
        base_form = kwargs.pop('form', self.PaginaEstadoForm)

        class RequestForm(base_form):
            def __init__(self, *args, **kwargs):
                kwargs['request'] = request
                super().__init__(*args, **kwargs)

        kwargs['form'] = RequestForm
        return super().get_form(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'componentes':
            kwargs['widget'] = ComponentesWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_estado_display(self, obj):
        return obj.get_estado_display()
    get_estado_display.short_description = "Nome do Estado"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        role = self.get_user_role(request)
        user_estado = request.user.userprofile.estado if hasattr(request.user, 'userprofile') else None
        
        if role == 'REPRESENTANTE' and user_estado:
            return qs.filter(estado=user_estado)
        
        return qs

    def has_add_permission(self, request):
        role = self.get_user_role(request)
        if role == 'REPRESENTANTE':
            user_estado = request.user.userprofile.estado
            if not user_estado:
                return False
            return not PaginaEstado.objects.filter(estado=user_estado).exists()
        
        return role not in ['COORD', 'MARKETING']

    def has_change_permission(self, request, obj=None):
        if not super().has_change_permission(request, obj):
            return False
        
        role = self.get_user_role(request)
        if role == 'REPRESENTANTE' and obj:
            user_estado = request.user.userprofile.estado
            return obj.estado == user_estado
        
        return role not in ['COORD', 'MARKETING']

    def has_delete_permission(self, request, obj=None):
        role = self.get_user_role(request)
        return role not in ['COORD', 'REPRESENTANTE', 'MARKETING']

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'estado', 'grupo_extra', 'get_ligas_display']
    list_filter = ['estado', 'grupo_extra']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']
    filter_horizontal = ['ligas']
    list_per_page = 50

    def get_ligas_display(self, obj):
        return ", ".join([str(s) for s in obj.ligas.all()]) or "—"
    get_ligas_display.short_description = "Subeventos"

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('auth.delete_user') or request.user.is_superuser:
            return True
        return False

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == "ligas":
            field.widget.can_add_related = False
        return field