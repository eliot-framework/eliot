# -*- coding: UTF-8 -*-


from datetime import datetime
from decimal import Decimal
import decimal
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.backends.dummy.base import DatabaseError
from django.db.models.aggregates import Max
from django.db.models.fields import FieldDoesNotExist
from django.db.models.query_utils import Q
from functools import reduce
import json
import operator

from fpc.utils import EmsRest, json_encode_java

class TransacaoDao(models.Manager):

    def get_or_new(self, nome):
        try:
            ts = Transacao.objects.get(nome = nome)
        except:
            ts = Transacao()
        return ts  



class Transacao(models.Model):
    """
        Classe para gerenciar menus e todas as funcionalidades da aplicação.
        Tudo é representado através de uma transação.
    """
    class Admin:
        pass

    objects = TransacaoDao()

    def __str__(self):
        return self.titulo

    TIPO_TRANSACAO = (
         ("S", "Sistema"),
         ("F", "Fluxo"),
         ("T", "Transação"),
         ("L", "Linha separadora")
     )

    nome = models.CharField(max_length=30, unique=True, blank=False, null=False)
    titulo = models.CharField(max_length=60, blank=False, null=False)
    transacaoPai = models.ForeignKey("Transacao", blank=True, null=True)
    tipoTransacao = models.CharField(max_length=1, null=False, choices=TIPO_TRANSACAO)
    posicao = models.IntegerField(null=False)
    image_url = models.CharField(max_length=250, null=True, blank=True)
    transacao_url = models.CharField(max_length=250, null=True, blank=True)
    classePermissao = models.ForeignKey(ContentType, null=True, blank=True)
    formModel = models.CharField(max_length=100, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    service_api = models.CharField(max_length=60, null=True, blank=True)
    
    # Private vars
    _filhos = None 


    
    """
        Obtem uma lista de todos os filhos da transação (transação tipo fluxo)
    """
    def getFilhos(self):
        if self._filhos == None:
            user = Fpc.getFpc().user
            menuFilhos = Transacao.objects.filter(transacaoPai__id=self.pk).order_by('posicao')
            menuFilhosPermissao = []
            
            # Deve retornar apenas transações que o usuário tem permissão
            for menu in (menu for menu in menuFilhos):
                if menu.tipoTransacao == "T":
                    # Se a transacao tem uma classe de permissão definida
                    # então verifica a permissão do usuário na classe para as operações add, change, e view
                    if menu.classePermissao != None:
                        permissao_add = menu.classePermissao.app_label + '.add_' + menu.classePermissao.model
                        permissao_change = menu.classePermissao.app_label + '.change_' + menu.classePermissao.model
                        permissao_view = menu.classePermissao.app_label + '.view_' + menu.classePermissao.model
                        if user.has_perm(permissao_add) or user.has_perm(permissao_change) or user.has_perm(permissao_view):
                            menuFilhosPermissao.append(menu)
                    else:
                        # se não tem classe de permissão a transação sempre vai estar disponível
                        menuFilhosPermissao.append(menu)
                else:
                    menuFilhosPermissao.append(menu)
                    
            self._filhos = menuFilhosPermissao
        
        return self._filhos
        
    
    def temTransacao(self):
        if self.tipoTransacao == "F":
            for t in self.getFilhos():
                if t.tipoTransacao == "T":
                    return True
                else:
                    bValue = t.temTransacao()
                    if bValue:
                        return True 
                    
        else:
            return False
             
    

    """
        Obtém uma lista de todos os menus principais por sistema que o usuário tem eliot
    """
    @classmethod
    def getMenuPrincipaisPorSistema(self, sistema):
        menus_tmp = list(Transacao.objects.filter(transacaoPai__id=sistema.id).order_by('posicao'))
        retorno = []
        for menu in menus_tmp:
            if menu.tipoTransacao == 'T':
                retorno.append(menu)
            else:
                if any(filter(lambda m : m.tipoTransacao == "T" or (m.tipoTransacao == "F" and m.temTransacao()), menu.getFilhos())):
                    retorno.append(menu)
        return retorno

    
    
    """
        Obtém uma lista dos sistemas disponíveis
    """
    @classmethod
    def getListaSistemas(self):
        return list(Transacao.objects.filter(tipoTransacao="S"))
    
    
    def clean(self):
        pass
    
    
    def getPermFlags(self, user):
        perm = ""
        classe = self.classePermissao 
        if classe is None:
            perm = '1111'
        else:
            permissao_change = classe.app_label + '.change_' + classe.model
            if (user.has_perm(permissao_change)):
                perm = "1"
            else:
                perm += "0"
                
            permissao_add = classe.app_label + '.add_' + classe.model
            if (user.has_perm(permissao_add)):
                perm += "1"
            else:
                perm += "0"
             
            permissao_delete = classe.app_label + '.delete_' + classe.model
            if (user.has_perm(permissao_delete)):
                perm += "1"
            else:
                perm += "0"
            
            permissao_view = classe.app_label + '.view_' + classe.model
            if (user.has_perm(permissao_view)):
                perm += "1"
            else:
                perm += "0"

        return perm

    
    """
        Obtém uma instância da transação pelo model
    """
    @classmethod
    def getTsByModel(self, model_str):
        return Transacao.objects.get(model=model_str)

    @classmethod
    def getIdByModel(self, model_str):
        return Transacao.objects.values_list('pk', flat=True).get(model=model_str)
    
    def get_breadcrumb(self):
        if not hasattr(self, "_breadcrumb"):
            breadcrumbs = []
            breadcrumbs.append(self)
            pai = self.transacaoPai
            while pai != None:
                breadcrumbs.append(pai)
                pai = pai.transacaoPai
            self._breadcrumb = breadcrumbs
        return self._breadcrumb

    
    @classmethod
    def cadastra_ts_fixa(cls):
        
        # Autenticar
        ts = Transacao()
        ts.nome = 'Autenticar'
        ts.titulo = 'Autenticar'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_autenticar'
        ts.posicao = 1
        ts.formModel = 'fpc.forms.AutenticarForm'
        ts.model = 'fpc.models.User'
        try:
            ts.save()
        except:
            pass
        
        
        # Sobre
        ts = Transacao()
        ts.nome = 'Sobre'
        ts.titulo = 'Sobre'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_sobre'
        ts.posicao = 1
        ts.formModel = 'fpc.forms.SobreForm'
        ts.model = 'fpc.models.User'
        try:
            ts.save()
        except:
            pass;
        
        
        ###################################### Módulo de administração ######################################

        # Módulo de administração
        ts_adm = Transacao.objects.get_or_new(nome='ts_adm')
        ts_adm.nome = 'ts_adm'
        ts_adm.titulo = 'Módulo de Administração'
        ts_adm.tipoTransacao = 'S'
        ts_adm.posicao = 1
        ts_adm.image_url = 'class glyphicon glyphicon-book'
        ts_adm.formModel = 'fpc.forms.SistemaForm'
        try:
            ts_adm.save()
        except:
            pass
        
         
        # opção gerenciamento de usuários
        ts_gerencia_usuario = Transacao.objects.get_or_new(nome='ts_gerencia_usuario')
        ts_gerencia_usuario.nome = 'ts_gerencia_usuario'
        ts_gerencia_usuario.titulo = 'Gerenciamento de Usuários'
        ts_gerencia_usuario.tipoTransacao = 'F'
        ts_gerencia_usuario.posicao = 1
        ts_gerencia_usuario.formModel = 'fpc.forms.PainelForm'
        ts_gerencia_usuario.image_url = 'class glyphicon glyphicon-list-alt'
        ts_gerencia_usuario.transacaoPai_id = ts_adm.id
        try:
            ts_gerencia_usuario.save()
        except:
            pass
         

        # opção gerenciamento de interface com o usuário
        ts_gerencia_ui = Transacao.objects.get_or_new(nome='ts_gerencia_ui')
        ts_gerencia_ui.nome = 'ts_gerencia_ui'
        ts_gerencia_ui.titulo = 'Gerenciamento das Configurações do Framework'
        ts_gerencia_ui.tipoTransacao = 'F'
        ts_gerencia_ui.posicao = 2
        ts_gerencia_ui.formModel = 'fpc.forms.PainelForm'
        ts_gerencia_ui.image_url = 'class glyphicon glyphicon-list-alt'
        ts_gerencia_ui.transacaoPai_id = ts_adm.id
        try:
            ts_gerencia_ui.save()
        except:
            ts_gerencia_ui = Transacao.objects.get(nome='ts_gerencia_ui')


        # cadastro de departamentos
        ts = Transacao.objects.get_or_new(nome='ts_cad_departamento')
        ts.nome = 'ts_cad_departamento'
        ts.titulo = 'Cadastro de Departamentos'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 1
        ts.formModel = 'adm.forms.DepartamentoForm'
        ts.model = 'adm.models.Departamento'
        ts.image_url = 'class glyphicon glyphicon glyphicon-tree-deciduous'
        ts.transacaoPai_id = ts_gerencia_usuario.id
        try:
            ts.save()
        except:
            pass;

         

        # menu cadastro de usuários
        ts = Transacao.objects.get_or_new(nome='ts_cad_usuario')
        ts.nome = 'ts_cad_usuario'
        ts.titulo = 'Cadastro de Usuários'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 2
        ts.formModel = 'adm.forms.UsuarioForm'
        ts.model = 'adm.models.Usuario'
        ts.image_url = 'class glyphicon glyphicon glyphicon glyphicon-user'
        ts.transacaoPai_id = ts_gerencia_usuario.id
        try:
            ts.save()
        except:
            pass;


        # menu personalizar tela principal
        ts = Transacao.objects.get_or_new(nome='ts_config_fpc')
        ts.nome = 'ts_config_fpc'
        ts.titulo = 'Personalizar Framework'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/adm.views.personalizar_framework'
        ts.posicao = 1
        ts.formModel = 'adm.forms.FpcConfigForm'
        ts.model = 'fpc.models.Fpc'
        ts.image_url = 'class glyphicon glyphicon glyphicon glyphicon-user'
        ts.transacaoPai_id = ts_gerencia_ui.id
        try:
            ts.save()
        except:
            pass;


        # cadastro de sistemas
        ts = Transacao.objects.get_or_new(nome='ts_cad_sistema')
        ts.nome = 'ts_cad_sistema'
        ts.titulo = 'Cadastro de Sistemas'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 3
        ts.formModel = 'adm.forms.SistemaForm'
        ts.model = 'adm.models.Sistema'
        ts.image_url = 'class glyphicon glyphicon glyphicon-asterisk'
        ts.transacaoPai_id = ts_adm.id
        try:
            ts.save()
        except:
            pass;


        ###################################### Módulo Estoque ######################################

        # Sistema Estoque
        ts = Transacao()
        ts.nome = 'mod_estoque'
        ts.titulo = 'Estoque'
        ts.tipoTransacao = 'S'
        ts.posicao = 2
        ts.image_url = 'class glyphicon glyphicon-folder-close'
        ts.formModel = 'fpc.forms.SistemaForm'
        try:
            ts.save()
        except:
            pass;


        # menu Estoque
        ts = Transacao()
        ts.nome = 'cad_estoque'
        ts.titulo = 'Cadastro'
        ts.tipoTransacao = 'F'
        ts.posicao = 1
        ts.formModel = 'fpc.forms.PainelForm'
        ts.image_url = 'class glyphicon glyphicon-list-alt'
        ts.transacaoPai = Transacao.objects.get(nome='mod_estoque')
        try:
            ts.save()
        except:
            pass;


        # menu Cadastro de grupo 
        ts = Transacao()
        ts.nome = 'cad_grupo'
        ts.titulo = 'Cadastro de Grupos'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 1
        ts.formModel = 'estoque.forms.GrupoProdutoForm'
        ts.model = 'estoque.models.GrupoProduto'
        ts.image_url = 'class glyphicon glyphicon glyphicon-asterisk'
        ts.transacaoPai = Transacao.objects.get(nome='cad_estoque')
        try:
            ts.save()
        except:
            pass;


        # menu Cadastro de subgrupo 
        ts = Transacao()
        ts.nome = 'cad_subgrupo'
        ts.titulo = 'Cadastro de Subgrupos'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 1
        ts.formModel = 'estoque.forms.SubgrupoProdutoForm'
        ts.model = 'estoque.models.SubgrupoProduto'
        ts.image_url = 'class glyphicon glyphicon glyphicon-asterisk'
        ts.transacaoPai = Transacao.objects.get(nome='cad_estoque')
        try:
            ts.save()
        except:
            pass;


        # menu Cadastro de produto 
        ts = Transacao()
        ts.nome = 'cad_produto'
        ts.titulo = 'Cadastro de Produtos'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 1
        ts.formModel = 'estoque.forms.ProdutoForm'
        ts.model = 'estoque.models.Produto'
        ts.image_url = 'class glyphicon glyphicon glyphicon-asterisk'
        ts.transacaoPai = Transacao.objects.get(nome='cad_estoque')
        try:
            ts.save()
        except:
            pass;



        ###################################### Módulo SAE ######################################

        # Sistema SAE
        ts = Transacao()
        ts.nome = 'mod_sae'
        ts.titulo = 'Assistência Estudantil'
        ts.tipoTransacao = 'S'
        ts.posicao = 2
        ts.image_url = 'class glyphicon glyphicon-folder-close'
        ts.formModel = 'fpc.forms.SistemaForm'
        try:
            ts.save()
        except:
            pass;


        # menu Cadastros
        ts = Transacao()
        ts.nome = 'cad_sae'
        ts.titulo = 'Cadastro'
        ts.tipoTransacao = 'F'
        ts.posicao = 1
        ts.formModel = 'fpc.forms.PainelForm'
        ts.image_url = 'class glyphicon glyphicon-list-alt'
        ts.transacaoPai = Transacao.objects.get(nome='mod_sae')
        try:
            ts.save()
        except:
            pass;


        # menu Vale Alimentação
        ts = Transacao()
        ts.nome = 'cad_vale_alimentacao'
        ts.titulo = 'Vale Alimentação'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 1
        ts.formModel = 'sae.forms.ValeAlimentacaoForm'
        ts.model = 'sae.models.ValeAlimentacao'
        ts.image_url = 'class glyphicon glyphicon glyphicon-asterisk'
        ts.transacaoPai = Transacao.objects.get(nome='cad_sae')
        try:
            ts.save()
        except:
            pass;


        # menu Ocorrências
        ts = Transacao()
        ts.nome = 'cad_ocorrencias'
        ts.titulo = 'Ocorrências'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 1
        ts.formModel = 'sae.forms.OcorrenciasForm'
        ts.model = 'sae.models.Ocorrencias'
        ts.image_url = 'class glyphicon glyphicon glyphicon-asterisk'
        ts.transacaoPai = Transacao.objects.get(nome='cad_sae')
        try:
            ts.save()
        except:
            pass;


        # menu Gerar Arquivo RU
        ts = Transacao()
        ts.nome = 'cad_gera_arq_ru'
        ts.titulo = 'Gerar Arquivo RU'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 1
        ts.formModel = 'sae.forms.GeraArquivoRUForm'
        ts.model = 'sae.models.GeraArquivoRU'
        ts.image_url = 'class glyphicon glyphicon glyphicon-asterisk'
        ts.transacaoPai = Transacao.objects.get(nome='cad_sae')
        try:
            ts.save()
        except:
            pass;

        

        # menu Consultas/Relatórios
        ts = Transacao()
        ts.nome = 'cad_consulta_sae'
        ts.titulo = 'Consultas/Relatórios'
        ts.tipoTransacao = 'F'
        ts.posicao = 1
        ts.formModel = 'fpc.forms.PainelForm'
        ts.image_url = 'class glyphicon glyphicon-list-alt'
        ts.transacaoPai = Transacao.objects.get(nome='mod_sae')
        try:
            ts.save()
        except:
            pass;


        # menu Imprimir Agendamento
        ts = Transacao()
        ts.nome = 'cad_imprime_agendamento_sae'
        ts.titulo = 'Imprime Agendamento'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 1
        ts.formModel = 'sae.forms.ImprimeAgendamentoForm'
        ts.model = 'sae.models.ImprimeAgendamento'
        ts.image_url = 'class glyphicon glyphicon glyphicon-asterisk'
        ts.transacaoPai = Transacao.objects.get(nome='cad_consulta_sae')
        try:
            ts.save()
        except:
            pass;
        
        # menu Estudo socioeconomico
        ts = Transacao()
        ts.nome = 'estudosocioeconomico_sae'
        ts.titulo = 'Estudo Socioeconômico'
        ts.tipoTransacao = 'F'
        ts.posicao = 1
        ts.formModel = 'fpc.forms.PainelForm'
        ts.image_url = 'class glyphicon glyphicon-list-alt'
        ts.transacaoPai = Transacao.objects.get(nome='mod_sae')
        try:
            ts.save()
        except:
            pass;
        
        # Preencher formulário do estudo socioeconômico preliminar
        ts = Transacao()
        ts.nome = 'estudosocioeconomico_preliminar_sae'
        ts.titulo = 'Preencher Formulário'
        ts.tipoTransacao = 'T'
        ts.posicao = 1
        ts.formModel = 'sae.forms.EstudoSocioEconomicoForm'
        ts.model = 'sae.models.EstudoSocioEconomico'
        ts.image_url = 'class glyphicon glyphicon glyphicon-asterisk'
        ts.transacaoPai = Transacao.objects.get(nome='estudosocioeconomico_sae')
        try:
            ts.save()
        except:
            pass;

        # Preencher formulário do estudo socioeconômico
        ts = Transacao()
        ts.nome = 'formulario_estudosocioeconomico_dadospessoais_sae'
        ts.titulo = 'Dados Pessoais'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 4
        ts.formModel = 'sae.forms.EstudoSocioEconomicoDadosPessoaisForm'
        ts.model = 'sae.models.EstudoSocioEconomico'
        ts.image_url = 'class glyphicon glyphicon glyphicon-asterisk'
        ts.transacaoPai = Transacao.objects.get(nome='estudosocioeconomico_sae')
        try:
            ts.save()
        except:
            pass;


        # Preencher formulário do estudo socioeconômico
        ts = Transacao()
        ts.nome = 'formulario_estudosocioeconomico_dadosfamiliares_sae'
        ts.titulo = 'Dados Familiares'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 5
        ts.formModel = 'sae.forms.EstudoSocioEconomicoDadosFamiliaresForm'
        ts.model = 'sae.models.EstudoSocioEconomico'
        ts.image_url = 'class glyphicon glyphicon glyphicon-asterisk'
        ts.transacaoPai = Transacao.objects.get(nome='estudosocioeconomico_sae')
        try:
            ts.save()
        except:
            pass;


        # Preencher formulário do estudo socioeconômico
        ts = Transacao()
        ts.nome = 'formulario_estudosocioeconomico_bens_sae'
        ts.titulo = 'Bens Pertencente a Família'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 6
        ts.formModel = 'sae.forms.EstudoSocioEconomicoBensForm'
        ts.model = 'sae.models.EstudoSocioEconomico'
        ts.image_url = 'class glyphicon glyphicon glyphicon-asterisk'
        ts.transacaoPai = Transacao.objects.get(nome='estudosocioeconomico_sae')
        try:
            ts.save()
        except:
            pass;


        # Imprimir formulário do estudo socioeconômico
        ts = Transacao()
        ts.nome = 'imprimir_estudosocioeconomico_sae'
        ts.titulo = 'Imprimir Formulário'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 2
        ts.formModel = 'sae.forms.ImprimirEstudoSocioEconomicoForm'
        ts.model = 'sae.models.EstudoSocioEconomico'
        ts.image_url = 'class glyphicon glyphicon glyphicon-asterisk'
        ts.transacaoPai = Transacao.objects.get(nome='estudosocioeconomico_sae')
        try:
            ts.save()
        except:
            pass;


        # Preencher formulário do estudo socioeconômico
        ts = Transacao()
        ts.nome = 'info_estudosocioeconomico_sae'
        ts.titulo = 'Informações Sobre o Estudo'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 3
        ts.formModel = 'sae.forms.InfoEstudoSocioEconomicoForm'
        ts.image_url = 'class glyphicon glyphicon glyphicon-asterisk'
        ts.transacaoPai = Transacao.objects.get(nome='estudosocioeconomico_sae')
        try:
            ts.save()
        except:
            pass;
                
"""
    Classe de controle para registrar data e usuário que alterou um registro
"""    
class FpcControle(models.Model):
    dtInclusao = models.DateTimeField("Data Inclusão", null=False, blank=False)
    dtAlteracao = models.DateTimeField("Data Inclusão", null=True, blank=True)
    userInclusao = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='userInclusao')
    userAlteracao = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='userAlteracao', null=True, blank=True)


    

