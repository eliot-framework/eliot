# -*- coding: UTF-8 -*-

from django.shortcuts import render
from django.template.loader import render_to_string

from adm.services import TelefoneUsuarioService, EnderecoUsuarioService, \
    UsuarioService
from fpc.forms import FpcForm
from fpc.models import Fpc
from fpc.views import fpc_request, FpcJsonMessage


def usuario_telefone(request):
    service = TelefoneUsuarioService()
    matricula = int(request.GET['id_obj'])
    lista_telefones = service.lista_telefone(matricula)
    return render_to_string("usuario_telefone.html", { "matricula" : matricula, 
                       
                                                       "lista_telefones" : lista_telefones })    
def usuario_endereco(request):
    service = EnderecoUsuarioService()
    matricula = int(request.GET['id_obj'])
    lista_enderecos = service.lista_endereco(matricula)
    return render_to_string("usuario_endereco.html", { "matricula" : matricula, 
                                                       "lista_enderecos" : lista_enderecos })    
    


def consulta_historico_acesso(request):
    service = UsuarioService()
    matricula = int(request.GET['id_obj'])
    lista_historico = service.lista_historico_acesso(matricula)
    return render_to_string("consulta_historico_acesso.html", { "matricula" : matricula, 
                                                                "lista_historico" : lista_historico })    

@fpc_request
def personalizar_framework(request):
    ts = request.ts
    form = FpcForm.get_form(request)
    template = form.createTemplate()
    return FpcJsonMessage("", "info", {"template" : template, 
                                       "ts" : ts.pk, 
                                       "tipoTs" : ts.tipoTransacao,
                                       "update_fields" : Fpc.getFpc().get_values(),
                                       "operacao" : "update"})


