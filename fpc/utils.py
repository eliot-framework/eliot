# -*- coding: utf-8 -*-

import datetime
import decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import connection
from django.db import models
from django.http import HttpResponseRedirect
from django.utils.log import getLogger
import http
import logging
import os
from threading import RLock


class FpcException(Exception):
    """
        Classe de exception para erros do framework Fpc
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)    


# functions
def importModule(value):
    package = value.split(".")[0]
    eval("import "+ package)
    return 
  

     

# Deleta um arquivo de forma segura sem levantar erro    
def fpcDeleteFileSeguro(fileName):
    try:
        os.remove(fileName)
    except:
        pass




# lambda functions

fpcatDecimal = lambda value, decimal : ("%.*f" % (decimal, value)).replace(".", ",")


#
# Implementa uma pilha para uso geral
#
class FpcStack(object):
    def __init__(self) :
        self.items = []
 
    def push(self, item) :
        self.items.apend(item)
 
    def pop(self) :
        return self.items.pop()
 
    def isEmpty(self) :
        return (self.items == [])
    

#
# Implementa uma tabela hash para cache para uso geral
#    
class FpcCache(object):
    def __init__(self):
        self.__items = {}
        self.__lock = RLock()

    def get(self, key):
        with self.__lock:
            return self.__items.get(key)

    def set(self, key, value):
        with self.__lock:
            self.__items[key] = value
            
            

class FpcSingleton(type):
    __instances = {}
    __lock = RLock()
    def __call__(self, *args, **kwargs):
        with self.__lock:
            if self not in self.__instances:
                self.__instances[self] = super(FpcSingleton, self).__call__(*args, **kwargs)
            return self.__instances[self]


class EmsRest(object):
    
    @staticmethod
    def get(url):
        return EmsRest.call("GET", url, "")
    
    @staticmethod
    def post(url, body):
        return EmsRest.call("POST", url, body)

    @staticmethod
    def call(method, url, body):
        conn = http.client.HTTPConnection(settings.IP_ERLANGMS, settings.PORT_ERLANGMS)
        conn.request(method, url, body)
        try:
            json_str = conn.getresponse().read().decode("utf-8")
            return json_str
        finally:
            conn.close()

def json_encode_java(obj):
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
        return obj.strftime("%d/%m/%Y")
    raise TypeError(repr(obj) + " is not JSON serializable")
        