"""
    Definições de campos
"""    

class FpcTipoField:
    number = 0
    text = 1
    decimal = 2
    date = 3
    lookup = 4
    memo = 5
    

class FpcCustomField(object):
    """
        Classe base para os atributos dos models. 
        
        Objetivo: Estender os tipos basicos do Django com mais funcionalidades. 
    """
    def __init__(self, verbose_name=None, mascara=None, mascara_placeholder="_", subtipo=None, insertable=True, size=None, onchange=False, **kargs):
        self.verbose_name = verbose_name  
        self.mascara = mascara 
        self.mascara_placeholder = mascara_placeholder 
        self.subtipo = subtipo 
        self.insertable = insertable 
        self.size = size 
        self.onchange = onchange
        if self.subtipo != None:
            if self.subtipo == "telefone":
                kargs["max_length"] = 15
                if self.verbose_name is None:
                    self.verbose_name = "Telefone"
                self.mascara = "(999) 9999-9999"
                self.mascara_placeholder = "_"

    
    @property
    def size(self):
        return self.__size


    @size.setter
    def size(self, value):
        if value != None:
            if isinstance(value, str):
                if not (value.endswith("px") or value.endswith("%")):
                    self.__size = "%spx" % value
                else:
                    self.__size = value
            elif isinstance(value, int):
                self.__size = "%dpx" % value
            else:
                raise ValueError("Valor incorreto para o atributo size")                     
        else:
            self.__size = None
    

