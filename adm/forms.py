# -*- coding: utf-8 -*-

from adm.models import Sistema, Usuario, Departamento
from fpc.forms import FpcCrud, FpcForm, FpcField
import fpc.models


class SistemaForm(FpcCrud):
    class Meta:
        model = Sistema
        campos_pesquisa = ("cod_sistema", "nome", "sigla")
        campos_grid_pesquisa = ("cod_sistema", "nome", "sigla")
        layout = ("cod_sistema", "nome", "sigla")
        layout_pesquisa = ("cod_sistema", "nome", "sigla")
        titulo = "Sistema"
        


class DepartamentoForm(FpcCrud):
    class Meta:
        model = Departamento
        campos_pesquisa = ("cod_departamento", "denominacao")
        campos_grid_pesquisa = ("cod_departamento", "denominacao")
        layout = ("cod_departamento", "denominacao")
        layout_pesquisa = ("cod_departamento", "denominacao")
        titulo = "Departamento"

        

class UsuarioForm(FpcCrud):
    class Meta:
        model = Usuario
        campos_pesquisa = ("matricula", "nome")
        campos_grid_pesquisa = ("matricula", "nome", "login")
        layout = { "_config" : { "tipo" : "form-inline" },
                   "1:Dados do Usuário"  : ( "matricula",
                                             "nome", 
                                             "login", 
                                             "senha", 
                                             "departamento",
                                             "dt_cadastro",
                                             ["telefone", "celular"] ),
                    "2:Endereços do Usuário:no_insert" : "url:adm.views.usuario_endereco",
                    "3:Telefones do Usuário:no_insert" : "url:adm.views.usuario_telefone",
                    "4:Consulta Histórico de Acessos:no_insert" : "url:adm.views.consulta_historico_acesso"
                  }
        layout_pesquisa = ("matricula", "nome", "login")
        titulo = "Usuário"


class FpcConfigForm(FpcForm):
    class Meta:
        model = fpc.models.Fpc
        template = "fpc_config.html"
        layout = {  "_config" : { "tipo" : "form-horizontal",
                                  "label_grid" : "col-sm-2 col-md-2 col-xs-2 col-lg-2",
                                  "input_grid" : "col-sm-10 col-md-10 col-xs-10 col-lg-10",
                                  "css_form_group" : "background:#e7e7e7; padding:6px; margin-bottom:1px;"
                                },
                    "1:Configurações Gerais"  : ("nome", 
                                                "descricao", 
                                                "fale_conosco",
                                                ),
                    "2:Estilos css" : ( "fale_conosco", 
                                        "descricao", 
                                        "css_header_background_color"
                                      ),
                  }
        titulo = "Personalizar Framework"
    
