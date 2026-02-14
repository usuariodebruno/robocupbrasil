from .models import ConfiguracaoGlobal, Regiao


def carregar_configuracao(request):
    return {
        'config_global': ConfiguracaoGlobal.objects.first(),
        'Regiao': Regiao,
    }