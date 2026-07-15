from datetime import date
from functools import wraps

from django.views.decorators.cache import cache_page


def cache_page_diario(timeout):
    """``cache_page`` que também expira na virada do dia.

    O projeto já limpa o cache por signal quando um modelo do front-end muda
    (ver ``cache_invalidator_on_save`` em ``app.models``), mas nada dispara à
    meia-noite. Uma view que renderiza componentes dependentes de
    ``date.today()`` — o calendário, por exemplo — continuaria servindo o
    "hoje" de ontem até o timeout vencer. Embutir a data no ``key_prefix`` dá
    a cada dia um espaço de chaves próprio.

    O ``cache_page`` é montado por requisição porque ``key_prefix`` é fixado
    no momento da decoração e precisa acompanhar o calendário.
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            view_cacheada = cache_page(timeout, key_prefix=date.today().isoformat())(view_func)
            return view_cacheada(request, *args, **kwargs)

        return wrapper

    return decorator
