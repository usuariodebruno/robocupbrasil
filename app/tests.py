from django.test import TestCase

from .utils.render_components import render_components_to_html


class RenderComponentsTests(TestCase):
    def test_dynamic_texto_renders_container(self):
        comps = {"type": "dynamic_texto", "conteudo": "# Hello\nWorld"}
        html = render_components_to_html([comps])
        self.assertIn('texto-container', html)
        self.assertIn('# Hello\nWorld', html)  # raw text should be preserved
        self.assertIn('markdown-spinner', html)
        # when raw markdown is hidden it should appear in markup
        self.assertIn('<div class="markdown-raw"', html)

    def test_dynamic_slider_with_items_from_context(self):
        # slider uses "items" in context and expects an "item_template" to exist;
        # we create a simple template file under app/templates/test_slider_item.html
        comps = [{"type": "dynamic_slider", "items": "things", "item_template": "test_slider_item.html"}]
        html = render_components_to_html(comps, {"things": [1, 2, 3]})
        self.assertIn('1', html)
        self.assertIn('2', html)
        self.assertIn('3', html)

    def test_section_padding_and_margin(self):
        comps = [{"type": "section", "padding": "2", "margin_x": "1", "content": "OK"}]
        html = render_components_to_html(comps)
        # should have corresponding classes
        self.assertIn('padding-2', html)
        self.assertIn('margin-x-1', html)
        self.assertIn('OK', html)

    def test_named_context_resolution(self):
        # ensure that component keys other than "items" can refer to extra
        # context names by using a string value
        mylist = ["a", "b"]
        comps = [{"type": "dynamic_noticias", "noticias": "mylist"}]
        html = render_components_to_html(comps, {"mylist": mylist})
        # should iterate over 2 items (characters are rendered because they are
        # simple strings in our fake notice template)
        self.assertEqual(html.count('class="noticia"'), 2)

    def test_slider_default_item_template(self):
        # the renderer should guess a template based on the type of items
        # we have committed a physical template file at
        # components/dynamic/sliders/slider_item_foo.html already.
        class Foo:
            def __init__(self, v): self.v = v
        items = [Foo(1), Foo(2)]

        comps = [{"type": "dynamic_slider", "items": "things"}]
        html = render_components_to_html(comps, {"things": items})
        self.assertIn('1', html)
        self.assertIn('2', html)

    def test_dynamic_arquivo_and_calendar(self):
        class Dummy:
            def __init__(self, url): self.arquivo = type('O', (), {'url': url})
        arquivo = Dummy('http://example.com/doc.pdf')
        comps = [
            {"type": "dynamic_arquivo", "arquivo": "myfile"},
            {"type": "dynamic_calendar", "datas": "mydates"},
        ]
        mydates = [type('D', (), {'data': '2026-01-01', 'descricao': 'x', 'cor': 'red', 'action_link': ''})]
        html = render_components_to_html(comps, {"myfile": arquivo, "mydates": mydates})
        # arquivo should appear in source attribute
        self.assertIn('source="http://example.com/doc.pdf"', html)
        # calendar should contain exactly one event card
        self.assertIn('event-card', html)
    def test_carousel_slides_alias(self):
        comps1 = [{"type": "carousel", "tabs": [{"id": "a", "label": "L", "content": "C"}], "style": "foo bar"}]
        html1 = render_components_to_html(comps1)
        self.assertIn('carousel-slide', html1)
        self.assertIn('foo bar', html1)
        comps2 = [{"type": "carousel", "slides": [{"id": "b", "label": "L2", "content": "C2"}], "style": "baz"}]
        html2 = render_components_to_html(comps2)
        self.assertIn('carousel-slide', html2)
        self.assertIn('baz', html2)

    def test_section_id_and_main_classes(self):
        # section with no id should get auto id and respect main.classes
        comps = [{"type": "section", "content": "X"},
                 {"type": "section", "id": "foo", "content": "Y",
                  "main": {"classes": "bg-yin flex"}}]
        html = render_components_to_html(comps)
        # first section has generated id (prefix 'section-')
        self.assertRegex(html, r'<section id="section-\d+"')
        # second section uses provided id
        self.assertIn('id="foo"', html)
        self.assertIn('class="bg-yin flex"', html)

    def test_imagem_extra_classes_and_fullwidth_flag(self):
        comps = [{"type": "imagem", "imagem": "/foo.png", "titulo": "T", "rounded": True, "classes": "foo", "fullwidth": False}]
        html = render_components_to_html(comps)
        # custom classes should be preserved
        self.assertIn('foo', html)
        # not fullwidth, so w-100 shouldn't be added automatically
        self.assertNotIn('w-100', html)
        # if fullwidth is requested we should see w-100
        comps2 = [{"type": "imagem", "imagem": "/foo.png", "titulo": "T", "rounded": True, "fullwidth": True}]
        html2 = render_components_to_html(comps2)
        self.assertIn('w-100', html2)

    def test_texto_fullwidth_flag(self):
        comps = [{"type": "dynamic_texto", "conteudo": "Hello", "fullwidth": False}]
        html = render_components_to_html(comps)
        self.assertNotIn('w-100', html)
