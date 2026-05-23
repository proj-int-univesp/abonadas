from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from abon_app.models import (
    CargoChefia,
    CargoComum,
    Configuracao,
    Feriado,
    Funcionario,
    ReqAbonada,
    Setor,
    CalendarioFeriados,
)


def next_weekday(start_date):
    candidate = start_date + timedelta(days=1)
    while candidate.weekday() in [5, 6]:
        candidate += timedelta(days=1)
    return candidate


class FuncionarioModelTest(TestCase):
    def setUp(self):
        self.cargo_chefia = CargoChefia.objects.create(nome='Chefe', ativo=True)
        self.cargo_comum = CargoComum.objects.create(nome='Analista', ativo=True)
        self.setor = Setor.objects.create(
            nome='Recursos Humanos',
            sigla='RH',
            responsavel=self.cargo_chefia,
            ativo=True,
        )
        self.user = User.objects.create_user(username='usuario_teste', password='senha123')
        self.funcionario = Funcionario.objects.create(
            nome='Teste Funcionario',
            matricula='0001',
            data_nascimento=date(1990, 1, 1),
            cargo_comum=self.cargo_comum,
            lotacao=self.setor,
            credenciais=self.user,
        )
        Configuracao.objects.create(
            pk=1,
            max_abonadas_ano=10,
            max_abonadas_mes=1,
            min_dias_antes_abonada=1,
            setor_gestao_pessoas=self.setor,
        )

    def test_tem_cargo_comum_retorna_true(self):
        self.assertTrue(self.funcionario.tem_cargo_comum())

    def test_tem_cargo_chefia_retorna_false(self):
        self.assertFalse(self.funcionario.tem_cargo_chefia())

    def test_faz_gestao_pessoas_retorna_true_para_setor_de_gestao(self):
        self.assertTrue(self.funcionario.faz_gestao_pessoas())


class ReqAbonadaModelTest(TestCase):
    def setUp(self):
        self.cargo_chefia = CargoChefia.objects.create(nome='Chefe', ativo=True)
        self.cargo_comum = CargoComum.objects.create(nome='Analista', ativo=True)
        self.setor = Setor.objects.create(
            nome='Tecnologia da Informação',
            sigla='TI',
            responsavel=self.cargo_chefia,
            ativo=True,
        )
        self.user = User.objects.create_user(username='funcionario', password='senha123')
        self.funcionario = Funcionario.objects.create(
            nome='Funcionário TI',
            matricula='0010',
            data_nascimento=date(1990, 3, 10),
            cargo_comum=self.cargo_comum,
            lotacao=self.setor,
            credenciais=self.user,
        )
        Configuracao.objects.create(
            pk=1,
            max_abonadas_ano=10,
            max_abonadas_mes=1,
            min_dias_antes_abonada=1,
            setor_gestao_pessoas=self.setor,
        )
        self.exercicio = date.today().year
        self.calendario = CalendarioFeriados.objects.create(exercicio=self.exercicio, descricao='Calendário teste')
        self.feriado = Feriado.objects.create(
            nome='Feriado Teste',
            data=date(self.exercicio, 12, 25),
            calendario=self.calendario,
        )

    def test_inicio_req_retorna_erro_para_data_passada(self):
        req = ReqAbonada(data_abonada=date.today() - timedelta(days=1), eh_aniversario=False)
        erro = req.inicio_req(self.funcionario)
        self.assertIn('anterior à data atual', erro)

    def test_inicio_req_retorna_erro_para_feriado(self):
        req = ReqAbonada(data_abonada=self.feriado.data, eh_aniversario=False)
        erro = req.inicio_req(self.funcionario)
        self.assertIn('não pode ser em um feriado', erro)

    def test_inicio_req_com_data_valida_nao_retorna_erro(self):
        data_valida = next_weekday(date.today() + timedelta(days=2))
        req = ReqAbonada(data_abonada=data_valida, eh_aniversario=False)
        erro = req.inicio_req(self.funcionario)
        self.assertIsNone(erro)
        self.assertEqual(req.requerente, self.funcionario)

    def test_despacho_req_aprova_requisicao(self):
        req = ReqAbonada.objects.create(
            num_registro=1,
            requerente=self.funcionario,
            data_abonada=next_weekday(date.today() + timedelta(days=2)),
            eh_aniversario=False,
        )
        req.despacho = True
        chefia = Funcionario.objects.create(
            nome='Chefe TI',
            matricula='0020',
            data_nascimento=date(1980, 1, 1),
            cargo_chefia=self.cargo_chefia,
            lotacao=self.setor,
        )
        erro = req.despacho_req(chefia)
        self.assertIsNone(erro)
        self.assertEqual(req.situacao, 'D')
        self.assertEqual(req.chefe, chefia)
        self.assertEqual(req.cargo_chefe, self.cargo_chefia)

    def test_despacho_req_indeferimento_exige_justificativa(self):
        req = ReqAbonada.objects.create(
            num_registro=2,
            requerente=self.funcionario,
            data_abonada=next_weekday(date.today() + timedelta(days=2)),
            eh_aniversario=False,
        )
        req.despacho = False
        chefia = Funcionario.objects.create(
            nome='Chefe TI',
            matricula='0021',
            data_nascimento=date(1980, 1, 1),
            cargo_chefia=self.cargo_chefia,
            lotacao=self.setor,
        )
        erro = req.despacho_req(chefia)
        self.assertIn('justificativa é obrigatória', erro)
        req.justificativa = 'Motivo válido'
        erro = req.despacho_req(chefia)
        self.assertIsNone(erro)
        self.assertEqual(req.situacao, 'I')

    def test_nao_permite_duas_abonadas_mesmo_dia(self):
        data_abonada = next_weekday(date.today() + timedelta(days=2))
        
        # Primeiro funcionário cria requisição
        req1 = ReqAbonada.objects.create(
            num_registro=3,
            requerente=self.funcionario,
            data_abonada=data_abonada,
            eh_aniversario=False,
        )
        
        # Segundo funcionário tenta criar requisição para mesmo dia
        funcionario2 = Funcionario.objects.create(
            nome='Funcionário TI 2',
            matricula='0011',
            data_nascimento=date(1992, 7, 15),
            cargo_comum=self.cargo_comum,
            lotacao=self.setor,
        )
        
        req2 = ReqAbonada(
            data_abonada=data_abonada,
            eh_aniversario=False,
        )
        
        erro = req2.inicio_req(funcionario2)
        
        # Deve retornar erro indicando que já existe abonada para esse dia
        self.assertIsNotNone(erro)
        self.assertIn('abonada', erro.lower())
        self.assertIn('mesmo dia', erro.lower())


