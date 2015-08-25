# -*- coding: UTF-8 -*-

from django.shortcuts import render
from fpc.forms import FpcForm
from fpc.views import fpc_request


@fpc_request    
def estoque_exibe_controle_tche(request):    
    ts = request.ts
    formModel = FpcForm.get_form(request)
    vId = request.GET["id_obj"]
    obj = formModel.model.objects.get(pk=vId)
    formModel.setObject(obj)
    template = "fpc_controle.html"
    return render(request, template,  {'form' : formModel, "ts" : ts.id})


        

