from datetime import datetime as dt, timedelta
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models, transaction

# Create your models here.

class SingletonModel(models.Model):

    class Meta:
        abstract = True

    def set_cache(self):
        cache.get(self.__class__.__name__, self)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)
        self.set_cache()
    
    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                obj.set_cache()
        return cache.get(cls.__name__)


class CargoComum(models.Model):
    
    nome = models.CharField(max_length=50)
    detalhes = models.CharField(max_length=250, blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Cargo Comum"
        verbose_name_plural = "Cargos Comuns"

class CargoChefia(models.Model):
    
    nome = models.CharField(max_length=50)
    detalhes = models.CharField(max_length=250, blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Cargo de Chefia"
        verbose_name_plural = "Cargos de Chefia"

class Configuracao(SingletonModel):
    
    max_abonadas_ano = models.PositiveSmallIntegerField(default=10, verbose_name="Quantidade Máxima de Abonadas Comuns por Ano")
    max_abonadas_mes = models.PositiveSmallIntegerField(default=1, verbose_name="Quantidade Máxima de Abonadas Comuns por Mês")
    min_dias_antes_abonada = models.PositiveSmallIntegerField(default=2, verbose_name="Antecedência Mínima para Solicitação de Abonada")
    setor_gestao_pessoas = models.ForeignKey('Setor', on_delete=models.PROTECT, blank=True, null=True,
                                             verbose_name="Setor com Atribuição de Gestão de Pessoas")

    def __str__(self):
        return "Configurações Globais"

    class Meta:
        verbose_name = "Configuração"
        verbose_name_plural = "Configurações"

class Funcionario(models.Model):
    
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=10, unique=True, verbose_name="matrícula")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    cargo_comum = models.ForeignKey('CargoComum', on_delete=models.PROTECT, verbose_name="Cargo Comum",
                                    blank=True, null=True)
    cargo_chefia = models.ForeignKey('CargoChefia', on_delete=models.PROTECT, verbose_name="Cargo de Chefia",
                                    blank=True, null=True)
    lotacao = models.ForeignKey('Setor', on_delete=models.PROTECT, verbose_name="Lotação")
    credenciais = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null= True,
                                       verbose_name="Credenciais de Acesso")
    
    def tem_cargo_comum(self):
        
        if self.cargo_comum == None:
            return False
        
        return True
    
    def tem_cargo_chefia(self):
        
        if self.cargo_chefia == None:
            return False
        
        return True
    
    def faz_gestao_pessoas(self):

        if self.lotacao != Configuracao.objects.get(id=1).setor_gestao_pessoas:
            return False
        
        return True
        

    def __str__(self):
        return self.nome + " (" + self.matricula + ")"

    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"

class Numerador(models.Model):
    
    exercicio_num = models.PositiveSmallIntegerField("exercício")
    ultimo_num = models.PositiveBigIntegerField("último número", default=0)

    @classmethod
    def numerar(cls):
        
        with transaction.atomic():

            exercicio = dt.now().year
            
            try:
                numeracao_exerc = cls.objects.select_for_update().get(exercicio_num = exercicio)
            except cls.DoesNotExist:          
                numeracao_exerc = Numerador(exercicio_num=exercicio)
            
            numeracao_exerc.ultimo_num += 1
            numeracao_exerc.save()
            return numeracao_exerc.ultimo_num

class ReqAbonada(models.Model):

    SITUACOES = {
        "T": "Tramitando",
        "D": "Deferido",
        "I": "Indeferido",
        "C": "Cancelado"
    }

    num_registro = models.PositiveIntegerField(unique_for_year=True, 
                                               verbose_name="Número de Registro")
    momento_inicio = models.DateTimeField(auto_now_add=True, verbose_name="Data do Pedido")
    requerente = models.ForeignKey('Funcionario', related_name='func_requerente',
                                   on_delete=models.PROTECT, verbose_name="Requerente")
    data_abonada = models.DateField(verbose_name="Dia da Abonada")
    eh_aniversario = models.BooleanField(default=False, verbose_name="Abonada Aniversário?")

    situacao = models.CharField(max_length=1, choices=SITUACOES,
                                default='T', verbose_name="Situação")

    momento_despacho = models.DateTimeField(blank=True, null=True, verbose_name="Data do Despacho")
    chefe = models.ForeignKey('Funcionario', related_name='func_chefe', blank=True, null=True,
                                   on_delete=models.PROTECT, verbose_name="Chefia")
    cargo_chefe = models.ForeignKey('CargoChefia', on_delete=models.PROTECT,
                                   blank=True, null=True, verbose_name="Cargo")
    despacho = models.BooleanField(default=True, verbose_name="Deferido?")
    justificativa = models.CharField(max_length=200, blank=True, null=True,
                                     verbose_name="Justificativa")
    
    momento_cancelamento = models.DateTimeField(blank=True, null=True,
                                                verbose_name="Data do Cancelamento")
    
    arquivado = models.BooleanField(default=False, verbose_name="Arquivado?")

    def inicio_req(self, funcionario):
        
        if self.data_abonada < dt.now().date():
            return "A data da abonada não pode ser anterior à data atual!"
        
        if self.data_abonada < dt.now().date() + timedelta(days=Configuracao.objects.get(id=1).min_dias_antes_abonada):
            return "A antecedência mínima para solicitação de abonada é de " + str(Configuracao.objects.get(id=1).min_dias_antes_abonada) + " dias!"
        
        abonadas_mes = ReqAbonada.objects.filter(requerente=funcionario, 
                                                data_abonada__month=self.data_abonada.month,
                                                data_abonada__year=self.data_abonada.year,
                                                situacao__in=['T', 'D'], 
                                                eh_aniversario=self.eh_aniversario).count()
        
        if self.eh_aniversario:
            
            if self.data_abonada.month != funcionario.data_nascimento.month:
                return "A abonada de aniversário só pode ser requerida para o mês de aniversário do funcionário!"
            
            if abonadas_mes >= 1:
                return "Sua abonada de aniversário já foi requerida!"

        else:

            if abonadas_mes >= Configuracao.objects.get(id=1).max_abonadas_mes:
                return "O limite de abonadas comuns por mês foi atingido!"
            
            abonadas_ano = ReqAbonada.objects.filter(requerente=funcionario, 
                                                    data_abonada__year=self.data_abonada.year,
                                                    situacao__in=['T', 'D']).count()
            
            if abonadas_ano >= Configuracao.objects.get(id=1).max_abonadas_ano:
                return "O limite de abonadas comuns por ano foi atingido!"
        
        self.requerente = funcionario
        
        return None

    def save(self, *args, **kwargs):
        
        if self.num_registro is None:                        
            self.num_registro = Numerador.numerar()

        super(ReqAbonada, self).save(*args, **kwargs)

class Setor(models.Model):
    
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=10)
    responsavel = models.ForeignKey(CargoChefia, on_delete=models.PROTECT, verbose_name="responsável")
    detalhes = models.CharField(max_length=250, blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Setores"