class FpcTextField(models.CharField, FpcCustomField):
    def __init__(self, verbose_name=None, caixa_alta=True, mascara=None, mascara_placeholder="_", subtipo=None, insertable=True, size=None, onchange=False, **kargs):
        models.TextField.__init__(self, **kargs)
        FpcCustomField.__init__(self, verbose_name, mascara, mascara_placeholder, subtipo, insertable, size, onchange, **kargs)
        self.caixa_alta = caixa_alta


class FpcIntegerField(models.IntegerField, FpcCustomField):
    def __init__(self, verbose_name=None, auto_increment=False, mascara=None, mascara_placeholder="_", subtipo=None, insertable=True, size=None, onchange=False, **kargs):
        models.IntegerField.__init__(self, **kargs)
        FpcCustomField.__init__(self, verbose_name, mascara, mascara_placeholder, subtipo, insertable, size, onchange, **kargs)
        self.auto_increment = auto_increment


class FpcDecimalField(models.DecimalField, FpcCustomField):
    def __init__(self, verbose_name=None, subtipo=None, insertable=True, size=None, onchange=False, **kargs):
        models.DecimalField.__init__(self, **kargs)
        FpcCustomField.__init__(self, verbose_name, subtipo, insertable, size, onchange, **kargs)


class FpcDateField(models.DateField, FpcCustomField):
    def __init__(self, verbose_name=None, subtipo=None, insertable=True, size=None, onchange=False, **kargs):
        models.DateField.__init__(self, **kargs)
        FpcCustomField.__init__(self, verbose_name, subtipo, insertable, size, onchange, **kargs)

            
