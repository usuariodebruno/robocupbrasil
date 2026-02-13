from .models import ConfiguracaoGlobal

def carregar_configuracao(request):
    return {
        'config_global': ConfiguracaoGlobal.objects.first()
    }