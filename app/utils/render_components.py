try:
    from markdown import markdown
except Exception:
    def markdown(text):
        # fallback: very small passthrough (no markdown processing)
        return '<pre>'+ (str(text) or '') +'</pre>'

from django.template import Engine, Context

# Very small renderer for componentes JSON to HTML. Extend as needed.

def render_components_to_html(componentes):
    """Render a list of componentes (JSON) into a minimal HTML string.

    Supported component types (basic):
    - content: {'type':'content','markdown': '...'}
    - title: {'type':'title','texto':'...', 'evento':'RCB'}
    - grid: {'type':'grid','columns_mobile':1,'columns_desktop':3,'items':[...]} (renders a flex grid)
    - button: {'type':'button','text':'...', 'bg':'#000', 'fg':'#fff', 'href':'...'}

    WIP
    """
    out = []
    for c in componentes or []:
        t = c.get('type')
        if t == 'content':
            md = c.get('markdown') or c.get('texto') or ''
            html = markdown(md)
            out.append(f"<div class=\"component-content\">{html}</div>")
        elif t == 'title':
            texto = c.get('texto','')
            evento = c.get('evento','')
            out.append(f"<h2 class=\"header-line ribbon-{evento.lower()}\">{texto}</h2>")
        elif t == 'grid':
            items = c.get('items', [])
            cols = c.get('columns_desktop', 3)
            out.append(f"<div class=\"rcb-grid\" style=\"display:flex;gap:1rem;flex-wrap:wrap;\">")
            for it in items:
                out.append(f"<div style=\"flex:1 1 calc({100/cols}% - 1rem);\">{render_components_to_html([it])}</div>")
            out.append('</div>')
        elif t == 'button':
            text = c.get('text','Clique')
            href = c.get('href','#')
            bg = c.get('bg','#000')
            fg = c.get('fg','#fff')
            out.append(f"<a class=\"rcb-button\" href=\"{href}\" style=\"background:{bg};color:{fg};padding:0.5rem 1rem;border-radius:6px;display:inline-block;\">{text}</a>")
        else:
            # fallback: dump raw
            out.append(f"<div class=\"component-unknown\">{c}</div>")
    return '\n'.join(out)
