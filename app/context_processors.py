from .models import (
    ConfiguracaoGlobal, Regiao,
    TagFuncionario, TagArquivo, TagData, TagNoticia,
    Sede, Funcionario, Noticia, Arquivo, Data, Subevento
)

def carregar_globais(request):
    return {
        'config_global': ConfiguracaoGlobal.objects.first(),
        'Regiao': Regiao,

        # Tags
        'all_tags_funcionario': TagFuncionario.objects.all(),
        'all_tags_arquivo': TagArquivo.objects.all(),
        'all_tags_data': TagData.objects.all(),
        'all_tags_noticia': TagNoticia.objects.all(),

        # Getters for lists of objects
        'get_sedes_list': Sede.get_sedes_list,
        'get_sedes': Sede.get_items,
        'get_funcionarios': Funcionario.get_items,
        'get_noticias': Noticia.get_items,
        'get_arquivos': Arquivo.get_items,
        'get_datas': Data.get_items,
        'get_subeventos': Subevento.get_items,
    }