class FpcDateTimeField(models.DateTimeField, FpcCustomField):
    def __init__(self, verbose_name=None, subtipo=None, insertable=True, size=None, onchange=False, **kargs):
        models.DateTimeField.__init__(self, **kargs)
        FpcCustomField.__init__(self, verbose_name, subtipo, insertable, size, onchange, **kargs)


class FpcValidation(Exception):
    """ 
        Classe para validação do modelo.
    """
    def __init__(self, errors, warnings, infos):
        self.errors = errors
        self.warnings = warnings
        self.infos = infos
           
           
class FpcManager(models.Manager):
    """
       Classe base para managers dos modelos
    """
    
    def existe_campo_duplicado(self, obj, field):
        if type(field) == tuple:
            q_expr = []
            for fld in field:
                value = getattr(obj, fld)
                if value == None:
                    return False
                q = Q(("%s__exact" % fld, value))
                q_expr.append(q)
            q_expr = reduce(operator.and_, q_expr)
            if obj.pk != None and obj.pk > 0:
                return self.filter(q_expr).exclude(pk=obj.pk).exists()
            else:
                return self.filter(q_expr).exists()
        else:
            value = getattr(obj, field.name) 
            if value != None: 
                q = Q(("%s__exact" % field.name, value))
                if obj.pk != None and obj.pk > 0 and not obj._state.adding:
                    return self.filter(q).exclude(pk=obj.pk).exists()
                else:
                    return self.filter(q).exists()
           
    def sequence(self, field_name):
        value = self.all().aggregate(Max(field_name))["%s__max" % field_name]
        if value != None:
            value = value + 1
        else:
            value = 1
        return value
    
    def save(self, obj):
        if not obj._state.adding and obj.pk != None and obj.update_fields != None and len(obj.update_fields) > 0:
            super(FpcModel, obj).save(force_insert=False, force_update=False, using=None,
                                       update_fields=obj.update_fields)
        else:
            super(FpcModel, obj).save()

    
