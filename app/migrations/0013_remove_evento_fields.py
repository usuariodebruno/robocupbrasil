from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_data_owner_alter_data_action_link_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='funcionario',
            name='evento',
        ),
        migrations.RemoveField(
            model_name='noticia',
            name='evento',
        ),
        migrations.RemoveField(
            model_name='arquivo',
            name='evento',
        ),
    ]
