# -*- coding: UTF-8 -*-

from estoque.models import Produto, GrupoProduto, SubgrupoProduto
from fpc.services import FpcService, fpc_public


class ProdutoService(FpcService):
    class Meta:
        model = Produto
        
    @fpc_public
    def lista_produtos_negativos(self, sort):
        return self.model.objects.filter(precoVenda__gt=0)


class GrupoService(FpcService):
    class Meta:
        model = GrupoProduto
         

class SubgrupoService(FpcService):
    class Meta:
        model = SubgrupoProduto
        

    def teste(self):
        return True
    
    def processa_arquivo(self):
        pass
        
    