class ViewIntegrationTest(TestCase):
    def setUp(self):
        self.cargo_chefia = CargoChefia.objects.create(nome='Chefe', ativo=True)
        self.cargo_comum = CargoComum.objects.create(nome='Analista', ativo=True)
        self.setor_rh = Setor.objects.create(
            nome='Recursos Humanos',
            sigla='RH',
            responsavel=self.cargo_chefia,
            ativo=True,
        )
        Configuracao.objects.create(
            pk=1,
            max_abonadas_ano=10,
            max_abonadas_mes=1,
            min_dias_antes_abonada=1,
            setor_gestao_pessoas=self.setor_rh,
        )

        self.user_func = User.objects.create_user(username='funcionario', password='senha123')
        self.funcionario = Funcionario.objects.create(
            nome='Funcionario Teste',
            matricula='0010',
            data_nascimento=date(1990, 1, 1),
            cargo_comum=self.cargo_comum,
            lotacao=self.setor_rh,
            credenciais=self.user_func,
        )

        self.user_chefe = User.objects.create_user(username='chefe', password='senha123')
        self.chefe = Funcionario.objects.create(
            nome='Chefe Teste',
            matricula='0020',
            data_nascimento=date(1980, 1, 1),
            cargo_chefia=self.cargo_chefia,
            lotacao=self.setor_rh,
            credenciais=self.user_chefe,
        )

        self.client = Client()

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse('menu'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_funcionario_comum_acessa_abonadas_anual(self):
        self.client.login(username='funcionario', password='senha123')
        response = self.client.get(reverse('abonadas_anual'))
        self.assertEqual(response.status_code, 200)

    def test_funcionario_sem_chefia_nao_acessa_despacho(self):
        self.client.login(username='funcionario', password='senha123')
        response = self.client.get(reverse('abonadas_despacho'))
        self.assertEqual(response.status_code, 403)

    def test_chefe_acessa_despacho(self):
        self.client.login(username='chefe', password='senha123')
        response = self.client.get(reverse('abonadas_despacho'))
        self.assertEqual(response.status_code, 200)
