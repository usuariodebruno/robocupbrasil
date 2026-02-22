from django import template
from urllib.parse import urlparse

register = template.Library()


@register.filter(is_safe=True)
def file_extension(value):
    try:
        if hasattr(value, 'name') and value.name:
            path = value.name
        elif hasattr(value, 'url') and value.url:
            path = value.url
        else:
            path = str(value or '')

        parsed = urlparse(path)
        filename = parsed.path.rsplit('/', 1)[-1]

        if '.' in filename:
            return filename.rsplit('.', 1)[-1].lower()
    except Exception:
        pass
    return ''
