from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField
import jsonfield

def validate_file_size_8mb(f):
    if f and getattr(f, 'size', 0) > 8 * 1024 * 1024:
        raise ValidationError("Tamanho máximo do arquivo: 8MB.")

def validate_file_size_16mb(f):
    if f and getattr(f, 'size', 0) > 16 * 1024 * 1024:
        raise ValidationError("Tamanho máximo do arquivo: 16MB.")

def validate_file_size_64mb(f):
    if f and getattr(f, 'size', 0) > 64 * 1024 * 1024:
        raise ValidationError("Tamanho máximo do arquivo: 64MB.")

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

    def __str__(self):
        return self.nome

class Funcionario(models.Model):
    nome = models.CharField(max_length=200)
    cargo = models.CharField(max_length=200)
    tags = models.ManyToManyField(TagFuncionario)
    bio = models.TextField(blank=True)
    foto = models.ImageField(
        upload_to='fotos_funcionarios/',
        blank=True,
        verbose_name='Foto (tam. ideal 512x512)',
        help_text='Tamanho máximo: 8MB',
        validators=[validate_file_size_8mb],
    )

    def __str__(self):
        return self.nome or f"Funcionário {self.id}"

class TagNoticia(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Noticia(models.Model):
    titulo = models.CharField(max_length=200)
    conteudo = RichTextField()
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

    def __str__(self):
        return self.titulo

class TagData(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Data(models.Model):
    descricao = models.CharField(max_length=200, verbose_name='Descrição')
    data = models.DateField()
    cor = models.CharField(max_length=7, default='#000000')
    action_link = models.URLField(blank=True, verbose_name='Link de mais informações')
    tags = models.ManyToManyField(TagData)

    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, editable=False)

    def __str__(self):
        return f"{self.descricao} ({self.data})"

    class Meta:
        verbose_name = "Data no Calendário"
        verbose_name_plural = "Datas no Calendário"

class TagArquivo(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Arquivo(models.Model):
    nome = models.CharField(max_length=200)
    arquivo = models.FileField(
        upload_to='arquivos/',
        verbose_name='Arquivo (tamanho máximo 64MB)',
        help_text='Tamanho máximo: 64MB',
        validators=[validate_file_size_64mb],
    )
    tags = models.ManyToManyField(TagArquivo)

    def __str__(self):
        return self.nome

class Subevento(models.Model):
    nome = models.CharField(max_length=200)
    evento = models.CharField(max_length=50, choices=Evento.choices)
    icone = models.ImageField(
        upload_to='icones/',
        blank=True,
        verbose_name='Ícone (tam. ideal 256x256)',
        help_text='Tamanho máximo: 8MB',
        validators=[validate_file_size_8mb],
    )
    quadro_avisos = RichTextField(verbose_name='Quadro de Avisos da Liga / Subevento')

    class Meta:
        verbose_name = "Subevento (Liga)"
        verbose_name_plural = "Subeventos (Ligas)"

    def __str__(self):
        return self.nome

class ConfiguracaoGlobal(models.Model):
    descricao = models.TextField(blank=True, verbose_name="Descrição da Página (para o Google e Rodapé)")
    patrocinio_vertical = models.ImageField(upload_to='patrocinio/', verbose_name="Patrocínio Vertical (Celular)", blank=True)
    patrocinio_horizontal = models.ImageField(upload_to='patrocinio/', verbose_name="Patrocínio Horizontal (Computador)", blank=True)
    email_contato = models.EmailField(blank=True, verbose_name="Email Principal")
    outros_emails = models.TextField(blank=True, verbose_name="Outros Emails de Contato", help_text="Separe os e-mails por espaço (ex: contato@exemplo.com suporte@exemplo.com)")
    instagram = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)

    logo_link_rcb = models.CharField(blank=True, verbose_name="Link da Logo (RCB)", help_text="Link ao clicar na logo no header RCB")
    logo_link_cbr = models.CharField(blank=True, verbose_name="Link da Logo (CBR)", help_text="Link ao clicar na logo no header CBR")
    logo_link_mnr = models.CharField(blank=True, verbose_name="Link da Logo (MNR)", help_text="Link ao clicar na logo no header MNR")
    logo_link_obr = models.CharField(blank=True, verbose_name="Link da Logo (OBR)", help_text="Link ao clicar na logo no header OBR")

    class Meta:
        verbose_name = "Config. e Patrocínio"
        verbose_name_plural = "Config. e Patrocínio"

    def __str__(self):
        return "Configurações Globais do Site"

class AtalhoGlobal(models.Model):
    config = models.ForeignKey(ConfiguracaoGlobal, on_delete=models.CASCADE, related_name='atalhos')
    nome = models.CharField(max_length=100, help_text="Texto do link (ex: 'Material de Divulgação')")
    link = models.CharField(max_length=200, help_text="URL externa (https://...) ou caminho interno (ex: /sobre)")

    class Meta:
        verbose_name = "Atalho de Rodapé"
        verbose_name_plural = "Atalhos de Rodapé"

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
    escondido = models.BooleanField(default=False, verbose_name="Escondido no Desktop?", help_text="Se marcado, aparece apenas no menu hamburger no Desktop. No mobile, todos aparecem no hamburger.")

    class Meta:
        verbose_name = "Item do Menu"
        verbose_name_plural = "Itens do Menu"

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
        unique=True,
        blank=True,
        verbose_name='Link',
        help_text="Link único, sem espaços (ex: 'noticias-obr'). Deixe vazio para a página inicial (/)<br><strong>Atenção:</strong> editar este campo pode quebrar links existentes!"
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
        verbose_name="🧩 Componentes",
    )
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

    def __str__(self):
        if not self.slug:
            return "Página Inicial (Raiz)"
        return self.nome

    def get_absolute_url(self):
        if self.parent:
            return f"{self.parent.get_absolute_url()}/{self.slug}/"
        return f"/{self.slug}/" if self.slug else '/'

    def clean(self):
        from django.core.exceptions import ValidationError

        prohibited_slugs = ['noticia', 'estado', 'static', 'media', 'admin']
        if self.slug in prohibited_slugs:
            raise ValidationError(f"Slug '{self.slug}' é reservado e não pode ser usado.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Sede(models.Model):
    ano = models.CharField(max_length=4, help_text="Ano (ex: 2026)")
    cidade = models.CharField(max_length=200)
    estado = models.CharField(max_length=2, choices=Regiao.choices)
    imagem = models.ImageField(
        upload_to='sedes/',
        blank=True,
        verbose_name='Imagem (16:9, tam. ideal 1920x1080)',
        help_text='Tamanho máximo: 16MB',
        validators=[validate_file_size_16mb],
    )

    class Meta:
        ordering = ['ano']

    def __str__(self):
        return f"{self.ano} - {self.cidade}, {self.estado}"

class PaginaEstado(models.Model):
    estado = models.CharField(
        max_length=2,
        choices=Regiao.choices,
        unique=True
    )
    texto = RichTextField(
        blank=True,
        verbose_name = "Conteúdo da Página",
    )

    class Meta:
        verbose_name = "Página do Estado"
        verbose_name_plural = "Páginas dos Estados"

    def __str__(self):
        return f"Página de {self.get_estado_display()} ({self.estado})"

    def get_absolute_url(self):
        return f"/{self.estado.lower()}/"

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