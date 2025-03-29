from datetime import datetime as dt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.db.models.functions import ExtractYear
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView
from io import BytesIO
from weasyprint import HTML
from .forms import DespacharAbonada, FormRelatorioPeriodo, RequererAbonada
from .models import Configuracao, ReqAbonada, Setor

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

        usuario = request.user.funcionario
        req = ReqAbonada.objects.get(pk=self.kwargs['pk'])

        if ((usuario.cargo_comum is not None and req.requerente == usuario) or 
            (usuario.cargo_chefia is not None and req.requerente.lotacao.responsavel == usuario.cargo_chefia) or
            usuario.lotacao == Configuracao.objects.get(id=1).setor_gestao_pessoas):
            
            return super().dispatch(request, *args, **kwargs)            
        
        return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")        

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

        filtros = 0
        
        if numero and numero.isdigit():
            queryset = queryset.filter(num_registro=int(numero))
            filtros += 1
        if ano and ano.isdigit():
            queryset = queryset.filter(momento_inicio__year=int(ano))
            filtros += 1
        if requerente:
            queryset = queryset.filter(requerente__nome__icontains=requerente)
            filtros += 1
        if modalidade == 'A':
            queryset = queryset.filter(eh_aniversario=True)
            filtros += 1
        elif modalidade == 'C':
            queryset = queryset.filter(eh_aniversario=False)
            filtros += 1
        if data_inicio:
            queryset = queryset.filter(data_abonada__gte=data_inicio)
            filtros += 1
        if data_fim:
            queryset = queryset.filter(data_abonada__lte=data_fim)
            filtros += 1
        if situacao:
            queryset = queryset.filter(situacao=situacao)
            filtros += 1

        queryset = queryset.order_by('-momento_inicio') 

        if filtros == 0:
            queryset = queryset[:20]

        return queryset

    def get_context_data(self, **kwargs):
        # Adiciona os filtros ao contexto para manter os valores no template
        context = super().get_context_data(**kwargs)      

        context['filtros'] = self.request.GET
        
        return context

class ConsultaAbonadasAnual(LoginRequiredMixin, ListView):

    model = ReqAbonada
    template_name = 'abon_app/abonadas_anual.html'
    context_object_name = 'abon'

    def dispatch(self, request, *args, **kwargs):

        if  request.user.funcionario.cargo_comum is None:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")         
        
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        
        # Obtém os parâmetros de filtro da URL (GET)
        ano = self.request.GET.get('ano')

        # Aplica os filtros dinamicamente      
        if not ano or not ano.isdigit():
            ano = dt.now().year

        return ReqAbonada.objects.filter(requerente=self.request.user.funcionario, 
                                             data_abonada__year=int(ano)).order_by('data_abonada')

    def get_context_data(self, **kwargs):
        # Adiciona os filtros ao contexto para manter os valores no template
        context = super().get_context_data(**kwargs)      

        context['filtro'] = self.request.GET
        
        return context
    
class ConsultaAbonadasArquivamento(LoginRequiredMixin, ListView):
    
    model = ReqAbonada
    template_name = 'abon_app/abonadas_arquivamento.html'
    context_object_name = 'abon'

    def dispatch(self, request, *args, **kwargs):

        if  request.user.funcionario.lotacao != Configuracao.objects.get(id=1).setor_gestao_pessoas:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")            
        
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Obtém o queryset base
        queryset = ReqAbonada.objects.filter(((Q(situacao='T') & 
                                              Q(data_abonada__lt=dt.now().date())) | 
                                              Q(situacao='D')) &
                                              Q(arquivado=False))
        
        queryset = queryset.order_by('data_abonada') 
        
        return queryset
    
def arquivar_abonada(request, pk):
    
    if request.user.funcionario.lotacao != Configuracao.objects.get(id=1).setor_gestao_pessoas:
        return HttpResponseForbidden("Você não tem permissão para realizar esta operação."
                                    " Contate o administrador do sistema.")            
    
    req = ReqAbonada.objects.get(pk=pk)
    req.arquivado = True
    if req.situacao == 'T':
        req.situacao = 'D'
    req.save()
    
    return redirect('abonadas_arquivamento')

class ConsultaAbonadasCancelamento(LoginRequiredMixin, ListView):
    
    model = ReqAbonada
    template_name = 'abon_app/abonadas_cancelamento.html'
    context_object_name = 'abon'

    def dispatch(self, request, *args, **kwargs):

        if  request.user.funcionario.cargo_comum is None:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")           
        
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Obtém o queryset base
        queryset = ReqAbonada.objects.filter(Q(requerente=self.request.user.funcionario) &
                                            Q(data_abonada__gte=dt.now().date()) &
                                            (Q(situacao='D') | Q(situacao='T')))
        
        queryset = queryset.order_by('data_abonada') 
        
        return queryset

def cancelar_abonada(request, pk):

    req = ReqAbonada.objects.get(pk=pk)
    usuario = request.user.funcionario
    
    if(usuario.cargo_comum is None or req.requerente != usuario):
        return HttpResponseForbidden("Você não tem permissão para realizar esta operação."
                                    " Contate o administrador do sistema.")  

    req.momento_cancelamento = dt.now()
    req.situacao = 'C'
    req.save()
    
    return redirect('abonadas_cancelamento')
    
