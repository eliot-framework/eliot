#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models

from fpc.models import FpcModel, FpcTextField, FpcDecimalField, \
    FpcIntegerField, EmsModel


BOOLEAN = ((0, "Não"), (1, 'Sim'))

TIPO_GERA_ARQUIVO_RU = ((0, "Restaurante Universitário"), (1,
                        "Todos os Estudos Concluídos"), (2,
                        'Todos os Estudos de Baixa Renda'), (3,
                        "Participantes do Auxílio Alimentação"))


# CRUDS

class ValeAlimentacao(FpcModel):

    id = FpcIntegerField('Código', primary_key=True, auto_increment=True, editable=False, insertable=False, size=120)
    campus = FpcIntegerField('Campus', null=False, blank=False)
    inicioVigencia = models.DateField("Início Vigência", null=True, blank=True)
    fimVigencia = models.DateField("Fim Vigência?", null=True, blank=True)
    pagaBeneficio = FpcIntegerField("Paga Benefício?", size=160, null=False, blank=False, choices=BOOLEAN, default=0)
    geraArquivoRU = FpcIntegerField(
        'Gerar Arquivo RU', size=160, null=False, blank=False, choices=BOOLEAN, default=1)
    valorBeneficio = FpcDecimalField("Valor do Benefício", null=False, blank=False, default=0, max_digits=10, decimal_places=2)


class Ocorrencias(EmsModel):

    id = FpcIntegerField('Código', primary_key=True, auto_increment=True, editable=False, insertable=False, size=120)
    aluno_id = FpcIntegerField('Aluno', null=False, blank=False)
    semestreAno = FpcIntegerField('Semestre/Ano', null=True, blank=True)
    dataInicio = models.DateField("Data Início", null=True, blank=True)
    dataFim = models.DateField('Data Fim', null=True, blank=True)
    texto = FpcTextField('Texto', max_length=4000, null=True, blank=False, caixa_alta=False)
    suspendeBA = FpcIntegerField("Suspende Bolsa de Alimentação", size=160, null=False, blank=False, choices=BOOLEAN, default=0)


class GeraArquivoRU(FpcModel):

    id = FpcIntegerField('Código', primary_key=True, auto_increment=True, editable=False, insertable=False, size=120)
    dataGeracao = models.DateField("Data Geração", null=True, blank=True)
    semestreAno1 = FpcIntegerField('Semestre/Ano(1)', null=True, blank=True)
    semestreAno2 = FpcIntegerField('Semestre/Ano(2)', null=True, blank=True)
    semestreAno3 = FpcIntegerField('Semestre/Ano(3)', null=True, blank=True)
    semestreAno4 = FpcIntegerField('Semestre/Ano(4)', null=True, blank=True)
    tipo = FpcIntegerField('Tipo de Arquivo', size=225, null=False, blank=False, choices=TIPO_GERA_ARQUIVO_RU, default=0)


# Consultas / Relatórios

OPCAO_IMPRIME_AGENDAMENTO = ((0, 'Pedido Novo'), (1, "Renovação"))


class ImprimeAgendamento(FpcModel):

    id = FpcIntegerField('Código', primary_key=True, auto_increment=True, editable=False, insertable=False, size=120)
    semestreAno = FpcIntegerField('Semestre/Ano', null=True, blank=True)
    aluno_id = FpcIntegerField('Aluno', null=True, blank=True)
    opcao = FpcIntegerField("Opção", size=225, null=False, blank=False, choices=OPCAO_IMPRIME_AGENDAMENTO, default=0)

