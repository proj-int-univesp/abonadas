from datetime import datetime as dt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import ExtractYear
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView
from .forms import RequererAbonada
from .models import Configuracao, ReqAbonada

# Create your views here.

class MenuView(LoginRequiredMixin, TemplateView):
    template_name = 'abon_app/menu.html'

class RequererAbonada(LoginRequiredMixin, FormView):

    form_class = RequererAbonada
    template_name = 'abon_app/req_abonada.html'

    def dispatch(self, request, *args, **kwargs):

        if  request.user.funcionario.cargo_comum is None:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")        
        
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        
        req_abonada = form.save(commit=False)
        funcionario = self.request.user.funcionario
        print(funcionario)
        erro = req_abonada.inicio_req(funcionario)

        if erro == None:
            req_abonada.save()
            return redirect('detalhes_abonada', pk=req_abonada.pk)
        else:
            form.add_error(None, erro)
            return super(RequererAbonada, self).form_invalid(form)

class DetalhesAbonada(LoginRequiredMixin, DetailView):

    model = ReqAbonada
    template_name = 'abon_app/detalhes_abonada.html'
    context_object_name = 'req'

    def dispatch(self, request, *args, **kwargs):

        if  request.user.funcionario.cargo_comum is None:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")        
        
        return super().dispatch(request, *args, **kwargs)

class ConsultaGeralAbonadas(LoginRequiredMixin, ListView):

    model = ReqAbonada
    template_name = 'abon_app/abonadas_geral.html'
    context_object_name = 'abon'

    def dispatch(self, request, *args, **kwargs):

        if  request.user.funcionario.lotacao != Configuracao.objects.get(id=1).setor_gestao_pessoas:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")        
        
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Obtém o queryset base
        queryset = ReqAbonada.objects.all()

        # Obtém os parâmetros de filtro da URL (GET)
        numero = self.request.GET.get('numero')
        ano = self.request.GET.get('ano')
        requerente = self.request.GET.get('requerente')
        modalidade = self.request.GET.get('modalidade')
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        situacao = self.request.GET.get('situacao')

        # Aplica os filtros dinamicamente
        
        if numero and numero.isdigit():
            queryset = queryset.filter(num_registro=int(numero))
        if ano and ano.isdigit():
            queryset = queryset.filter(momento_inicio__year=int(ano))
        if requerente:
            queryset = queryset.filter(requerente__nome__icontains=requerente)
        if modalidade == 'A':
            queryset = queryset.filter(eh_aniversario=True)
        elif modalidade == 'C':
            queryset = queryset.filter(eh_aniversario=False)
        if data_inicio:
            queryset = queryset.filter(data_abonada__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data_abonada__lte=data_fim)
        if situacao:
            queryset = queryset.filter(situacao=situacao)

        queryset = queryset.order_by('-momento_inicio') 

        return queryset

    def get_context_data(self, **kwargs):
        # Adiciona os filtros ao contexto para manter os valores no template
        context = super().get_context_data(**kwargs)      

        context['filtros'] = self.request.GET
        
        return context
    
class ConsultaAbonadasParaDespacho(LoginRequiredMixin, ListView):

    model = ReqAbonada
    template_name = 'abon_app/abonadas_despacho.html'
    context_object_name = 'abon'

    def dispatch(self, request, *args, **kwargs):

        if  request.user.funcionario.cargo_chefia == None:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")        
        
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Obtém o queryset base
        queryset = ReqAbonada.objects.filter(requerente__setor__in=self.request.user.funcionario.cargo_chefia.setor_set.all(),
                                            situacao='T',
                                            data_abonada__gt=dt.now().date())
        
        return queryset