from django import template

register = template.Library()

@register.filter
def get_model_icon(model_name):
    mapping = {
        'arquivo': 'far fa-file-alt',
        'configuracaoglobal': 'far fa-sun',
        'data': 'far fa-calendar-alt',
        'funcionario': 'far fa-address-card',
        'noticia': 'far fa-newspaper',
        'pagina': 'far fa-file-code',
        'paginaestado': 'far fa-map',
        'sede': 'far fa-building',
        'subevento': 'far fa-star',
        'tagarquivo': 'far fa-sticky-note',
        'tagdata': 'far fa-calendar-check',
        'tagfuncionario': 'far fa-id-badge',
        'tagnoticia': 'far fa-comment-alt',
        'user': 'far fa-user',
        'logentry': 'far fa-list-alt',
    }
    
    return mapping.get(model_name.lower(), 'far fa-circle')