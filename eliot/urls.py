from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
     url(r'^admin/', include(admin.site.urls)),
     (r'^eliot/index.html', 'fpc.views.fpc_index'),
     (r'^eliot/autenticar.html/$', 'fpc.views.fpc_autenticar'),
     (r'^eliot/erro_autenticar.html/$', 'fpc.views.fpc_erro_autenticar'),
     (r'^eliot/sobre.html/$', 'fpc.views.fpc_sobre'),
     url(r'^eliot/sistema/$', 'fpc.views.fpc_exibe_sistema', name="exibe_sistema"),
     url(r'^fpc.views.fpc_login', 'fpc.views.fpc_login'),
     url(r'^fpc.views.fpc_autenticar', 'fpc.views.fpc_autenticar'),
     url(r'fpc.views.fpc_logout', 'fpc.views.fpc_logout'),
     url(r'^fpc.views.fpc_pesquisar', 'fpc.views.fpc_pesquisar'),
     url(r'^fpc.views.fpc_exibe_sistemas', 'fpc.views.fpc_exibe_sistemas'),
     url(r'^fpc.views.fpc_manter_cadastro', 'fpc.views.fpc_manter_cadastro'),
     url(r'^fpc.views.fpc_novo_cadastro', 'fpc.views.fpc_novo_cadastro'),
     url(r'^fpc.views.fpc_salvar_cadastro', 'fpc.views.fpc_salvar_cadastro'),
     url(r'^fpc.views.fpc_exibe_pesquisa', 'fpc.views.fpc_exibe_pesquisa'),
     url(r'^fpc.views.fpc_executa_transacao', 'fpc.views.fpc_executa_transacao'),
     url(r'fpc.views.fpc_consultar', 'fpc.views.fpc_consultar'),
     url(r'fpc.views.fpc_exibe_ajax_tab', 'fpc.views.fpc_exibe_ajax_tab'),
     url(r'fpc.views.fpc_field_onchange', 'fpc.views.fpc_field_onchange'),
     url(r'fpc.views.fpc_lazy_field', 'fpc.views.fpc_lazy_field'),
     
     # camada de serviço
     
     url(r'^eliot/(?P<api>(api)[0-9]\/[a-zA-Z0-9_\s\+]+\/[a-zA-Z0-9_\s\+]+)/(?P<persist>(insert|update))$', 'fpc.views.fpc_service_persist'),
     url(r'^eliot/(?P<api>(api)[0-9]\/[a-zA-Z0-9_\s\+]+\/[a-zA-Z0-9_\s\+]+)/((all/)*)((?P<count>(count)*)|(?P<exists>(exists)*)|(?P<update>(update)*)|(?P<validate>(validate)*)|(?P<delete>(delete)*))$', 'fpc.views.fpc_service_all'),
     url(r'^eliot/(?P<api>(api)[0-9]\/[a-zA-Z0-9_\s\+]+\/[a-zA-Z0-9_\s\+]+)/(?P<obj_id>[0-9]+)/((?P<modificador>(count|exists|update|delete|validate)*))$', 'fpc.views.fpc_service_get'),
     url(r'^eliot/(?P<api>(api)[0-9]\/[a-zA-Z0-9_\s\+]+\/[a-zA-Z0-9_\s\+]+)/filtro(/*|/((?P<count>(count)*)|(?P<exists>(exists)*)))$', 'fpc.views.fpc_service_filtro'),
     url(r'^eliot/(?P<api>(api)[0-9]\/[a-zA-Z0-9_\s\+]+\/[a-zA-Z0-9_\s\+]+)/findby(?P<field>[a-zA-Z0-9\s\+]+)(?P<op>(__contains|__exact|__gt|__gte|__lt|__lte)*)/(?P<value>[a-zA-Z0-9\s\+]+)/((?P<count>(count)*)|(?P<exists>(exists)*))$', 'fpc.views.fpc_service_findby'),
     url(r'^eliot/(?P<api>(api)[0-9]\/[a-zA-Z0-9_\s\+]+\/[a-zA-Z0-9_\s\+]+)/(?P<metodo>[a-zA-Z][a-zA-Z0-9_]+)$', 'fpc.views.fpc_service_metodo'),
     
     # módulo adm

     url(r'adm.views.usuario_telefone', 'adm.views.usuario_telefone'),
     url(r'adm.views.personalizar_framework', 'adm.views.personalizar_framework'),
     
)

     
    


