from django.contrib import admin

from estoque.models import Produto, GrupoProduto, SubgrupoProduto, Aliquota, ICMS, PIS_COFINS, \
    ProdutoComposicao


admin.site.register(Produto)
admin.site.register(GrupoProduto)
admin.site.register(SubgrupoProduto)
admin.site.register(Aliquota)
admin.site.register(ICMS)
admin.site.register(PIS_COFINS)
admin.site.register(ProdutoComposicao)


