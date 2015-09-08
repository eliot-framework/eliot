#!/usr/bin/python
# -*- coding: utf-8 -*-

from sae.models import *
from fpc.forms import *

# CRUDS....

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


# Consultas / Relatórios

class ImprimeAgendamentoForm(FpcForm):
    class Meta:
        model = ImprimeAgendamento
        template = 'imprime_agendamento.html'
        titulo = 'Imprime Agendamento'
        layout = ('semestreAno', 'aluno_id', 'opcao')


