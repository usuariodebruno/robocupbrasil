from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_arquivo_descricao_arquivo_thumbnail_and_more'),
    ]

    operations = [
        # remove HTML cache fields
        migrations.RemoveField(
            model_name='subevento',
            name='componentes_html',
        ),
        migrations.RemoveField(
            model_name='pagina',
            name='componentes_html',
        ),
        migrations.RemoveField(
            model_name='sede',
            name='componentes_html',
        ),
        # change Noticia.conteudo to plain TextField
        migrations.AlterField(
            model_name='noticia',
            name='conteudo',
            field=models.TextField(),
        ),
    ]
