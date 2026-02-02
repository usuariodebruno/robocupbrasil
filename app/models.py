from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from ckeditor.fields import RichTextField
import jsonfield

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
    def bandeira(self):
        bandeiras = {
            'AC': '/media/bandeiras/ac.png',
            'AL': '/media/bandeiras/al.png',
            'AP': '/media/bandeiras/ap.png',
            'AM': '/media/bandeiras/am.png',
            'BA': '/media/bandeiras/ba.png',
            'CE': '/media/bandeiras/ce.png',
            'DF': '/media/bandeiras/df.png',
            'ES': '/media/bandeiras/es.png',
            'GO': '/media/bandeiras/go.png',
            'MA': '/media/bandeiras/ma.png',
            'MT': '/media/bandeiras/mt.png',
            'MS': '/media/bandeiras/ms.png',
            'MG': '/media/bandeiras/mg.png',
            'PA': '/media/bandeiras/pa.png',
            'PB': '/media/bandeiras/pb.png',
            'PR': '/media/bandeiras/pr.png',
            'PE': '/media/bandeiras/pe.png',
            'PI': '/media/bandeiras/pi.png',
            'RJ': '/media/bandeiras/rj.png',
            'RN': '/media/bandeiras/rn.png',
            'RS': '/media/bandeiras/rs.png',
            'RO': '/media/bandeiras/ro.png',
            'RR': '/media/bandeiras/rr.png',
            'SC': '/media/bandeiras/sc.png',
            'SP': '/media/bandeiras/sp.png',
            'SE': '/media/bandeiras/se.png',
            'TO': '/media/bandeiras/to.png',
        }
        return bandeiras.get(self.value, '')

class TagFuncionario(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Funcionario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    evento = models.CharField(max_length=50, choices=Evento.choices)
    tags = models.ManyToManyField(TagFuncionario)
    bio = models.TextField(blank=True)
    foto = models.ImageField(upload_to='fotos_funcionarios/', blank=True)
    nome = models.CharField(max_length=200)
    cargo = models.CharField(max_length=200)

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
        verbose_name="Tipo de Header",
        help_text="Qual header usar nesta notícia (como se fosse uma página)"
    )
    evento = models.CharField(max_length=50, choices=Evento.choices)
    tags = models.ManyToManyField(TagNoticia)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class TagData(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Data(models.Model):
    descricao = models.CharField(max_length=200)
    data = models.DateField()
    cor = models.CharField(max_length=7, default='#000000')
    action_link = models.URLField(blank=True)
    tags = models.ManyToManyField(TagData)

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
    arquivo = models.FileField(upload_to='arquivos/')
    evento = models.CharField(max_length=50, choices=Evento.choices)
    tags = models.ManyToManyField(TagArquivo)

    def __str__(self):
        return self.nome

class Subevento(models.Model):
    nome = models.CharField(max_length=200)
    evento = models.CharField(max_length=50, choices=Evento.choices)
    icone = models.ImageField(upload_to='icones/', blank=True)
    quadro_avisos = RichTextField()

    def __str__(self):
        return self.nome

class ConfiguracaoGlobal(models.Model):
    patrocinio_imagem = models.ImageField(upload_to='patrocinio/', blank=True)
    patrocinio_link = models.URLField(blank=True)
    email_contato = models.EmailField(blank=True)
    instagram = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)

    class Meta:
        verbose_name = "Configurações e Patrocínio"
        verbose_name_plural = "Configurações e Patrocínio"

    def __str__(self):
        return "Configurações Globais do Site"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    estado = models.CharField(max_length=2, choices=Regiao.choices, blank=True, null=True)
    ligas = models.JSONField(default=list, blank=True)
    grupo_extra = models.CharField(max_length=50, blank=True)   # opcional: "content-admin", etc.

    def __str__(self):
        return f"Perfil de {self.user.username}"

class Pagina(models.Model):
    nome = models.CharField(max_length=200, help_text="Nome visível da página (ex: 'Notícias OBR')")
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="Link único, sem espaços (ex: 'noticias-obr'). Deixe vazio para a página inicial (/)"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        help_text="Página pai/origem (para hierarquia)"
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
        help_text="Tipo de header para a página"
    )
    componentes = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista ordenada de componentes: [{'type': 'equipe', 'tags': ['obr'], 'title': 'Equipe'}, ...]. A ordem aqui define a exibição."
    )
    mostrar_no_menu = models.BooleanField(
        default=False,
        help_text="Mostrar esta página no menu correspondente ao header_type (apenas páginas de 1º nível)"
    )
    evento_associado = models.CharField(
        max_length=50,
        choices=Evento.choices,
        blank=True,
        null=True,
        help_text="Evento ligado (para filtros automáticos)"
    )
    privada = models.BooleanField(
        default=False,
        verbose_name="Privada",
        help_text="Se verdadeiro, adiciona meta robots noindex no head da página."
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

        prohibited_slugs = ['noticias', 'estados', 'static', 'media', 'admin']
        if self.slug in prohibited_slugs:
            raise ValidationError(f"Slug '{self.slug}' é reservado e não pode ser usado.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Sede(models.Model):
    ano = models.CharField(max_length=4, help_text="Ano (ex: 2026)")
    cidade = models.CharField(max_length=200)
    estado = models.CharField(max_length=2, choices=Regiao.choices)
    imagem = models.ImageField(upload_to='sedes/', blank=True)

    class Meta:
        ordering = ['ano']

    def __str__(self):
        return f"{self.ano} - {self.cidade}, {self.estado}"

class PaginaEstado(models.Model):
    estado = models.CharField(
        max_length=2,
        choices=Regiao.choices,
        unique=True,
        help_text="Selecione o estado (único por página)"
    )
    texto = RichTextField(
        blank=True,
        help_text="Conteúdo da página do estado (use CKEditor para HTML rico)"
    )

    class Meta:
        verbose_name = "Página do Estado"
        verbose_name_plural = "Páginas dos Estados"

    def __str__(self):
        return f"Página de {self.get_estado_display()} ({self.estado})"

    def get_absolute_url(self):
        return f"/{self.estado.lower()}/"

    @property
    def bandeira(self):
        return Regiao[self.estado].bandeira

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()