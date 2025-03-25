from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, TemplateView
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

class ConsultaGeralAbonadas(LoginRequiredMixin, TemplateView):

    template_name = 'abon_app/consulta_geral_abonadas.html'

    def dispatch(self, request, *args, **kwargs):

        if  request.user.funcionario.setor != Configuracao.get(id).setor_gestao_pessoas:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")        
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['abon'] = ReqAbonada.objects.all()
        return context