class FpcModel(models.Model):
    objects = FpcManager()

    """
        Classe base para os objetos de modelo
    """
    class Meta:
        abstract = True
        #unique_together = ("codigo", "nome")

    update_fields = None
    lista_models = None

    def setAutoIncrementFields(self):
        manager = type(self).objects
        for field in self._meta.fields: 
            if type(field) == FpcIntegerField and field.auto_increment and getattr(self, field.name) == None:
                value = manager.sequence(field.name)
                setattr(self, field.name, value)

    def save(self, *args, **kwargs):
        self.clean()
        self.setAutoIncrementFields()
        manager = type(self).objects
        manager.save(self)
        self.update_fields = []
    
    def clean(self):
        errors = []
        manager = type(self).objects
        # Validação para os campos unique a nível de coluna
        for field in self._meta.fields: 
            if field.unique and type(field) != models.AutoField and getattr(self, field.name) != None:
                if manager.existe_campo_duplicado(self, field):
                    msg = 'Campo "%s" já está cadastrado.' % field.verbose_name
                    errors.append({'msg' : msg, 'field' : field.name})
        
        # Validação para os campos unique com várias colunas
        if self._meta.unique_together != None:
            for fields in self._meta.unique_together:
                if type(fields) == tuple:
                    if manager.existe_campo_duplicado(self, fields):
                        verbose_names = ", ".join([self._meta._name_map[fld][0].verbose_name for fld in fields])
                        msg = 'Já existe outro registro com os campos "%s" informados.' % verbose_names
                        errors.append({'msg' : msg})
                        
        if len(errors) > 0:
            raise FpcValidation(errors, None, None)
                    
   
    @classmethod
    def field_by_name(self, field_name):
        if field_name == 'pk':
            return self._meta.pk
        else:
            return self._meta.get_field_by_name(field_name)[0]


    __fields_insensitive_cache = None


    @classmethod
    def field_by_name_insensitive(cls, field_name):
        field_name = field_name.lower()
        try:
            return cls.__fields_insensitive_cache[field_name] 
        except KeyError:
            raise FieldDoesNotExist('%s has no field named %r' % (cls.get_name(), field_name))            
        except TypeError:
            cls.__fields_insensitive_cache = {}
            for f in cls._meta.local_fields:
                cls.__fields_insensitive_cache[f.name.lower()] = f
            return cls.field_by_name_insensitive(field_name)
 
        
    def onChange(self, field_name):
        pass
    
    
    def checkUpdateFields(self, obj_copy):
        self.update_fields += [campo.name for campo in self._meta.fields if getattr(self, campo.name) != getattr(obj_copy, campo.name)]
    
    
    def get_update_values(self):
        result = {}
        for field_name in self.update_fields:
            field = self._meta.get_field_by_name(field_name)[0]
            result[field_name] = self.get_valor_formatado(field)
        return result
           

    def get_values(self):
        result = {}
        for field in self._meta.fields:
            if field.name not in ("controle"):
                result[field.name] = self.get_valor_formatado(field)
        return result
    
    def get_values_flat(self):
        result = {}
        for field in self._meta.fields:
            result[field.name] = self.get_valor_formatado(field, flat=True)
        return result
    
    def set_values(self, values):
        for field_name in values:
            field = self.field_by_name(field_name)
            value = self.text_to_value(field, values[field_name])
            if self.get_tipo_field(field) == FpcTipoField.lookup:
                setattr(self, field_name + "_id", value)
            else:
                setattr(self, field_name, value)
    
    def getNome(self):
        return str(self)[8:-2]
    
    
    @classmethod
    def get_name(cls):
        return cls._meta.object_name


    @staticmethod
    def text_to_value(field, value):
        """
            Converte text para value de acordo com o tipo de field  
            field -> referência do campo do modelo
        """
        if value == None or value == "":
            return ""
        else:
            try:
                tipo = FpcModel.get_tipo_field(field)
                if tipo == FpcTipoField.number:
                    value = int(value)
                elif tipo == FpcTipoField.date:
                    t_value = type(value)
                    if t_value == datetime:
                        pass
                    elif t_value == str:
                        # conversão realizada de duas maneiras
                        # 1) str contém /. Ex.: 27/06/2014
                        # 2) str não contém /  Ex.: 27062014
                        if "/" in value:
                            value = datetime.strptime(value, "%d/%m/%Y")
                        else:
                            value = datetime.strptime(value, "%d%m%Y")
                    else:
                        raise ValidationError()
                elif tipo == FpcTipoField.decimal:
                    if type(value) == str:
                        formata = lambda value, decimal : ("%.*f" % (decimal, value)).replace(".", ",")
                        value =  formata(value, field.decimal_places)
                        value = Decimal(value.replace(",", "."))
                return value
            except Exception as e:
                raise ValidationError("Não foi possível formatar o campo %s. Erro interno: %s" % (field.name, e))
    

    @staticmethod
    def value_to_text(field, value):
        """
            Converte value para text de acordo com o tipo de field para apresentação  
        """
        if value == None or value == "":
            return ""
        else:
            try:
                tipo = FpcModel.get_tipo_field(field)
                if tipo == FpcTipoField.number:
                    value = str(value)
                elif tipo == FpcTipoField.date:
                    t_value = type(value)
                    if t_value == datetime:
                        value = value.strftime("%d/%m/%Y")
                    elif t_value == str:
                        try:
                            # conversão realizada de duas maneiras
                            # 1) str contém /. Ex.: 27/06/2014
                            # 2) str não contém /  Ex.: 27062014
                            if "/" in value:
                                value = datetime.strptime(value, "%d/%m/%Y")
                            else:
                                value = datetime.strptime(value, "%d%m%Y")
                            value = value.strftime("%d/%m/%Y")
                        except:
                            value = ""
                    else:
                        value = ""
                elif tipo == FpcTipoField.decimal:
                    formata = lambda value, decimal : ("%.*f" % (decimal, value)).replace(".", ",")
                    value =  formata(value, field.decimal_places)
                return value
            except Exception as e:
                raise ValidationError("Não foi possível formatar o campo %s. Erro interno: %s" % (field.name, e))

            
    
    def get_valor_formatado(self, field, flat=False):
        """
            Retorna o valor formatado de uma instância de acordo com o field
            field -> instância do field  
            flat -> se True retorna apenas atributos simples 
        """
        try:
            value = None
            tipo = FpcModel.get_tipo_field(field)
            if tipo == FpcTipoField.text:
                value = getattr(self, field.name)
            elif tipo == FpcTipoField.number:
                value = getattr(self, field.name)
                if value != None:
                    value = str(value)
            elif tipo == FpcTipoField.date:
                value = getattr(self, field.name)
                if value != None:
                    value = value.strftime("%d/%m/%Y")
            elif tipo == FpcTipoField.decimal:
                value = getattr(self, field.name)
                if value != None:
                    formata = lambda value, decimal : ("%.*f" % (decimal, value)).replace(".", ",")
                    value =  formata(value, field.decimal_places)
            elif tipo == FpcTipoField.lookup:
                key = getattr(self, "%s_id" % field.name)
                if key != None and type(key) == int and key > 0:
                    if flat:
                        value = key
                    else:
                        value = {}
                        value["id"] = key
                        obj = getattr(self, field.name)
                        value["desc"] = obj.__str__()
            elif tipo == FpcTipoField.memo:
                value = getattr(self, field.name)
            if value == None:
                return ""
            else:
                return value
        except Exception as e:
            raise ValidationError("Não foi possível formatar o campo %s. Erro interno: %s" % (field.name, e))
        

    @staticmethod
    def get_valor_default_formatado(field):
        try:
            tipo = FpcModel.get_tipo_field(field)
            value = field.default
            if tipo == FpcTipoField.number:
                if value != None:
                    value = str(value)
            elif tipo == FpcTipoField.date:
                value = value.strftime("%d/%m/%Y")
            elif tipo == FpcTipoField.decimal:
                formata = lambda value, decimal : ("%.*f" % (decimal, value)).replace(".", ",")
                value =  formata(value, field.decimal_places)
            elif tipo == FpcTipoField.lookup:
                key = getattr(self, "%s_id" % field.name)
                if not (type(key) == int and key > 0):
                    value = None

            if value == None:
                return ""
            else:
                return value
        except:
            raise ValidationError("Não foi possível formatar o campo %s." % field.name)


    @staticmethod
    def get_tipo_field(field):
        if hasattr(field, 'tipo'):
            return field.tipo
        else:
            tipo_field_model = type(field)
            tipo = None
            if tipo_field_model == FpcTextField or tipo_field_model == models.CharField:
                tipo = FpcTipoField.text
            elif tipo_field_model == FpcIntegerField or tipo_field_model == models.IntegerField or tipo_field_model == models.AutoField:
                tipo = FpcTipoField.number
            elif tipo_field_model == FpcDecimalField or tipo_field_model == models.DecimalField:
                tipo = FpcTipoField.decimal 
            elif tipo_field_model == models.DateField:
                tipo = FpcTipoField.date
            elif tipo_field_model == models.ForeignKey:
                tipo = FpcTipoField.lookup
            else:
                raise ValidationError("Não foi possível obter o tipo do campo %s." % field.name)
            field.tipo = tipo
            return tipo

        
    def __str__(self):
        if hasattr(self, "codigo") and hasattr(self, "nome"):
            return "%s - %s" % (self.codigo, self.nome)
        elif hasattr(self, "nome"): 
            return self.nome
        elif hasattr(self, "descricao"): 
            return self.descricao
        elif hasattr(self, "denominacao"): 
            return self.denominacao
        else:
            return "Denominação não fornecida"


    
    
