from django.db import models
from django.core.cache import cache

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

class Funcionario(models.Model):
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=10, unique=True, verbose_name="matrícula")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    email = models.EmailField(max_length=254, blank=True, null=True, verbose_name="e-mail")
    cargo_comum = models.ForeignKey(CargoComum, on_delete=models.PROTECT, verbose_name="Cargo Comum",
                                    blank=True, null=True)
    cargo_chefia = models.ForeignKey(CargoChefia, on_delete=models.PROTECT, verbose_name="Cargo de Chefia",
                                    blank=True, null=True)
    lotacao = models.ForeignKey(Setor, on_delete=models.PROTECT, verbose_name="Lotação")
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome + " (" + self.matricula + ")"

    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"

class Configuracao(SingletonModel):
    max_abonadas_ano = models.PositiveSmallIntegerField(default=10, verbose_name="Quantidade Máxima de Abonadas Comuns por Ano")
    max_abonadas_mes = models.PositiveSmallIntegerField(default=1, verbose_name="Quantidade Máxima de Abonadas Comuns por Mês")
    min_dias_antes_abonada = models.PositiveSmallIntegerField(default=2, verbose_name="Antecedência Mínima para Solicitação de Abonada")
    setor_gestao_pessoas = models.ForeignKey(Setor, on_delete=models.PROTECT, blank=True, null=True,
                                             verbose_name="Setor com Atribuição de Gestão de Pessoas")

    def __str__(self):
        return "Configurações Globais"

    class Meta:
        verbose_name = "Configuração"
        verbose_name_plural = "Configurações"