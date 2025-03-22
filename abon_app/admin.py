from django.contrib import admin

from .models import CargoChefia, CargoComum, Configuracao, Funcionario, Setor
# Register your models here.

class ConfiguracaoAdmin(admin.ModelAdmin):

  def has_delete_permission(self, request, obj = None):
    return False

class FuncionarioAdmin(admin.ModelAdmin):
  list_display = ("nome", "lotacao", "cargo_comum", "cargo_chefia")

admin.site.register(CargoChefia)
admin.site.register(CargoComum)
admin.site.register(Configuracao, ConfiguracaoAdmin)
admin.site.register(Funcionario, FuncionarioAdmin)
admin.site.register(Setor)