class EmsManager(FpcManager):
    """
        Classe base para manager ErlangMS
    """
    def get(self, pk):
        url = '/fpc/get?db_table="%s"&pk=%s' % (self.model._meta.db_table, pk)
        json_str = EmsRest.get(url)
        obj_dict = json.loads(json_str)
        obj = self.model()
        obj.set_values(obj_dict)
        return obj

    def pesquisar(self, filtro, fields, limit_ini, limit_fim):
        if isinstance(fields, tuple):
            fields = ",".join(fields)
        url = '/fpc/pesquisar?db_table="%s"&filtro="%s"&fields="%s"&limit_ini=%d&limit_fim=%d' % \
            (self.model._meta.db_table, filtro, fields, limit_ini, limit_fim)
        result = EmsRest.get(url)
        return result
   
    def as_object(self, d):
        p = self.model()
        p.__dict__.update(d)
        return p
   
    def existe_campo_duplicado(self, obj, field):
        field_name = field.name
        field_value = getattr(obj, field_name)
        url = '/fpc/existe_campo_duplicado?db_table="%s"&pk=%s&field_name="%s"&field_value="%s"' % \
            (self.model._meta.db_table, obj.pk, field_name, field_value)
        result = EmsRest.get(url)
        return result == "true"

    def sequence(self, field_name):
        url = '/fpc/sequence?db_table="%s"&field_name="%s' % (self.model._meta.db_table, field_name)
        result = EmsRest.get(url)
        return int(result)
    
    def save(self, obj):
        update_fields = json.dumps(obj.get_update_values(), default=json_encode_java)
        url = '/fpc/save?db_table="%s"&pk=%s' % (self.model._meta.db_table, obj.pk)
        result = EmsRest.post(url, update_fields)
        if result != "ok":
            raise DatabaseError(result)
        obj.update_fields = []


