from django import forms
from .models import ReqAbonada

class RequererAbonada(forms.ModelForm):

    class Meta:
        model = ReqAbonada
        fields = ['data_abonada', 'eh_aniversario']

class DespacharAbonada(forms.ModelForm):

    class Meta:
        model = ReqAbonada
        fields = ['despacho', 'justificativa']

class FormRelatorioPeriodo(forms.Form):
    data_inicial = forms.DateField(
        label='Data Inicial',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    data_final = forms.DateField(
        label='Data Final',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    def clean(self):
        cleaned_data = super().clean()
        data_inicial = cleaned_data.get("data_inicial")
        data_final = cleaned_data.get("data_final")

        if data_inicial and data_final and data_inicial > data_final:
            raise forms.ValidationError("A data inicial deve ser anterior à data final.")
        return cleaned_data