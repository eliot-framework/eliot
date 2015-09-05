# -*- coding: UTF-8 -*-

from django.contrib import auth
from django.contrib.auth.models import User
from django.db import connection
from django.db import models

from fpc.models import FpcModel, FpcTextField, FpcIntegerField


# 
#    DAO
#
class UsuarioDao(models.Manager):

    def lista_historico_acesso(self, matricula):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT dataHora,
                   nome_departamento,
                   nome_perfil,
                   nome_funcionalidade,
                   sigla_sistema,
                   nome_sistema
            FROM VW_ConsultaHistoricoUsuario
            WHERE usu_matricula = %d""" % matricula)
        result_list = []
        for row in cursor.fetchall():
            result_list.append({ "dataHora" : row[0],
                                 "nome_departamento" : row[1],
                                 "nome_perfil" : row[2],
                                 "nome_funcionalidade" : row[3],
                                 "sigla_sistema" : row[4],
                                 "nome_sistema" : row[5]
                                 })
        return result_list            
        

    def autentica(self, login, senha):
        cursor = connection.cursor()
        sql = "SELECT id FROM auth_user WHERE username = '" + login + "' and password = '" + senha + "'"
        cursor.execute(sql)
        row = cursor.fetchone() 
        if row != None:
            user = User.objects.get(pk=row[0])
            user = Usuario.config_backend(user)
            return user
        else:
            return None


class TelefoneUsuarioDao(models.Manager):
    
    def lista_telefone(self, matricula):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT ddd, numero
            FROM Telefone
            WHERE usu_matricula = %d""" % matricula)
        result_list = []
        for row in cursor.fetchall():
            t = Telefone()
            t.matricula = matricula
            t.ddd = row[0]
            t.numero = row[1]
            result_list.append(t)
        return result_list            


    def excluir_telefone(self, matricula, numero):
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM Telefone
            WHERE usu_matricula = %s 
              AND numero = %s""", [matricula, numero])
        

    def incluir_telefone(self, matricula, ddd, numero):
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Telefone(usu_matricula, ddd, numero)
            VALUES (%s, %s, %s)""", [matricula, ddd, numero])



class EnderecoUsuarioDao(models.Manager):
    
    def lista_endereco(self, matricula):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT tipo, logradouro, municipio, CEP, bairro
            FROM Endereco
            WHERE usu_matricula = %d""" % matricula)
        result_list = []
        for row in cursor.fetchall():
            e = Endereco()
            e.usu_matricula = matricula
            e.tipo = row[0]
            e.logradouro = row[1]
            e.municipio = row[2]
            e.CEP = row[3]
            e.bairro = row[4]
            result_list.append(e)
        return result_list            


    def excluir_endereco(self, matricula, tipo):
        cursor = connection.cursor()
        sql = "DELETE FROM Endereco WHERE usu_matricula = %s AND tipo = %s" % (matricula, tipo)
        cursor.execute(sql)
        

    def incluir_endereco(self, matricula, tipo, logradouro, municipio, CEP, bairro):
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Endereco(usu_matricula, tipo, logradouro, municipio, CEP, bairro)
            VALUES (%s, %s, %s, %s, %s, %s)""", [matricula, tipo, logradouro, municipio, CEP, bairro])



# 
#   Models
#



class Sistema(FpcModel):
    class Meta:
        db_table = 'Sistema'
        
  
    cod_sistema = FpcIntegerField('Código', primary_key=True, auto_increment=True, editable=False, insertable=False, size=120)
    nome = FpcTextField('Nome', max_length=70, null=False, blank=False, unique=True, size=300, caixa_alta=False)
    sigla = FpcTextField("Sigla", max_length=3)
    


class Departamento(FpcModel):
    class Meta:
        db_table = 'Departamento'
  
    cod_departamento = FpcIntegerField('Código', primary_key=True, db_column="cod_departamento", auto_increment=True, editable=False, insertable=False, size=120)
    denominacao = FpcTextField('Denominação', max_length=100, null=False, blank=False, unique=True, size=300, caixa_alta=False)



class Usuario(FpcModel):
    matricula = FpcIntegerField('Matrícula', db_column="usu_matricula", primary_key=True, auto_increment=True, editable=False, insertable=False, size=120)
    nome = FpcTextField('Nome', max_length=70, null=False, blank=False, unique=True, size=300, caixa_alta=False)
    dt_cadastro = models.DateField("Data Cadastro", auto_now=True)
    login = FpcTextField('Login', max_length=10, null=False, blank=False, caixa_alta=False)
    senha = FpcTextField('Senha', max_length=10, null=False, blank=False, caixa_alta=False, mascara_placeholder="*")
    departamento = models.ForeignKey('Departamento', verbose_name="Departamento", db_column="cod_departamento", null=True, blank=True)
    telefone = FpcTextField("Telefone", blank=True, null=True, subtipo="telefone", max_length=14)
    celular = FpcTextField("Celular", blank=True, null=True, subtipo="telefone", max_length=14)
    
    objects = UsuarioDao()
    
    @classmethod
    def config_backend(self, user):
        return auth.authenticate(username=user.username, password="960101")
    
    
class Telefone(FpcModel):
    class Meta:
        db_table = 'Telefone'

    matricula = FpcIntegerField('Matrícula', primary_key=True)    
    DDD = FpcIntegerField("DDD")
    numero = FpcTextField('Número', max_length=10)
    
    objects = TelefoneUsuarioDao() 
    
    
    
TIPO_ENDERECO = (
    ("R", "Residencial"),
    ("C", "Comercial"),
    ("X", "Cobrança")
)    


class Endereco(FpcModel):
    class Meta:
        db_table = 'Endereco'

    usu_matricula = FpcIntegerField('Matrícula', primary_key=True)
    tipo = FpcTextField("Tipo", max_length=1, size=160, null=False, blank=False, choices=TIPO_ENDERECO, default="R")     
    logradouro = FpcTextField('Logradouro', max_length=100)
    municipio = FpcTextField('Município', max_length=45)
    CEP = FpcTextField('CEP', max_length=9)
    bairro = FpcTextField('Bairro', max_length=45)  
    
    objects = EnderecoUsuarioDao() 
    
    

    
            
            
