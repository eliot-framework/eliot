# -*- coding: utf-8 -*-

from estoque.models import Produto, GrupoProduto, SubgrupoProduto, ProdutoComposicao, \
    Pessoa
from fpc.forms import FpcCrud, FpcButton, FpcField, FpcGrid, FpcColumn


class ProdutoComposicaoForm(FpcCrud):
    class Meta:
        model = ProdutoComposicao
        campos_pesquisa = ("codigo", "nome")
        campos_grid_pesquisa = ("codigo", "nome")
        layout = ( "codigo", "nome", "produto", "unidade", "quantidade" )
        titulo = "Produto Composição"


class ProdutoForm(FpcCrud):
    class Meta:
        model = Produto
        campos_grid_pesquisa = ("codigo", "cod_barra", "nome")

        layout = {"_config" : { "tipo" : "form-inline",
                                "css_label" : "display:block"
                                },
                  "1:Principal"         : (
                                            (
                                                "codigo", 
                                                "codigoEstruturado",
                                                FpcButton(id="btnGerarCodigo",
                                                          label="Gerar Código"),
                                                FpcField(name="dataValidade",
                                                         css="font-weight: italic")
                                            ),
                                             FpcField(name = "cod_barra", 
                                                      label = "Código de Barra", 
                                                      size = 160,
                                                      mini_button=True,
                                                      css="font-style: italic;"),
                                            ("nome", 
                                             FpcField(name="sigla", 
                                                      label="Sigla do produto",
                                                      css_label="min-width:14px;display:inline-block;color:red",
                                                      css="color:blue")),
                                            "descricao", 
                                            "tipo:cboTipo",
                                            FpcField(name="tipo", mini_button=True, mini_button_icon="glyphicon-dashboard")
                                         ), 
                 "2:Formação Preço"    : ( "nome", 
                                           "precoCusto", 
                                            (
                                                "lucroBruto", 
                                                "lucroLiquido"
                                            ), 
                                           ("precoVenda", 
                                             FpcButton(id="btnSelecionarPessoa", label="Atualizar")
                                            ) 
                                           
                                           
                                         ) 
                                         ,
                 "3:Dados Adicionais"  : ( "grupo", 
                                            "subgrupo",
                                             FpcButton(id="btnUmBotaoEscondido", label="Testar2"),
                                             #FpcGrid(
                                             #    id="gridDados",  
                                             #    field="produtocomposicao_set",
                                             #    columns = (
                                             #                FpcColumn(field="codigo",
                                             #                          label="Cód",
                                             #                          style="text-aligment: center"),
                                             #                "cod_barra",
                                             #                "nome"
                                             #              )
                                             #)
                                         ),
                 "4:Composições do Produto:ajax"  : ( 
                                                         
                                                    ),
                 "5:Controle:no_insert":       "fpc_controle.html"
               }
        
        layout_pesquisa = ("codigo", "cod_barra", "nome")
        layout_consulta = ("codigo", "cod_barra", "codigoEstruturado", "nome")

        layout_dados_pesquisa = (
                                     FpcGrid(  
                                         field="produtocomposicao_set",
                                         columns = (
                                                     FpcColumn(field="codigo",
                                                               label="Cód",
                                                               style="text-aligment: center"),
                                                     "cod_barra",
                                                     "nome"
                                                   )
                                     )
                                )
        
        
        titulo = "Produto"
        
        

class GrupoProdutoForm(FpcCrud):
    class Meta:
        model = GrupoProduto
        campos_pesquisa = ("codigo", "nome")
        campos_grid_pesquisa = ("codigo", "nome")
        layout = ( "codigo", "nome" )
        layout_pesquisa = ("codigo", "nome")
        titulo = "Grupo de Produto"


class SubgrupoProdutoForm(FpcCrud):
    class Meta:
        model = SubgrupoProduto
        campos_pesquisa = ("codigo", "nome")
        campos_grid_pesquisa = ("codigo", "nome")
        layout = { "1:Principal" : ( "codigo", "nome" ) }
        layout_pesquisa = ("codigo", "nome")
        titulo = "Subgrupo"
        

class PessoaForm(FpcCrud):
    class Meta:
        model = Pessoa
        campos_pesquisa = ("codigo", "nome")
        campos_grid_pesquisa = ("codigo", "nome")
        layout = ("codigo", "nome", "CpfCnpj")
        layout_pesquisa = ("codigo", "nome", "CpfCnpj")
        titulo = "Pessoa"
        

