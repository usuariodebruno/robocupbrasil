from django.db import models, transaction
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django_resized import ResizedImageField
from django.core.cache import cache

def validate_file_size(f):
    if f and getattr(f, 'size', 0) > 64 * 1024 * 1024:
        raise ValidationError("Tamanho máximo do arquivo: 64MB.")

def _sanitize_recursive(value):
    """Walk through strings/lists/dicts raising ValidationError if forbidden patterns are found."""
    if isinstance(value, str):
        lowered = value.lower()
        if '<script' in lowered or 'onclick=' in lowered or 'onerror=' in lowered or 'onload=' in lowered:
            raise ValidationError(
                "Conteúdo contém trechos proibidos (scripts/onclick/etc). Remova qualquer tag <script> ou atributos de evento."
            )
    elif isinstance(value, dict):
        for v in value.values():
            _sanitize_recursive(v)
    elif isinstance(value, (list, tuple)):
        for v in value:
            _sanitize_recursive(v)

class GlobalQueryMixin(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def get_items(cls, tag_ids=None, limit=10, page_index=0, **kwargs):
        if not tag_ids:
            tag_ids = []

        qs = cls.objects.all()

        # Filtros Específicos por Modelo
        if cls.__name__ == 'Subevento':
            evento = kwargs.get('evento')
            if evento and evento.lower() != 'todos':
                qs = qs.filter(evento__iexact=evento)

        # Filtro por Tags (para modelos que possuem o campo 'tags')
        if tag_ids and hasattr(cls, 'tags'):
            # O modelo Sede não tem tags, então este bloco será ignorado para ele.
            try:
                valid_tag_ids = [int(tid) for tid in tag_ids]
                if valid_tag_ids:
                    qs = qs.filter(tags__id__in=valid_tag_ids).distinct()
            except (ValueError, TypeError):
                pass

        # Ordering
        if cls.__name__ == 'Noticia':
            qs = qs.order_by('-data')
        elif cls.__name__ == 'Data':
            qs = qs.order_by('data')
        elif hasattr(cls, 'ano'):
            qs = qs.order_by('-ano')
        elif hasattr(cls, 'nome'):
            qs = qs.order_by('nome')
        elif hasattr(cls, 'titulo'):
            qs = qs.order_by('titulo')
        elif hasattr(cls, 'descricao'):
            qs = qs.order_by('descricao')

        # Pagination
        try:
            limit = int(limit) if limit is not None else 10
            page_index = int(page_index) if page_index is not None else 0
        except (ValueError, TypeError):
            limit = 10
            page_index = 0
        
        start_index = page_index * limit
        end_index = start_index + limit
        
        return list(qs[start_index:end_index])

class Evento(models.TextChoices):
    MNR = 'MNR', 'MNR'
    CBR = 'CBR', 'CBR'
    OBR = 'OBR', 'OBR'
    ROBOTICA = 'Robotica', 'Robotica'
    ROBOCUP_BRASIL = 'RoboCup Brasil', 'RoboCup Brasil'
    TODOS = 'Todos', 'Todos'

    @property
    def cor(self):
        cores = {
            'MNR': '#00ff00',
            'CBR': '#00ffff',
            'OBR': '#ff4d00',
            'Robotica': '#0000ff',
            'RoboCup Brasil': '#0000ff',
            'Todos': '#0000ff',
        }
        return cores.get(self.value, '#000000')

class Regiao(models.TextChoices):
    AC = 'AC', 'Acre'
    AL = 'AL', 'Alagoas'
    AP = 'AP', 'Amapá'
    AM = 'AM', 'Amazonas'
    BA = 'BA', 'Bahia'
    CE = 'CE', 'Ceará'
    DF = 'DF', 'Distrito Federal'
    ES = 'ES', 'Espirito Santo'
    GO = 'GO', 'Goiás'
    MA = 'MA', 'Maranhão'
    MT = 'MT', 'Mato Grosso'
    MS = 'MS', 'Mato Grosso do Sul'
    MG = 'MG', 'Minas Gerais'
    PA = 'PA', 'Pará'
    PB = 'PB', 'Paraíba'
    PR = 'PR', 'Paraná'
    PE = 'PE', 'Pernambuco'
    PI = 'PI', 'Piauí'
    RJ = 'RJ', 'Rio de Janeiro'
    RN = 'RN', 'Rio Grande do Norte'
    RS = 'RS', 'Rio Grande do Sul'
    RO = 'RO', 'Rondônia'
    RR = 'RR', 'Roraima'
    SC = 'SC', 'Santa Catarina'
    SP = 'SP', 'São Paulo'
    SE = 'SE', 'Sergipe'
    TO = 'TO', 'Tocantins'

class TagFuncionario(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Tag de Funcionário"
        verbose_name_plural = "Tags de Funcionários"

    def __str__(self):
        return self.nome

class Funcionario(GlobalQueryMixin, models.Model):
    nome = models.CharField(max_length=200)
    cargo = models.CharField(max_length=200)
    instituicao = models.CharField(max_length=200, blank=True, verbose_name='Instituição / Empresa')
    tags = models.ManyToManyField(TagFuncionario, verbose_name='Tag(s) de Funcionário')
    bio = models.TextField(blank=True)
    foto = ResizedImageField(
        size=[3000, 3000],
        quality=75,
        upload_to='fotos_funcionarios/',
        blank=True,
        verbose_name='Foto (tam. ideal 512x512)',
        help_text='A imagem será redimensionada para no máximo 3000x3000 pixels.',
    )

    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"

    def __str__(self):
        return self.nome or f"Funcionário {self.id}"

class TagNoticia(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Tag de Notícia"
        verbose_name_plural = "Tags de Notícias"

    def __str__(self):
        return self.nome

class Noticia(GlobalQueryMixin, models.Model):
    titulo = models.CharField(max_length=200)
    chamada = models.CharField(max_length=200, default="Insira uma curta chamada ou introdução para sua notícia aqui...")
    imagem = ResizedImageField(
        size=[3000, 3000],
        quality=75,
        upload_to='noticias/',
        blank=True,
        verbose_name='Imagem da Notícia (prop. ideal 16:9)',
        help_text='A imagem será redimensionada para no máximo 3000x3000 pixels.',
    )
    # stored as plain markdown (rendered on front-end)
    conteudo = models.TextField()

    header_type = models.CharField(
        max_length=50,
        choices=[
            ('RCB', 'Header Padrão RCB'),
            ('OBR', 'Header OBR'),
            ('CBR', 'Header CBR'),
            ('MNR', 'Header MNR'),
        ],
        default='RCB',
        verbose_name="Cabeçalho da Página",
        help_text="Qual cabeçalho usar nesta notícia (como se fosse uma página)"
    )
    tags = models.ManyToManyField(TagNoticia, verbose_name='Tag(s) da Notícia')
    data = models.DateTimeField(auto_now_add=True)
    permalink = models.SlugField(unique=True, max_length=255, editable=False, allow_unicode=True, blank=True)

    def clean(self):
        # ensure markdown content doesn't contain disallowed scripts or event attributes
        _sanitize_recursive(self.conteudo)

    def save(self, *args, **kwargs):
        self.clean()
        if not self.permalink:
            base_slug = slugify(self.titulo, allow_unicode=True)
            slug = base_slug
            counter = 1

            while Noticia.objects.filter(permalink=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.permalink = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/noticia/{self.permalink}"

    class Meta:
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"

    def __str__(self):
        return self.titulo

class TagData(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Tag de Data"
        verbose_name_plural = "Tags de Datas"

    def __str__(self):
        return self.nome

class Data(GlobalQueryMixin, models.Model):
    descricao = models.CharField(max_length=200, verbose_name='Nome / Descrição para a Data')
    data = models.DateField()
    cor = models.CharField(max_length=7, default='#000000')
    action_link = models.URLField(blank=True, verbose_name='Link de mais informações')
    tags = models.ManyToManyField(TagData, verbose_name='Tag(s) da Data')

    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, editable=False)

    def __str__(self):
        return f"{self.descricao} ({self.data})"

    class Meta:
        verbose_name = "Data no Calendário"
        verbose_name_plural = "Datas no Calendário"

class TagArquivo(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Tag de Arquivo"
        verbose_name_plural = "Tags de Arquivos"

    def __str__(self):
        return self.nome

class Arquivo(GlobalQueryMixin, models.Model):
    nome = models.CharField(max_length=200)
    arquivo = models.FileField(
        upload_to='arquivos/',
        verbose_name='Arquivo (tamanho máximo 64MB)',
        help_text='Tamanho máximo: 64MB',
        validators=[validate_file_size],
    )
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    thumbnail = ResizedImageField(
        size=[1200, 1200],
        quality=80,
        upload_to='arquivos/thumbnails/',
        blank=True,
        editable=False,
    )
    tags = models.ManyToManyField(TagArquivo, verbose_name='Tag(s) de Arquivo')

    class Meta:
        verbose_name = "Arquivo"
        verbose_name_plural = "Arquivos"

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        # attempt to generate thumbnail for PDF files using pdf2image (requires poppler)
        if self.arquivo and (not self.thumbnail) and self.arquivo.name.lower().endswith('.pdf'):
            try:
                from pdf2image import convert_from_bytes
                from io import BytesIO
                from django.core.files.base import ContentFile

                self.arquivo.open('rb')
                pdf_bytes = self.arquivo.read()
                images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1)
                if images:
                    bio = BytesIO()
                    images[0].save(bio, format='PNG')
                    bio.seek(0)
                    thumb_name = f"{self.arquivo.name.rsplit('/',1)[-1]}.png"
                    self.thumbnail.save(thumb_name, ContentFile(bio.read()), save=False)
            except Exception:
                # silently ignore thumbnail generation errors
                pass

        super().save(*args, **kwargs)

class Subevento(GlobalQueryMixin, models.Model):
    nome = models.CharField(max_length=200)
    evento = models.CharField(max_length=50, choices=Evento.choices)
    icone = ResizedImageField(
        size=[3000, 3000],
        quality=75,
        upload_to='icones/',
        blank=True,
        verbose_name='Ícone (tam. ideal 256x256)',
        help_text='A imagem será redimensionada para no máximo 3000x3000 pixels.',
    )
    componentes = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Configuração da Página",
    )
    # cache field removed; dynamic rendering used instead

    permalink = models.SlugField(unique=True, max_length=255, editable=False, allow_unicode=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.permalink:
            base_slug = slugify(self.nome, allow_unicode=True)
            slug = base_slug
            counter = 1

            while Subevento.objects.filter(permalink=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.permalink = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/evento/{self.permalink}"

    class Meta:
        verbose_name = "Subevento (Liga)"
        verbose_name_plural = "Subeventos (Ligas)"

    def __str__(self):
        return self.nome

    def clean(self):
        # sanitize componentes JSON
        _sanitize_recursive(self.componentes)

class ConfiguracaoGlobal(models.Model):
    descricao = models.TextField(blank=True, verbose_name="Descrição da Página (para o Google e Rodapé)")
    patrocinio_vertical = ResizedImageField(
        size=[3000, 3000],
        quality=75,
        upload_to='patrocinio/',
        blank=True,
        verbose_name='Patrocínio Vertical (Celular) (prop. ideal 9:16)',
        help_text='A imagem será redimensionada para no máximo 3000x3000 pixels.',
    )
    patrocinio_horizontal = ResizedImageField(
        size=[3000, 3000],
        quality=75,
        upload_to='patrocinio/',
        blank=True,
        verbose_name='Patrocínio Horizontal (Computador) (prop. ideal 16:9)',
        help_text='A imagem será redimensionada para no máximo 3000x3000 pixels.',
    )
    email_contato = models.EmailField(blank=True, verbose_name="Email Principal")
    outros_emails = models.TextField(blank=True, verbose_name="Outros Emails de Contato", help_text="Separe os e-mails por espaço (ex: contato@exemplo.com suporte@exemplo.com)")
    instagram = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)

    logo_link_cbr = models.CharField(blank=True, verbose_name="Link da Logo (CBR)", help_text="Link ao clicar na logo no header CBR")
    logo_link_mnr = models.CharField(blank=True, verbose_name="Link da Logo (MNR)", help_text="Link ao clicar na logo no header MNR")
    logo_link_obr = models.CharField(blank=True, verbose_name="Link da Logo (OBR)", help_text="Link ao clicar na logo no header OBR")

    # cabecalho_admin = models.JSONField(
    #     default=list,
    #     blank=True,
    #     verbose_name="🧩 Componentes",
    # )

    @property
    def headers_with_hidden_items(self):
        return [
            t.lower()
            for t in self.itens_menu.filter(escondido=True).values_list('header_type', flat=True).distinct()
        ]

    class Meta:
        verbose_name = "Config. e Patrocínio"
        verbose_name_plural = "Config. e Patrocínio"

    def __str__(self):
        return "Configurações Globais do Site"

    def clean(self):
        if not self.pk and ConfiguracaoGlobal.objects.exists():
            raise ValidationError("Já existe uma configuração global criada. Edite a existente em vez de criar uma nova.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class AtalhoGlobal(models.Model):
    config = models.ForeignKey(ConfiguracaoGlobal, on_delete=models.CASCADE, related_name='atalhos')
    nome = models.CharField(max_length=100, help_text="Texto do link (ex: 'Material de Divulgação')")
    link = models.CharField(max_length=200, help_text="URL externa (https://...) ou caminho interno (ex: /sobre)")

    class Meta:
        verbose_name = "Atalho de Rodapé"
        verbose_name_plural = "Atalhos de Rodapé"

    def __str__(self):
        return 'Atalho no Rodapé:'

class ItemMenu(models.Model):
    config = models.ForeignKey(ConfiguracaoGlobal, on_delete=models.CASCADE, related_name='itens_menu')
    header_type = models.CharField(
        max_length=50,
        choices=[
            ('RCB', 'Header Padrão RCB'),
            ('OBR', 'Header OBR'),
            ('CBR', 'Header CBR'),
            ('MNR', 'Header MNR'),
        ],
        default='RCB'
    )
    nome = models.CharField(max_length=100, help_text="Texto do link")
    link = models.CharField(max_length=200, help_text="URL externa ou caminho interno")
    escondido = models.BooleanField(default=False, verbose_name="Escondido no Desktop?", help_text="Se marcado, o link aparece fora do menu \"≡\" no computador. Para o menu padrão RCB, manter um item escondido fará o mesmo aparecer em todas as páginas.")

    class Meta:
        verbose_name = "Item do Menu"
        verbose_name_plural = "Itens do Menu"

    def __str__(self):
        if(self.header_type == 'CBR'):
            return 'Atalho no Menu CBR:'
        if(self.header_type == 'MNR'):
            return 'Atalho no Menu MNR:'
        if(self.header_type == 'OBR'):
            return 'Atalho no Menu OBR:'
        if(self.escondido):
            return 'Atalho Global:'

        return 'Atalho no Menu RoboCup:'

class ItemMenuRCB(ItemMenu):
    class Meta:
        proxy = True
        verbose_name = "Item do Menu RCB"
        verbose_name_plural = "Itens do Menu RCB"

class ItemMenuCBR(ItemMenu):
    class Meta:
        proxy = True
        verbose_name = "Item do Menu CBR"
        verbose_name_plural = "Itens do Menu CBR"

class ItemMenuMNR(ItemMenu):
    class Meta:
        proxy = True
        verbose_name = "Item do Menu MNR"
        verbose_name_plural = "Itens do Menu MNR"

class ItemMenuOBR(ItemMenu):
    class Meta:
        proxy = True
        verbose_name = "Item do Menu OBR"
        verbose_name_plural = "Itens do Menu OBR"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    estado = models.CharField(max_length=2, choices=Regiao.choices, blank=True, null=True)

    ligas = models.ManyToManyField('Subevento', blank=True)

    GRUPO_CHOICES = [
        ('', '—'),
        ('SUPER', 'Superusuário'),
        ('SECRETARIA', 'Secretaria'),
        ('COORD', 'Coordenador de Subevento'),
        ('REPRESENTANTE', 'Representante Local'),
        ('MARKETING', 'Marketing'),
    ]
    grupo_extra = models.CharField(max_length=20, choices=GRUPO_CHOICES, blank=True, verbose_name='Grupo de permissão')

    class Meta:
        verbose_name = "Dados Adicionais"
        verbose_name_plural = "Dados Extras do Usuário"

    def __str__(self):
        return f"Dados Adicionais de \"{self.user.username}\""

    def clean(self):
        from django.core.exceptions import ValidationError
        from django.contrib.auth.models import User as DjangoUser

        if self.grupo_extra == 'SUPER':
            if self.user_id is not None:
                existing = DjangoUser.objects.filter(is_superuser=True).exclude(pk=self.user_id)
            else:
                existing = DjangoUser.objects.filter(is_superuser=True)

            if existing.exists():
                raise ValidationError({'grupo_extra': "Já existe um Superusuário. Só pode haver um."})

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
        except Exception:
            raise

        super().save(*args, **kwargs)

        from django.contrib.auth.models import Group, User as DjangoUser
        role_name_map = {
            'SECRETARIA': 'Secretaria',
            'COORD': 'Coordenador de Subevento',
            'REPRESENTANTE': 'Representante Local',
            'MARKETING': 'Marketing',
        }

        managed_group_names = set(role_name_map.values())

        if self.user_id is None:
            return

        user = self.user

        user.groups.remove(*Group.objects.filter(name__in=managed_group_names))

        if self.grupo_extra in role_name_map:
            group_name = role_name_map[self.grupo_extra]
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

        if self.grupo_extra == 'SUPER':
            DjangoUser.objects.filter(pk=user.pk).update(is_superuser=True)
        else:
            if self.grupo_extra == '' and DjangoUser.objects.filter(pk=user.pk, is_superuser=True).exists():
                self.grupo_extra = 'SUPER'
                UserProfile.objects.filter(pk=self.pk).update(grupo_extra='SUPER')
            elif DjangoUser.objects.filter(pk=user.pk, is_superuser=True).exists():
                DjangoUser.objects.filter(pk=user.pk).update(is_superuser=False)

    @property
    def is_secretaria(self):
        return self.grupo_extra == 'SECRETARIA'

    @property
    def is_coordenador(self):
        return self.grupo_extra == 'COORD'

    @property
    def is_representante(self):
        return self.grupo_extra == 'REPRESENTANTE'

    @property
    def is_marketing(self):
        return self.grupo_extra == 'MARKETING'

class Pagina(models.Model):
    nome = models.CharField(max_length=200, help_text="Nome visível da página (ex: 'Notícias OBR')")
    slug = models.SlugField(
        max_length=100,
        blank=True,
        verbose_name='Link',
        help_text="Link único, sem espaços (ex: 'material-divulgacao'). Deixe vazio para a página inicial (/)<br><strong>Atenção:</strong> editar este campo pode quebrar links existentes!"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Página-mãe',
        help_text="Página mãe ou de origem (para hierarquia: pagina-de-origem/sua-pagina)"
    )
    header_type = models.CharField(
        max_length=50,
        choices=[
            ('RCB', 'Header Padrão RCB'),
            ('OBR', 'Header OBR'),
            ('CBR', 'Header CBR'),
            ('MNR', 'Header MNR'),
        ],
        default='RCB',
        verbose_name="Cabeçalho da Página"
    )
    componentes = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Configuração da Página",
    )
    # removed HTML cache field

    evento_associado = models.CharField(
        max_length=50,
        choices=Evento.choices,
        blank=True,
        null=True,
    )
    privada = models.BooleanField(
        default=False,
        verbose_name="🔒 Página Privada?",
        help_text="Se verdadeiro, a página só é visível para quem tiver o link de acesso."
    )

    class Meta:
        ordering = ['nome']
        verbose_name = "Página Dinâmica"
        verbose_name_plural = "Páginas Dinâmicas"
        constraints = [
            models.UniqueConstraint(fields=['parent', 'slug'], name='unique_parent_slug'),
            models.UniqueConstraint(fields=['slug'], condition=models.Q(parent__isnull=True), name='unique_root_slug'),
        ]

    def __str__(self):
        if not self.slug:
            return "Página Inicial (Raiz)"
        return self.nome

    def get_absolute_url(self):
        if self.parent:
            return f"{self.parent.get_absolute_url()}/{self.slug}/"
        return f"/{self.slug}/" if self.slug else '/'

    def clean(self):
        # sanitize components JSON to avoid dangerous snippets
        _sanitize_recursive(self.componentes)

        from django.core.exceptions import ValidationError

        prohibited_slugs = ['noticia', 'estado', 'evento', 'sede', 'static', 'media', 'admin']
        if self.slug in prohibited_slugs:
            raise ValidationError(f"Slug '{self.slug}' é reservado e não pode ser usado.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Sede(GlobalQueryMixin, models.Model):
    ano = models.CharField(max_length=4, help_text="Ano (ex: 2026)", unique=True)
    cidade = models.CharField(max_length=200)
    estado = models.CharField(max_length=2, choices=Regiao.choices)
    componentes = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Configuração da Página",
    )
    # removed HTML cache field


    class Meta:
        ordering = ['ano']
        verbose_name = "Sede"
        verbose_name_plural = "Sedes"

    def __str__(self):
        return f"{self.ano} - {self.cidade}, {self.estado}"

    def clean(self):
        _sanitize_recursive(self.componentes)

    @classmethod
    def get_sedes_list(cls):
        return list(cls.objects.order_by('-ano').values_list('cidade', 'ano'))

class PaginaEstado(models.Model):
    estado = models.CharField(
        max_length=2,
        choices=Regiao.choices,
        unique=True
    )
    componentes = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Configuração da Página",
    )

    class Meta:
        verbose_name = "Página do Estado"
        verbose_name_plural = "Páginas dos Estados"

    def __str__(self):
        return f"Página de {self.get_estado_display()} ({self.estado})"

    def clean(self):
        _sanitize_recursive(self.componentes)

    def get_absolute_url(self):
        return f"/estado/{self.estado.lower()}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        pass

@receiver(post_delete, sender=Funcionario)
def delete_funcionario_foto(sender, instance, **kwargs):
    if instance.foto:
        instance.foto.delete(save=False)

@receiver(post_delete, sender=Noticia)
def delete_noticia_imagem(sender, instance, **kwargs):
    if instance.imagem:
        instance.imagem.delete(save=False)

@receiver(post_delete, sender=Arquivo)
def delete_arquivo_files(sender, instance, **kwargs):
    if instance.arquivo:
        instance.arquivo.delete(save=False)
    if instance.thumbnail:
        instance.thumbnail.delete(save=False)

@receiver(post_delete, sender=Subevento)
def delete_subevento_icone(sender, instance, **kwargs):
    if instance.icone:
        instance.icone.delete(save=False)

@receiver(post_delete, sender=ConfiguracaoGlobal)
def delete_config_patrocinios(sender, instance, **kwargs):
    if instance.patrocinio_vertical:
        instance.patrocinio_vertical.delete(save=False)
    if instance.patrocinio_horizontal:
        instance.patrocinio_horizontal.delete(save=False)

# Cacheing strategy:
# Invalida o cache em qualquer alteração nos modelos que afetam o front-end
RELEVANT_MODELS_FOR_CACHE = [
    'Noticia', 'Funcionario', 'Arquivo', 'Data', 'ItemMenu', 'AtalhoGlobal', 
    'ConfiguracaoGlobal', 'Pagina', 'PaginaEstado', 'Sede', 'Subevento', 
    'TagNoticia', 'TagFuncionario', 'TagData', 'TagArquivo',
    'ItemMenuRCB', 'ItemMenuCBR', 'ItemMenuMNR', 'ItemMenuOBR'
]

@receiver(post_save)
def cache_invalidator_on_save(sender, instance, **kwargs):
    """Limpa o cache em qualquer save (criação ou edição) de modelos relevantes."""
    if sender.__name__ in RELEVANT_MODELS_FOR_CACHE:
        transaction.on_commit(lambda: cache.clear())

@receiver(post_delete)
def cache_invalidator_on_delete(sender, instance, **kwargs):
    """Limpa o cache em qualquer delete de modelos relevantes."""
    if sender.__name__ in RELEVANT_MODELS_FOR_CACHE:
        transaction.on_commit(lambda: cache.clear())