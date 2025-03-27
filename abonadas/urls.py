"""
URL configuration for abonadas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from abon_app import views

urlpatterns = [
    path('', views.MenuView.as_view(), name='menu'),
    path('abonada/arquivar/<int:pk>/', views.arquivar_abonada, name='arquivar_abonada'),
    path('abonada/cancelar/<int:pk>/', views.cancelar_abonada, name='cancelar_abonada'),
    path('abonada/despachar/<int:pk>/', views.DespacharAbonada.as_view(), name='despachar_abonada'),
    path('abonada/requerer/', views.RequererAbonada.as_view(), name='req_abonada'),
    path('abonada/<int:pk>/', views.DetalhesAbonada.as_view(), name='detalhes_abonada'),
    path('abonadas/arquivamento/', views.ConsultaAbonadasArquivamento.as_view(), name='abonadas_arquivamento'),
    path('abonadas/cancelamento/', views.ConsultaAbonadasCancelamento.as_view(), name='abonadas_cancelamento'),
    path('abonadas/consulta-geral/', views.ConsultaGeralAbonadas.as_view(), name='abonadas_geral'),
    path('abonadas/despachar/', views.ConsultaAbonadasDespacho.as_view(), name='abonadas_despacho'),
    path("accounts/", include("django.contrib.auth.urls")),
    path('admin/', admin.site.urls),
]

admin.site.site_header = "Gerenciamento Abon-App"
admin.site.site_title = "Abon-App Admin"
admin.site.index_title = "Sistema de Controle de Faltas Abonadas"