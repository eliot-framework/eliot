# -*- coding: UTF-8 -*-


from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.backends.dummy.base import DatabaseError
from django.db.models.aggregates import Max
from django.db.models.fields import FieldDoesNotExist
from django.db.models.query_utils import Q
from fpc.utils import EmsRest, json_encode_java
from functools import reduce
import json
import operator
import os
from urllib.parse import unquote


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
        try:
            return Transacao.objects.values_list('pk', flat=True).get(model=model_str)
        except Exception:
            raise Exception("Model %s não possui transação cadastrado!" % model_str)
            
    
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
    def __init__(self, verbose_name=None, mascara=None, mascara_placeholder="_", subtipo=None, insertable=True, size=None, onchange=False, lazy=False, render="input", **kargs):
        self.verbose_name = verbose_name  
        self.mascara = mascara 
        self.mascara_placeholder = mascara_placeholder 
        self.subtipo = subtipo 
        self.insertable = insertable 
        self.size = size 
        self.onchange = onchange
        self.lazy = lazy
        self.render = render
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
    def __init__(self, verbose_name=None, caixa_alta=True, mascara=None, mascara_placeholder="_", subtipo=None, insertable=True, size=None, onchange=False, lazy=False, render="input", **kargs):
        models.TextField.__init__(self, **kargs)
        FpcCustomField.__init__(self, verbose_name, mascara, mascara_placeholder, subtipo, insertable, size, onchange, lazy, render, **kargs)
        self.caixa_alta = caixa_alta


class FpcIntegerField(models.IntegerField, FpcCustomField):
    def __init__(self, verbose_name=None, auto_increment=False, mascara=None, mascara_placeholder="_", subtipo=None, insertable=True, size=None, radio=None, onchange=False, lazy=False, render="input", **kargs):
        models.IntegerField.__init__(self, **kargs)
        FpcCustomField.__init__(self, verbose_name, mascara, mascara_placeholder, subtipo, insertable, size, onchange, lazy, render, **kargs)
        self.auto_increment = auto_increment
        self.radio = radio


class FpcDecimalField(models.DecimalField, FpcCustomField):
    def __init__(self, verbose_name=None, subtipo=None, insertable=True, size=None, onchange=False, lazy=False, render="input", **kargs):
        models.DecimalField.__init__(self, **kargs)
        FpcCustomField.__init__(self, verbose_name, None, None, subtipo, insertable, size, onchange, lazy, render, **kargs)


class FpcDateField(models.DateField, FpcCustomField):
    def __init__(self, verbose_name=None, subtipo=None, insertable=True, size=None, onchange=False, lazy=False, render="input", **kargs):
        models.DateField.__init__(self, **kargs)
        FpcCustomField.__init__(self, verbose_name, None, None, subtipo, insertable, size, onchange, lazy, render, **kargs)

            
class FpcDateTimeField(models.DateTimeField, FpcCustomField):
    def __init__(self, verbose_name=None, subtipo=None, insertable=True, size=None, onchange=False, lazy=False, render="input", **kargs):
        models.DateTimeField.__init__(self, **kargs)
        FpcCustomField.__init__(self, verbose_name, None, None, subtipo, insertable, size, onchange, lazy, render, **kargs)


class FpcForeignKey(models.ForeignKey, FpcCustomField):
    def __init__(self, verbose_name=None, insertable=True, size=None, onchange=False, lazy=False, render="lookup", **kargs):
        models.ForeignKey.__init__(self, **kargs)
        FpcCustomField.__init__(self, verbose_name, None, None, None, insertable, size, onchange, lazy, render, **kargs)


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

    def pesquisar(self, filtro, fields, limit_ini, limit_fim, sort, filtroIds):
        if filtro != None and isinstance(filtro, str) and filtro != "" and filtro != "{}": 
            filtro = json.loads(filtro)
        else:
            filtro = None

        # Verifica os filtros a incluir  
        if filtro != None: 
            expr = []
            result = None
            for fname in filtro:
                fvalue = filtro[fname] 
                if isinstance(fvalue, str):
                    fvalue = unquote(fvalue) 
                expr.append(("%s__contains" % fname, fvalue))
            
            q_expr = [Q(x) for x in expr]    
            q_expr = reduce(operator.and_, q_expr)
    
            # Verifica filtro de ids inseridos
            if filtroIds != "":
                listaIds = filtroIds.split(",")
                q_expr2 = Q(("id__in", listaIds))    
                result = self.values_list(*fields).filter(q_expr | q_expr2)
            else:
                result = self.values_list(*fields).filter(q_expr)
        else:
            result = self.values_list(*fields).all()

        if result.exists():
            # Deve trazer o resultado ordenado
            if sort != None:
                if isinstance(sort, str):
                    sort = sort.split(",")
                result = result.order_by(*sort)

        return result

    
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

    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)
        pass

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
            try:
                field = self.field_by_name(field_name)
                value = self.text_to_value(field, values[field_name])
                if self.get_tipo_field(field) == FpcTipoField.lookup:
                    setattr(self, field_name + "_id", value)
                else:
                    setattr(self, field_name, value)
            except FieldDoesNotExist:
                pass
    
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
                        value = float(value)
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
                        try:
                            obj = getattr(self, field.name)
                            value = {}
                            value["id"] = key
                            value["desc"] = obj.__str__()
                        except Exception:
                            value = None
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
            tipo_str = None
            if tipo_field_model == FpcTextField or tipo_field_model == models.CharField:
                tipo = FpcTipoField.text
                tipo_str = "text"
            elif tipo_field_model == FpcIntegerField or tipo_field_model == models.IntegerField or tipo_field_model == models.AutoField:
                tipo = FpcTipoField.number
                tipo_str = "numero"
            elif tipo_field_model == FpcDecimalField or tipo_field_model == models.DecimalField:
                tipo = FpcTipoField.decimal
                tipo_str = "decimal" 
            elif tipo_field_model == models.DateField:
                tipo = FpcTipoField.date
                tipo_str = "data"
            elif tipo_field_model == models.ForeignKey:
                tipo = FpcTipoField.lookup
                tipo_str = "lookup"
            else:
                raise ValidationError("Não foi possível obter o tipo do campo %s." % field.name)
            field.tipo = tipo
            field.tipo_str = tipo_str
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
        if isinstance(pk, str):
            pk = int(pk)
        url = '%s/%d' % (self.model.service_url, pk)
        json_str = EmsRest.get(url)
        obj_dict = json.loads(json_str)
        obj = self.model()
        obj.set_values(obj_dict)
        return obj

    def pesquisar(self, filtro, fields, limit_ini, limit_fim, sort, filtroIds):
        if isinstance(fields, tuple):
            fields = ",".join(fields)
        if isinstance(sort, list):
            sort = ",".join(sort)
        url = '%s?filtro="%s"&fields="%s"&limit_ini=%d&limit_fim=%d&sort="%s"' % \
            (self.model.service_url, filtro, fields, limit_ini, limit_fim, sort)
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
        if obj.pk > 0:
            url = '%s/%d' % (self.model.service_url, obj.pk)
        else:
            url = '%s' % self.model.service_url
        result = EmsRest.post(url, update_fields)
        if result != "":
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
        if self.service_url != "":
            self.service_url = os.path.join(self.service_url, os.sep)
        else:
            self.service_url = os.path.join(settings.ERLANGMS_URL, os.sep)


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

