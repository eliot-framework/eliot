#!/usr/bin/python
# -*- coding: utf-8 -*-

from sae.models import *
from fpc.forms import *

# Cadastros básicos

class ValeAlimentacaoForm(FpcCrud):
    class Meta:
        model = ValeAlimentacao
        campos_pesquisa = ('id','campus', 'inicioVigencia', 'fimVigencia','pagaBeneficio')
        campos_grid_pesquisa = ('id','campus', 'inicioVigencia', 'fimVigencia','pagaBeneficio')
        layout = ('id', 'campus', 
                  ('inicioVigencia', 'fimVigencia'),
                  'valorBeneficio', 
                  'pagaBeneficio', 
                  "ocorrencia")
        layout_pesquisa = ('id','campus','inicioVigencia','fimVigencia','pagaBeneficio')
        titulo = "Auxílio Alimentação"


class OcorrenciasForm(FpcCrud):
    class Meta:
        model = Ocorrencias
        campos_pesquisa = ('aluno_id', 'semestreAno', 'dataInicio',
                           'dataFim', 'suspendeBA')
        campos_grid_pesquisa = ('aluno_id', 'semestreAno', 'dataInicio'
                                , 'dataFim', 'suspendeBA')
        layout = ('id', 'aluno_id', 'semestreAno', 
                  ('dataInicio','dataFim'), 'suspendeBA'
                )
        layout_pesquisa = ('aluno_id', 'semestreAno', 'dataInicio',
                           'suspendeBA')
        titulo = "Ocorrências"


class GeraArquivoRUForm(FpcCrud):
    class Meta:
        model = GeraArquivoRU
        campos_pesquisa = 'dataGeracao'
        campos_grid_pesquisa = ('dataGeracao', 'semestreAno1',
                                'semestreAno2', 'semestreAno3',
                                'semestreAno4')
        layout = (
            'dataGeracao',
            'semestreAno1',
            'semestreAno2',
            'semestreAno3',
            'semestreAno4',
            'tipo',
            )
        layout_pesquisa = 'dataGeracao'
        titulo = 'Gerar Arquivo RU'



# ########### Estudo socioeconômico # ###########

class EstudoSocioEconomicoForm(FpcForm):
    class Meta:
        titulo = "Estudo Socioeconômico"
        template = 'estudo_socioeconomico.html'

class EstudoSocioEconomicoPreliminarForm(FpcForm):
    class Meta:
        titulo = "Estudo Socioeconômico Preliminar"
        template = 'estudo_socioeconomico_preliminar.html'

class EstudoSocioEconomicoDadosPessoaisForm(FpcForm):
    class Meta:
        titulo = "Estudo Socioeconômico"
        template = 'estudo_socioeconomico_dadospessoais.html'

class EstudoSocioEconomicoDadosFamiliaresForm(FpcForm):
    class Meta:
        titulo = "Estudo Socioeconômico"
        template = 'estudo_socioeconomico_dadosfamiliares.html'

class EstudoSocioEconomicoBensForm(FpcForm):
    class Meta:
        titulo = "Estudo Socioeconômico"
        template = 'estudo_socioeconomico_bens.html'

class ImprimeEstudoSocioEconomicoForm(FpcForm):
    class Meta:
        titulo = "Imprimir Estudo Estudo Socioeconômico"
        template = 'imprime_estudo_socioeconomico.html'


class InfoEstudoSocioEconomicoForm(FpcForm):
    class Meta:
        titulo = "Informações Sobre o Estudo Socioeconômico"
        template = 'info_estudo_socioeconomico.html'


# ########### Consultas / Relatórios ############


class ImprimeAgendamentoForm(FpcForm):
    class Meta:
        model = ImprimeAgendamento
        template = 'imprime_agendamento.html'
        titulo = 'Imprime Agendamento'
        layout = ('semestreAno', 'aluno_id', 'opcao')


