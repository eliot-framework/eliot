# -*- coding: UTF-8 -*-

from adm.models import Sistema, Usuario, Telefone, Departamento, Endereco
from fpc.services import FpcService, fpc_public


class ConfigFrameworkService(FpcService):
    pass 


class SistemaService(FpcService):
    class Meta:
        model = Sistema
        


class DepartamentoService(FpcService):
    class Meta:
        model = Departamento



class UsuarioService(FpcService):
    class Meta:
        model = Usuario
        
    @fpc_public
    def lista_historico_acesso(self, matricula : int):
        if type(matricula) == str:
            matricula = int(matricula)
        lista_historico = Usuario.objects.lista_historico_acesso(matricula)
        return lista_historico
    
    @fpc_public    
    def helloWorld(self):
        return "Ola Mundo!!!"
    
    @fpc_public    
    def calculadora(self, valor1 : int, valor2 : int, operacao):
        valor1 = int(valor1)    
        valor2 = int(valor2)
        if operacao == 'soma':
            return valor1 + valor2
        elif operacao == 'subtrai':
            return valor1 - valor2
        else:
            return "Tchê, operação não suportada!!!"

    @fpc_public    
    def autentica(self, login, senha):
        return Usuario.objects.autentica(login, senha)
    
    

class TelefoneUsuarioService(FpcService):
    class Meta:
        model = Telefone
        
        
    def lista_telefone(self, matricula):
        lista_telefones = Telefone.objects.lista_telefone(matricula)
        return lista_telefones
        
        
    def excluir_telefone(self, matricula, numero):
        Telefone.objects.excluir_telefone(matricula, numero)


    def incluir_telefone(self, matricula, ddd, numero):
        # no Django o correto seria passar os objetos mas este trabalho é para demonstrar um DAO com os comandos DML
        # telefone = Telefone()
        # telefone.ddd = xxx
        # telefone.numero = xxxxx-xxxx
        # telefone.matricula = xxxx
        # telefone.save()
        
        Telefone.objects.incluir_telefone(matricula, ddd, numero)
        



class EnderecoUsuarioService(FpcService):
    class Meta:
        model = Endereco
        
        
    def lista_endereco(self, matricula):
        lista_enderecos = Endereco.objects.lista_endereco(matricula)
        return lista_enderecos
        
        
    def excluir_endereco(self, matricula, tipo):
        Endereco.objects.excluir_endereco(matricula, tipo)


    def incluir_endereco(self, matricula, tipo, logradouro, municipio, CEP, bairro):
        Endereco.objects.incluir_endereco(matricula, tipo, logradouro, municipio, CEP, bairro)
        
        
    