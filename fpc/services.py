# -*- coding: UTF-8 -*-
from django.db.models import Q
from django.http.response import HttpResponse
from functools import reduce
import inspect
from io import StringIO
import operator
from urllib.parse import unquote

from fpc.forms import FpcForm
from fpc.utils import FpcSingleton


def fpc_public(func):
    """
        Decorator para marcar um atributo como public.
        Utilizado para informar que uma api é pública em uma classe FpcService. 
    """
    def _wrapped_func(*args, **kwargs):
        response = func(*args, **kwargs)
        return response
    _wrapped_func.fpc_public = True
    return _wrapped_func



class FpcService(object, metaclass=FpcSingleton):
    """
        Classe base para serviços do framework Fpc.
    """
    class Meta:
        model = None 

    def __init__(self):
        try:
            self.model_str = str(self.Meta.model)[8:-2]
            self.model = self.Meta.model
        except:
            self.model_str = None
            self.model = None



    @staticmethod
    def get_service_by_api(api):
        """
            Obtém uma referência para uma instância de um service pelo seu api url. 
        """
        try:
            imp = api.split("/")  # api1/sca/produto
            pacote = imp[1]
            modulo = "services"
            classe = imp[2]
            if "_" in classe:
                classe_ = classe
                pos__ = classe_.index("_")
                classe = classe_[0:pos__].capitalize()
                classe = classe + classe_[pos__+1:].capitalize()
                classe = "%sService" % classe
            else:
                classe = "%sService" % classe.capitalize()
            import_str = "__import__('%s.%s').%s.%s" % (pacote, modulo, modulo, classe)
            service_class = eval(import_str)
            service = service_class()
            service.api = api
            return service
        except:
            raise TypeError("Serviço não encontrado: %s." % api)

    
    @staticmethod
    def __process_param_fields(fields):
        """ 
            Processa parâmetro fields e devolte uma tupla com os campos e um flag is_flat 
        """
        if isinstance(fields, str):
            fields = tuple(fields.split(","))
            is_flat = len(fields) == 1
        else:
            is_flat = False
        return (fields, is_flat)


    @staticmethod
    def __process_param_paginador(paginador):
        """ 
            Processa parâmetro paginador e devolve uma tupla com o índice e offset da paginação 
        """
        if isinstance(paginador, str):
            ini, fim = paginador.split(",")
            paginador = (int(ini), int(fim))
        return paginador
        
        
    @staticmethod
    def __process_param_sort(sort):
        """ 
            Processa parâmetro sort e devolve uma tupla com os campos 
        """
        if isinstance(sort, str):
            sort = sort.split(",")
        return sort
    
            
    @fpc_public
    def all(self, fields=None, sort=None, paginador=None):
        """ Retorna todos os objetos
            fields -> quais campos seram retornados, senão o objeto inteiro
            paginador -> intervalo inicial e final para paginação
        """
        if fields != None:
            fields, is_flat = self.__process_param_fields(fields)
            query = self.model.objects.values_list(*fields, flat=is_flat).all()
        else:
            query = self.model.objects.all()
          
        if sort != None:
            sort = self.__process_param_sort(sort)
            query = query.order_by(*sort)
            
        if paginador != None:
            ini, fim = self.__process_param_paginador(paginador)
            return list(query[ini:fim])
        else:
            return list(query)


    @fpc_public
    def count(self):
        """ 
            Retorna o número de registros cadastrados.
        """
        return self.model.objects.count()


    @fpc_public
    def exists(self):
        """ 
            Retorna True/False se existem registros cadastrados.
        """
        return self.model.objects.exists()


    @fpc_public
    def get(self, obj_id, fields=None):
        """ Obtem o objeto pelo seu respectivo id
            obj_id -> id do objeto que será localizado
            fields -> quais campos seram retornados. Se não informado será retornado o objeto inteiro
        """
        if fields != None:
            fields, is_flat = self.__process_param_fields(fields)
            obj = self.model.objects.values_list(*fields, flat=is_flat).get(pk=obj_id)
        else:
            obj = self.model.objects.get(pk=obj_id)
        return obj


    @fpc_public
    def findby(self, field_name, value, op="exact", fields=None, sort=None, paginador=None, modificador=None):
        """ Localiza um objeto pelo field 
            field_name - campo para localizar
            value -> valor para localizar
            op -> operador: exact, contains, gt
            fields -> quais campos seram retornados, senão o objeto inteiro
            paginador -> intervalo inicial e final para paginação
            modificador -> modifica a pesquisa com count ou exists
        """
        if field_name == 'id':
            field_name = 'pk'
        expressao = Q(("%s__%s" % (field_name, op), value))
        if fields != None:
            fields, is_flat = self.__process_param_fields(fields)
            query = self.model.objects.values_list(*fields, flat=is_flat).filter(expressao)
        else:
            query = self.model.objects.filter(expressao)
        
        if modificador == "count":
            return query.count()
        
        if modificador == "exists":
            return query.exists()

        if sort != None:
            sort = self.__process_param_sort(sort)
            query = query.order_by(*sort)
        
        if paginador != None:
            ini, fim = self.__process_param_paginador(paginador)
            return list(query[ini:fim])
        else:
            return list(query)

    
    @fpc_public
    def filtro(self, filtro, fields=None, sort=None, paginador=None, modificador=None):
        """ Localiza registros através de um filtro avançado 
            filtro - filtro json
            fields -> quais campos seram retornados, senão o objeto inteiro
            paginador -> intervalo inicial e final para paginação
            modificador -> modifica a pesquisa com count ou exists
        """

        # Verifica os filtros a incluir  
        if filtro == None:
            raise TypeError("Filtro não informado.")
             
        expr = []
        for fname in filtro:
            fvalue = filtro[fname]
            if isinstance(fvalue, str):
                fvalue = unquote(fvalue) 
            expr.append(("%s" % fname, fvalue))
        
        q_expr = [Q(x) for x in expr]    
        expressao = reduce(operator.and_, q_expr)

        if fields != None:
            fields, is_flat = self.__process_param_fields(fields)
            query = self.model.objects.values_list(*fields, flat=is_flat).filter(expressao)
        else:
            query = self.model.objects.filter(expressao)
        
        if modificador == "count":
            return query.count()
        
        if modificador == "exists":
            return query.exists()

        if sort != None:
            sort = self.__process_param_sort(sort)
            query = query.order_by(*sort)
        
        if paginador != None:
            ini, fim = self.__process_param_paginador(paginador)
            return list(query[ini:fim])
        else:
            return list(query)
        
        
    @fpc_public
    def get_info(self):
        desc = []
        
        # lista dos métodos da classe
        lista_metodos = []
        for nome_metodo in dir(self):
            attr = getattr(self, nome_metodo)
            if callable(attr) and not nome_metodo.startswith("_") and hasattr(attr, 'fpc_public'):
                params = inspect.getargspec(attr)[0]
                try:
                    params.remove("self")
                except:
                    pass
                metodo = { nome_metodo : { "comment" : attr.__doc__,
                                           "params" : params
                                         } 
                         } 
                lista_metodos.append(metodo)
        
        
        # lista de informações
        desc.append({"api" : self.api, 
                     "service" : str(type(self))[8:-2],
                     "metodos" : lista_metodos
                    })
        
        return desc


    def save(self, obj):
        if not obj._state.adding and obj.pk != None and obj.update_fields != None and len(obj.update_fields) > 0:
            obj.save(update_fields=obj.update_fields)
        else:
            obj.save()     


    def insert(self, values):
        """
            Insere um objeto no banco.
            values -> dicionário ou instância de um objeto
        """            
        if isinstance(values, dict):
            obj = self.model()
            obj.set_values(values)
            self.save(obj)
        else:
            self.save(values)
        

    def update(self, values):
        """
            Atualiza um objeto no banco.
            values -> dicionário ou instância de um objeto para inserir no banco
        """            
        if isinstance(values, dict):
            try:
                obj_id = int(values["id"])
            except:
                obj_id = int(values["pk"])
            obj = self.get(obj_id)
            obj.set_values(values)
            self.save(obj)
        else:
            self.save(values)
    
   
