# Generated by Django 5.1.7 on 2025-03-21 00:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abon_app', '0004_alter_setor_responsavel_funcionario'),
    ]

    operations = [
        migrations.CreateModel(
            name='Configuracao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_abonadas_ano', models.PositiveSmallIntegerField(default=10, verbose_name='Quantidade Máxima de Abonadas Comuns por Ano')),
                ('max_abonadas_mes', models.PositiveSmallIntegerField(default=1, verbose_name='Quantidade Máxima de Abonadas Comuns por Mês')),
                ('min_dias_antes_abonada', models.PositiveSmallIntegerField(default=2, verbose_name='Antecedência Mínima para Solicitação de Abonada')),
                ('deferimento_presumido', models.BooleanField(default=True, verbose_name='Presumir Deferimento no Silêncio?')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
