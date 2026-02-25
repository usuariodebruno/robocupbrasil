# markdown conversion is now handled on the front end; backend simply
# returns the raw text.  The import remains hidden in case older code still
# calls markdown(), but it will just return the input.

def markdown(text):
    return str(text or '')

from django.template import Engine, Context

# Renderer for componentes JSON to HTML.  Supports the richer schema
# described in claude.txt.  Accepts an optional ``extra_context`` dict of
# variables made available to dynamic component templates (e.g. lists of
# funcionarios, noticias, etc gathered by the view).


def render_components_to_html(componentes, extra_context=None):
    """Render a list of componentes (JSON) into an HTML string.

    ``extra_context`` should be a dictionary containing any objects or
    querysets that dynamic components may refer to by name.  For instance,
    ``estado_view`` always passes ``{'funcionarios': funcionarios}`` so a
    JSON item with ``"items": "funcionarios"`` will receive that list.
    """

    if extra_context is None:
        extra_context = {}

    out = []
    section_counter = 0

    def render_list(lst):
        return render_components_to_html(lst, extra_context)

    for c in componentes or []:
        if not isinstance(c, dict):
            out.append(f"<div class=\"component-unknown\">{c}</div>")
            continue

        t = c.get('type') or c.get('tipo')
        if t is None:
            # backwards compatibility with very simple objects
            if 'markdown' in c or 'texto' in c:
                md = c.get('markdown') or c.get('texto') or ''
                html = markdown(md)
                out.append(f"<div class=\"component-content\">{html}</div>")
            else:
                out.append(f"<div class=\"component-unknown\">{c}</div>")
            continue

        # section handling
        if t == 'section':
            classes = []
            if c.get('bg'):
                classes.append(f"bg-{c['bg']}")
            for axis in ('', 'x', 'y'):
                for prop in ('padding', 'margin'):
                    val = c.get(f"{prop}{'_'+axis if axis else ''}")
                    if val is not None:
                        key = f"{prop}{'-'+axis if axis else ''}-{val}"
                        classes.append(key)
            if c.get('inside_top'):
                classes.append('inside-top')
            if c.get('inside_bottom'):
                classes.append('inside-bottom')
            # preserve any user-supplied class list on the section itself
            if c.get('classes'):
                classes.extend(str(c['classes']).split())

            # id handling: use provided id or auto‑generate sequential
            sec_id = c.get('id')
            if not sec_id:
                sec_id = f"section-{section_counter}"
                section_counter += 1
            # also add id to classes so old CSS still works
            classes.append(f"id-{sec_id}")

            html = f"<section id=\"{sec_id}\" class=\"{' '.join(classes)}\">"
            for bd in c.get('border_details', []):
                bd_classes = []
                if bd.get('container'):
                    bd_classes.append('container')
                bd_classes.append(bd.get('type', ''))
                if bd.get('color'):
                    bd_classes.append(bd['color'])
                if bd.get('position'):
                    bd_classes.append(bd['position'])
                if bd.get('size'):
                    bd_classes.append(bd['size'])
                if bd.get('spin'):
                    bd_classes.append('spin')
                if bd.get('desktop_only'):
                    bd_classes.append('desktop-only')
                if bd.get('mobile_only'):
                    bd_classes.append('mobile-only')
                if bd.get('margin_t'):
                    bd_classes.append(f"margin-t-{bd['margin_t']}")
                html += f"<border-detail class=\"{' '.join(bd_classes)}\"></border-detail>"

            if c.get('content'):
                html += str(c['content'])

            main = c.get('main')
            if main:
                mclasses = []
                if main.get('bg'):
                    mclasses.append(f"bg-{main['bg']}")
                if main.get('container'):
                    mclasses.append('container')
                if main.get('flex'):
                    mclasses.append('flex')
                for flexprop in ('flex_wrap','flex_row','flex_column','flex_center',
                                 'flex_start','flex_end','flex_between','flex_around','flex_evenly',
                                 'flex_reverse'):
                    if main.get(flexprop):
                        mclasses.append(flexprop.replace('_','-'))
                if main.get('padding'):
                    mclasses.append(f"padding-{main['padding']}")
                if main.get('margin'):
                    mclasses.append(f"margin-{main['margin']}")
                # allow arbitrary extra classes on main
                if main.get('classes'):
                    mclasses.extend(str(main['classes']).split())
                html += f"<main class=\"{' '.join(mclasses)}\">"
                if main.get('content'):
                    html += str(main['content'])
                if c.get('components'):
                    html += render_list(c['components'])
                html += "</main>"

            if c.get('components') and not main:
                html += render_list(c['components'])

            html += "</section>"
            out.append(html)
            continue

        # template renderer helper
        def render_template(name, ctx):
            try:
                tpl = Engine.get_default().get_template(name)
                return tpl.render(Context(ctx))
            except Exception as e:
                return f"<!-- error rendering {name}: {e} -->"

        # New specific slider components
        if t.startswith('slider_'):
            from app.models import Sede, Subevento, Funcionario, Arquivo

            ctx = {**c}
            items = []
            item_template = ""
            model = None
            comp_type = t.split('slider_')[1]

            if comp_type == 'sedes':
                model = Sede
                items = model.get_items(limit=c.get('limit', 50))
                item_template = "components/dynamic/sliders/slider_item_sede.html"

            elif comp_type == 'subeventos':
                model = Subevento
                items = model.get_items(limit=c.get('limit', 50), evento=c.get('evento'))
                item_template = "components/dynamic/sliders/slider_item_subevento.html"

            elif comp_type == 'funcionarios':
                model = Funcionario
                items = model.get_items(limit=c.get('limit', 10), tag_ids=c.get('tags'))
                item_template = "components/dynamic/sliders/slider_item_funcionario.html"
                ctx['size'] = c.get('size', 'medium') # Pass size to context

            elif comp_type == 'arquivos':
                model = Arquivo
                items = model.get_items(limit=c.get('limit', 10), tag_ids=c.get('tags'))
                item_template = "components/dynamic/sliders/slider_item_arquivo.html"

            if items:
                ctx['items'] = items
                ctx['item_template'] = item_template
                out.append(render_template("components/dynamic/slider.html", ctx))
            
            continue

        if t == 'arquivo_viewer':
            from app.models import Arquivo
            ctx = {**c}
            arquivo_id = c.get('arquivo_id')
            if arquivo_id:
                try:
                    arquivo = Arquivo.objects.get(pk=int(arquivo_id))
                    ctx['arquivo'] = arquivo
                    out.append(render_template("components/dynamic/arquivo.html", ctx))
                except (Arquivo.DoesNotExist, ValueError, TypeError):
                    # Fail silently if the ID is invalid or not found
                    pass
            continue

        # dynamic components (prefix dynamic_) - old slider logic is removed from here
        if t.startswith('dynamic_'):
            comp = t.split('dynamic_')[1]
            ctx = {}

            # copy all keys, but if the value is a string referencing an
            # item in extra_context, substitute the real object.  this
            # handles "items" as well as component-specific variable names
            for key, v in c.items():
                if isinstance(v, str) and v in extra_context:
                    ctx[key] = extra_context[v]
                else:
                    ctx[key] = v

            out.append(render_template(f"components/dynamic/{comp}.html", ctx))
            continue

        # static content widgets
        if t in ('tabs', 'accordion', 'carousel'):
            # carousel historically used "slides" key in JSON, but the
            # template expects "tabs" (it reuses the tabs code).  alias if
            # necessary so both work.
            ctx = {**c}
            if t == 'carousel' and 'slides' in ctx:
                ctx['tabs'] = ctx.pop('slides')
            # support simple style shortcuts: put style value into the
            # template variable the markup uses
            if 'style' in ctx:
                ctx['style_classes'] = ctx.get('style') or ''
            # keep any explicit classes as well
            if 'classes' in ctx:
                ctx['style_classes'] = (ctx.get('style_classes','') + ' ' + ctx['classes']).strip()
            out.append(render_template(f"components/content/{t}.html", ctx))
            continue

        # fallback: try generic content include path
        out.append(render_template(f"components/content/{t}.html", c))

    return '\n'.join(out)
