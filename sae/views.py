# -*- coding: UTF-8 -*-

from django.shortcuts import render
from fpc.forms import FpcForm
from fpc.views import fpc_request

@fpc_request    
def estudo_socioeconomico(request):    
    ts = request.ts
    form = FpcForm.get_form(request)
    obj = form.model()
    template = form.createTemplate(FpcOperacaoForm.novo)
    response = FpcJsonMessage("", "info", {"template" : template, 
                                           "update_values" : obj.get_values(), 
                                           "ts" : ts.pk })
    return response





        

