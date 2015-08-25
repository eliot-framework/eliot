from django.contrib import admin

from fpc.models import Fpc, Transacao


class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'titulo', 'posicao')
    ordering = ['transacaoPai', 'posicao']


admin.site.register(Fpc)
admin.site.register(Transacao, TransacaoAdmin)






