from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from abon_app.models import (
    CargoComum, CargoChefia, Setor, Configuracao, 
    CalendarioFeriados, Feriado, Funcionario
)
from datetime import date


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de teste para explorar todas as funcionalidades'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('⚠️  Iniciando população de dados de teste...'))
        
        # Limpar dados antigos (opcional)
        # User.objects.filter(username__startswith='teste_').delete()

        # 1. CRIAR CARGOS DE CHEFIA
        self.stdout.write('1️⃣  Criando Cargos de Chefia...')
        cargo_gerente, _ = CargoChefia.objects.get_or_create(
            nome="Gerente",
            defaults={'detalhes': 'Responsável pela gestão da área', 'ativo': True}
        )
        cargo_coordenador, _ = CargoChefia.objects.get_or_create(
            nome="Coordenador",
            defaults={
                'subordinacao': cargo_gerente,
                'detalhes': 'Coordena atividades sob supervisão do Gerente',
                'ativo': True
            }
        )
        self.stdout.write(self.style.SUCCESS('   ✅ Cargos de Chefia criados'))

        # 2. CRIAR CARGOS COMUNS
        self.stdout.write('2️⃣  Criando Cargos Comuns...')
        cargo_analista, _ = CargoComum.objects.get_or_create(
            nome="Analista",
            defaults={'detalhes': 'Analista de sistemas', 'ativo': True}
        )
        cargo_auxiliar, _ = CargoComum.objects.get_or_create(
            nome="Auxiliar Administrativo",
            defaults={'ativo': True}
        )
        self.stdout.write(self.style.SUCCESS('   ✅ Cargos Comuns criados'))

        # 3. CRIAR SETORES
        self.stdout.write('3️⃣  Criando Setores...')
        setor_rh, _ = Setor.objects.get_or_create(
            nome="Recursos Humanos",
            defaults={
                'sigla': 'RH',
                'responsavel': cargo_gerente,
                'ativo': True
            }
        )
        setor_ti, _ = Setor.objects.get_or_create(
            nome="Tecnologia da Informação",
            defaults={
                'sigla': 'TI',
                'responsavel': cargo_coordenador,
                'ativo': True
            }
        )
        setor_financeiro, _ = Setor.objects.get_or_create(
            nome="Financeiro",
            defaults={
                'sigla': 'FIN',
                'responsavel': cargo_gerente,
                'ativo': True
            }
        )
        self.stdout.write(self.style.SUCCESS('   ✅ Setores criados'))

        # 4. CRIAR CONFIGURAÇÃO GLOBAL
        self.stdout.write('4️⃣  Configurando aplicação...')
        config, _ = Configuracao.objects.get_or_create(
            pk=1,
            defaults={
                'max_abonadas_ano': 10,
                'max_abonadas_mes': 1,
                'min_dias_antes_abonada': 2,
                'setor_gestao_pessoas': setor_rh
            }
        )
        if config.setor_gestao_pessoas != setor_rh:
            config.setor_gestao_pessoas = setor_rh
            config.save()
        self.stdout.write(self.style.SUCCESS('   ✅ Configuração global criada'))

        # 5. CRIAR CALENDÁRIO DE FERIADOS 2025
        self.stdout.write('5️⃣  Criando Calendário de Feriados 2025...')
        calendario_2025, _ = CalendarioFeriados.objects.get_or_create(
            exercicio=2025,
            defaults={'descricao': 'Calendário de feriados 2025'}
        )
        
        feriados_2025 = [
            ("Ano Novo", date(2025, 1, 1)),
            ("Tiradentes", date(2025, 4, 21)),
            ("Dia do Trabalho", date(2025, 5, 1)),
            ("Corpus Christi", date(2025, 6, 19)),
            ("Independência do Brasil", date(2025, 9, 7)),
            ("Nossa Senhora Aparecida", date(2025, 10, 12)),
            ("Finados", date(2025, 11, 2)),
            ("Proclamação da República", date(2025, 11, 15)),
            ("Consciência Negra", date(2025, 11, 20)),
            ("Natal", date(2025, 12, 25)),
        ]
        
        for nome, data_feriado in feriados_2025:
            Feriado.objects.get_or_create(
                nome=nome,
                data=data_feriado,
                calendario=calendario_2025
            )
        self.stdout.write(self.style.SUCCESS(f'   ✅ {len(feriados_2025)} feriados criados'))

        # 6. CRIAR USUÁRIOS E FUNCIONÁRIOS
        self.stdout.write('6️⃣  Criando Usuários e Funcionários...')
        
        usuarios_dados = [
            {
                'username': 'chefe_rh',
                'email': 'chefe@rh.com',
                'password': 'senha123',
                'funcionario': {
                    'nome': 'João Silva Santos',
                    'matricula': '0001',
                    'data_nascimento': date(1980, 5, 15),
                    'cargo_chefia': cargo_gerente,
                    'lotacao': setor_rh
                }
            },
            {
                'username': 'chefe_ti',
                'email': 'chefe@ti.com',
                'password': 'senha123',
                'funcionario': {
                    'nome': 'Maria Santos Costa',
                    'matricula': '0002',
                    'data_nascimento': date(1985, 8, 20),
                    'cargo_chefia': cargo_coordenador,
                    'lotacao': setor_ti
                }
            },
            {
                'username': 'chefe_financeiro',
                'email': 'chefe@fin.com',
                'password': 'senha123',
                'funcionario': {
                    'nome': 'Carlos Alberto Oliveira',
                    'matricula': '0003',
                    'data_nascimento': date(1978, 3, 10),
                    'cargo_chefia': cargo_gerente,
                    'lotacao': setor_financeiro
                }
            },
            {
                'username': 'func_ti1',
                'email': 'func1@ti.com',
                'password': 'senha123',
                'funcionario': {
                    'nome': 'Pedro Costa Ferreira',
                    'matricula': '0010',
                    'data_nascimento': date(1990, 3, 10),
                    'cargo_comum': cargo_analista,
                    'lotacao': setor_ti
                }
            },
            {
                'username': 'func_ti2',
                'email': 'func2@ti.com',
                'password': 'senha123',
                'funcionario': {
                    'nome': 'Ana Paula Rodrigues',
                    'matricula': '0011',
                    'data_nascimento': date(1995, 7, 22),
                    'cargo_comum': cargo_analista,
                    'lotacao': setor_ti
                }
            },
            {
                'username': 'func_rh1',
                'email': 'func1@rh.com',
                'password': 'senha123',
                'funcionario': {
                    'nome': 'Fernanda Marques Silva',
                    'matricula': '0020',
                    'data_nascimento': date(1992, 6, 25),
                    'cargo_comum': cargo_auxiliar,
                    'lotacao': setor_rh
                }
            },
            {
                'username': 'func_fin1',
                'email': 'func1@fin.com',
                'password': 'senha123',
                'funcionario': {
                    'nome': 'Rafael Gomes Alves',
                    'matricula': '0030',
                    'data_nascimento': date(1988, 11, 14),
                    'cargo_comum': cargo_analista,
                    'lotacao': setor_financeiro
                }
            },
        ]

        for user_data in usuarios_dados:
            username = user_data['username']
            
            # Criar ou atualizar User
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.email = user_data['email']
                user.set_password(user_data['password'])
                user.save()
            
            # Criar ou atualizar Funcionario
            func_data = user_data['funcionario']
            funcionario, _ = Funcionario.objects.get_or_create(
                matricula=func_data['matricula'],
                defaults={
                    'nome': func_data['nome'],
                    'data_nascimento': func_data['data_nascimento'],
                    'cargo_comum': func_data.get('cargo_comum'),
                    'cargo_chefia': func_data.get('cargo_chefia'),
                    'lotacao': func_data['lotacao'],
                    'credenciais': user
                }
            )
            
            # Garantir que credenciais estão ligadas
            if funcionario.credenciais != user:
                funcionario.credenciais = user
                funcionario.save()
            
            status = '✅ Criado' if created else '↩️  Existente'
            self.stdout.write(f'   {status}: {username} → {func_data["nome"]}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('🎉 Dados de teste populados com sucesso!'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('📝 Credenciais de acesso:'))
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('CHEFES (podem despachar requisições):'))
        self.stdout.write('   • chefe_rh / senha123 (Gerente - RH)')
        self.stdout.write('   • chefe_ti / senha123 (Coordenador - TI)')
        self.stdout.write('   • chefe_financeiro / senha123 (Gerente - Financeiro)')
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('FUNCIONÁRIOS (podem fazer requisições):'))
        self.stdout.write('   • func_ti1 / senha123 (Pedro Costa - TI)')
        self.stdout.write('   • func_ti2 / senha123 (Ana Paula - TI)')
        self.stdout.write('   • func_rh1 / senha123 (Fernanda Marques - RH)')
        self.stdout.write('   • func_fin1 / senha123 (Rafael Gomes - Financeiro)')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('🌐 Acesse o admin em: http://localhost:8000/admin/'))
        self.stdout.write(self.style.WARNING('   Usuário: admin, Senha: (do seu superuser)'))
        self.stdout.write('')
