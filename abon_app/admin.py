from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import CalendarioFeriados, CargoChefia, CargoComum, Configuracao, Feriado, Funcionario, Setor
# Register your models here.

class FeriadoInline(admin.StackedInline):
  model = Feriado
  extra = 1
  verbose_name = "feriado"
  verbose_name_plural = "feriados"

class FuncionarioInline(admin.StackedInline):
  model=Funcionario
  can_delete = False
  verbose_name = "funcionário"
  verbose_name_plural = "funcionários"

class CalendarioFeriadosAdmin(admin.ModelAdmin):

  inlines = [FeriadoInline]
  list_display = ("exercicio",)

class ConfiguracaoAdmin(admin.ModelAdmin):

  def has_delete_permission(self, request, obj = None):
    return False

class FuncionarioAdmin(admin.ModelAdmin):
  
  list_display = ("nome", "lotacao", "cargo_comum", "cargo_chefia")

  exclude = ('credenciais',)  

class UserAdmin(BaseUserAdmin):
  inlines = [FuncionarioInline]

  list_display = ['get_nome_funcionario', 'get_lotacao_funcionario', 'username', 'is_active']

  @admin.display(description="Nome", ordering='funcionario__nome')
  def get_nome_funcionario(self, obj):
      return obj.funcionario.nome
  
  @admin.display(description="Lotação", ordering='funcionario__lotacao')
  def get_lotacao_funcionario(self, obj):
      return obj.funcionario.lotacao

  def get_fieldsets(self, request, obj=None):
    fieldsets = super().get_fieldsets(request, obj)
    new = []
    for name, fields_dict in fieldsets:
        if fields_dict['fields'] == ('first_name', 'last_name', 'email'):
            fields_dict['fields'] = ('email',)
        new.append((name, fields_dict))
    return new

admin.site.register(CalendarioFeriados, CalendarioFeriadosAdmin)
admin.site.register(CargoChefia)
admin.site.register(CargoComum)
admin.site.register(Configuracao, ConfiguracaoAdmin)
admin.site.register(Setor)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)