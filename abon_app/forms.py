from django.forms import ModelForm
from .models import ReqAbonada

class RequererAbonada (ModelForm):

    class Meta:
        model = ReqAbonada
        fields = ['data_abonada', 'eh_aniversario']