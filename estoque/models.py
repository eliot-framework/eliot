# -*- coding: UTF-8 -*-

from django.db import models

from fpc.models import FpcModel, FpcTextField, FpcDecimalField, FpcIntegerField


class GrupoProduto(FpcModel):
    codigo = FpcIntegerField('Código', primary_key=True, auto_increment=True, editable=False, insertable=True, size=120)
    nome = FpcTextField('Nome', max_length=70, null=False, blank=False, unique=True, size=300, caixa_alta=False)

    
class SubgrupoProduto(FpcModel):
    codigo = FpcIntegerField('Código', primary_key=True, auto_increment=True, editable=False, insertable=True, size=120)
    nome = FpcTextField('Nome', max_length=70, null=False, blank=False, unique=True, size=300, caixa_alta=False)

def codbarraValidator(value):
    pass


class ProdutoComposicao(FpcModel):
    codigo = FpcIntegerField('Código', primary_key=True, auto_increment=True, editable=False, insertable=True, size=120)
    nome = FpcTextField('Nome', max_length=70, null=False, blank=False, unique=True, size=300, caixa_alta=False)
    unidade = FpcTextField("Unidade", max_length=3, blank=False)
    produto = models.ForeignKey('Produto', blank=False)
    quantidade = FpcDecimalField("Quantidade", blank=False, default=0, max_digits=10, decimal_places=4)


TIPO_PRODUTO = (
    ("P", "Produto"),
    ("M", "Matéria Prima"),
    ("S", "Serviços")
)

class Produto(FpcModel):
    codigo = FpcIntegerField('Código', primary_key=True, auto_increment=True, editable=False, insertable=True, size=120)
    nome = FpcTextField('Nome', max_length=70, null=False, blank=False, unique=True, size=300, caixa_alta=False)
    codigoEstruturado = models.IntegerField('Cód. Estruturado', null=True, blank=True, unique=True)
    cod_barra = FpcTextField('Cód. Barra', max_length=13, null=True, blank=False, unique=True, size=110, validators=[codbarraValidator])
    descricao = FpcTextField('Descrição', max_length=80, null=True, blank=False, caixa_alta=False, unique=True)
    grupo = models.ForeignKey('GrupoProduto', verbose_name="Grupo", null=True, blank=True)
    subgrupo = models.ForeignKey('SubgrupoProduto', verbose_name="Subgrupo", null=True, blank=True)
    dataValidade = models.DateField("Data Validade", null=True, blank=True)
    precoCusto =  FpcDecimalField("Preço Custo", null=False, blank=False, default=0, max_digits=10, decimal_places=2, onchange=True)
    lucroBruto = FpcDecimalField("Lucro Bruto", null=False, blank=False, default=0, max_digits=10, decimal_places=4, onchange=True)
    lucroLiquido = FpcDecimalField("Lucro Líquido", null=False, blank=False, default=0, max_digits=10, decimal_places=4, editable=False, insertable=False)
    precoVenda =  FpcDecimalField("Preço Venda", null=False, blank=False, default=0, max_digits=10, decimal_places=2, onchange=True)
    sigla = FpcTextField("Sigla", mascara="***", mascara_placeholder=" ", null=True, blank=True, max_length=3, size=80)
    tipo = FpcTextField("Tipo", max_length=1, size=160, null=False, blank=False, choices=TIPO_PRODUTO, default="P", onchange=True)

    
    
    def onChange(self, field_name):
        
        # Calculo do preço de venda
        if field_name == "precoCusto":
            self.precoVenda = self.precoCusto + (self.precoCusto * self.lucroBruto / 100)
        elif field_name == "lucroBruto":
            self.precoVenda = self.precoCusto + (self.precoCusto * self.lucroBruto / 100)
        elif field_name == "precoVenda":
            if self.precoVenda == 0:
                self.lucroBruto = 0
            else:
                self.lucroBruto = (self.precoVenda - self.precoCusto) * 100 / self.precoCusto 

        
        
            

class Aliquota(FpcModel):
    pass

class ICMS(FpcModel):
    pass

class PIS_COFINS(FpcModel):
    pass

class Pessoa(FpcModel):
    CpfCnpj = FpcTextField("CPF/CNPJ", max_length=18, null=True, blank=True)
    
    
    