class ConsultaAbonadasDespacho(LoginRequiredMixin, ListView):

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

        setores_chefia = Setor.objects.filter(responsavel=self.request.user.funcionario.cargo_chefia)

        queryset = ReqAbonada.objects.filter(requerente__lotacao__in=setores_chefia,
                                            situacao='T',
                                            data_abonada__gt=dt.now().date())
        
        queryset = queryset.order_by('data_abonada') 
        
        return queryset

class DespacharAbonada(LoginRequiredMixin, FormView):

    form_class = DespacharAbonada
    template_name = 'abon_app/despacho_abonada.html'
    success_url = reverse_lazy('abonadas_despacho')

    def dispatch(self, request, *args, **kwargs):

        req = ReqAbonada.objects.get(pk=self.kwargs['pk'])
        chefe = request.user.funcionario

        if chefe.cargo_chefia == None or req.requerente.lotacao.responsavel != chefe.cargo_chefia:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")        
        
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        
        req_abonada = form.save(commit=False)
        chefe = self.request.user.funcionario
        erro = req_abonada.despacho_req(chefe)
        
        if erro == None:   
            req_abonada.save()
        else:
            form.add_error(None, erro)
            return super(DespacharAbonada, self).form_invalid(form)

        return super(DespacharAbonada, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # Adiciona o objeto ao contexto para exibir no template
        context = super().get_context_data(**kwargs)
        context['req'] = ReqAbonada.objects.get(pk=self.kwargs['pk'])
        
        return context

    def get_form_kwargs(self):
        # Adiciona o objeto ao form para ser validado
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = ReqAbonada.objects.get(pk=self.kwargs['pk'])
        
        return kwargs

class ConsultaAbonadasFuturas(LoginRequiredMixin, ListView):

    model = ReqAbonada
    template_name = 'abon_app/abonadas_futuras.html'
    context_object_name = 'abon'

    def dispatch(self, request, *args, **kwargs):

        if  request.user.funcionario.cargo_chefia == None:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")          
        
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Obtém o queryset base
        queryset = ReqAbonada.objects.filter(requerente__lotacao__responsavel=
                                             self.request.user.funcionario.cargo_chefia,
                                             data_abonada__gte=dt.now().date(),
                                             situacao__in=['T', 'D'])

        # Obtém os parâmetros de filtro da URL (GET)
        requerente = self.request.GET.get('requerente')
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')

        # Aplica os filtros dinamicamente

        filtros = 0
        
        if requerente:
            queryset = queryset.filter(requerente__nome__icontains=requerente)
            filtros += 1
        if data_inicio:
            queryset = queryset.filter(data_abonada__gte=data_inicio)
            filtros += 1
        if data_fim:
            queryset = queryset.filter(data_abonada__lte=data_fim)
            filtros += 1

        queryset = queryset.order_by('data_abonada') 

        if filtros == 0:
            return queryset[:20]

        return queryset

    def get_context_data(self, **kwargs):
        # Adiciona os filtros ao contexto para manter os valores no template
        context = super().get_context_data(**kwargs)      

        context['filtros'] = self.request.GET
        
        return context


def gerar_relatorio_pdf(request):

    # Verifica se o usuário tem permissão para acessar o relatório
    if request.user.funcionario.lotacao != Configuracao.objects.get(id=1).setor_gestao_pessoas:
        return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                     " Contate o administrador do sistema.")

    data_inicio_str = request.GET.get('data_inicio')
    data_fim_str = request.GET.get('data_fim')

    data_inicio = dt.strptime(data_inicio_str, '%Y-%m-%d') 
    data_fim = dt.strptime(data_fim_str, '%Y-%m-%d')

    if not data_inicio or not data_fim:
        return HttpResponseBadRequest("Parâmetros inválidos. "
        "Por favor, forneça uma data inicial e uma data final.")

    # Dados para o relatório
    dados = {
        'abonadas': ReqAbonada.objects.filter(data_abonada__gte=data_inicio, 
                                            data_abonada__lte=data_fim,
                                            situacao__in=['D','T'])
                                            .order_by('data_abonada', 
                                            'requerente__lotacao',
                                            'requerente__nome'),
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'setor_gestao_pessoas': Configuracao.objects.get(id=1).setor_gestao_pessoas
    }

    # Renderiza o template HTML
    template_path = 'abon_app/relatorio.html'
    html_string = render_to_string(template_path, dados)

    # Converte o HTML em PDF
    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(pdf_file)

    # Configura a resposta HTTP para PDF
    response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_abonadas.pdf"'

    return response

class FormRelatorioPeriodo(LoginRequiredMixin, FormView):

    form_class = FormRelatorioPeriodo
    template_name = 'abon_app/sol_rel_abon_periodo.html'
    success_url = reverse_lazy('relatorio_pdf')

    def dispatch(self, request, *args, **kwargs):

        if  request.user.funcionario.lotacao != Configuracao.objects.get(id=1).setor_gestao_pessoas:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")        
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Obtém os dados do formulário
        data_inicio = form.cleaned_data.get('data_inicial')
        data_fim = form.cleaned_data.get('data_final')

        # Constrói a URL com os parâmetros
        url = reverse('relatorio_pdf') + f'?data_inicio={data_inicio}&data_fim={data_fim}'

        # Redireciona para a URL
        return redirect(url)