class EmsModel(FpcModel):
    """
        Classe base para os objetos de modelo ErlangMS
    """
    objects = EmsManager()

    class Meta:
        abstract = True
        #unique_together = ("codigo", "nome")

    def __init__(self, *args, **kwargs):
        super(FpcModel, self).__init__(*args, **kwargs)
        pass
    


class Fpc(FpcModel):
    """
        Classe principal de configurações do Fpc
    """
    id = models.IntegerField('Id', primary_key=True)
    developer = FpcTextField(max_length=40, default="Everton de Vargas Agilar", null=False, insertable=False, editable=False)
    copyright = FpcTextField(max_length=100, default="Copyright 2015 Everton de Vargas Agilar - Todos os direitos reservados.", null=False, insertable=False, editable=False)
    local = FpcTextField(max_length=30, default="Brasília/DF", null=True, blank=True)
    fale_conosco = FpcTextField("Fale Conosco", max_length=250, default="", null=False,size=400)
    nome = FpcTextField("Nome", max_length=40, default="Eliot", null=False,size=100)
    descricao = FpcTextField("Descricao", max_length=250, default="Eliot Web Framework", null=False,size=400)
    
    # css styles do portal
    css_header_background_color = models.CharField("Cor do cabeçalho", max_length=250, default="#f8f8f8", null=False)
    
    

    __fpc = None;
    user = None;

    """ Obtém uma instância default da classe Fpc """
    @classmethod
    def getFpc(self):
        if Fpc.__fpc == None:
            Fpc.__fpc = Fpc.objects.get(pk=1)
        return Fpc.__fpc 


    @classmethod
    def getCurrentUser(self):
        return Fpc.getFpc().user

    @classmethod
    def setCurrentUser(self, user):
        Fpc.getFpc().user = user

