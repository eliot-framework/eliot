# -*- coding: utf-8 -*-

from datetime import datetime
from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from fpc.models import Transacao
import gzip
from http.client import HTTPConnection  
import os
import shutil
import sys
from urllib.parse import urlencode


class EliotConfig(AppConfig):
    name = 'eliot'
    label = "Eliot"
    verbose_name = "Eliot"
    
    def ready(self):
        
        print("Iniciando deploy do Eliot, aguarde...")
        print("Linha de comando: %s" % sys.argv)
         
        # As inicializações a seguir só devem ocorrer em deploy  
        if not ("syncdb" in sys.argv or "evolve" in sys.argv) :
        
            """
                Cadastra o objeto Fpc para armazenar configurações no banco
            """
            from fpc import utils
            from fpc.models import Fpc

            fpc = None
            try:
                fpc = Fpc.getFpc()
            except DatabaseError:
                exit
            except ObjectDoesNotExist:
                print("Cadastra configuração padrão.")
                fpc = Fpc()
                fpc.save()
            
            
            """
                Cadastra as funcionalidades fixas do framework
            """
            print("Cadastrando funcionalidades fixas do framework.")
            self.cadastra_transacoes()
            
            
            
            """
                Cadastra a permissão view para todas as classes novas
            """
            
            print("Cadastrando permissão view para todos os modelos.")
            
            for classe in ContentType.objects.filter(app_label__in=["adm"]):
                nome_perm = "view_" + classe.model
                if not Permission.objects.filter(content_type_id=classe.id, codename=nome_perm).exists():
                    permissao = Permission(name="Permite visualizar", content_type_id=classe.id, codename=nome_perm)
                    permissao.save()
            
             
            """
                ************* Geração dos arquivos js e css compactados da aplicação ***********************
            """
            
            static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static/")
            js_path = "%sjs%s" % (static_path, os.sep)
            css_path = "%scss%s" % (static_path, os.sep)
            css_concat_path = "%sfpc_concat.css" % css_path
            js_concat_path = "%sfpc_concat.js" % js_path
            css_concat_gz_path = "%sfpc_concat.css.gz" % css_path
            js_concat_gz_path = "%sfpc_concat.js.gz" % js_path
            manifest_file = "%sfpc.manifest" % static_path
            css_file = static_path + "css%sfpc.css" % (os.sep)
            css_file_dinamico = static_path + "css%sfpc_dinamico.css" % (os.sep)
            
            
            """
                Processando parâmetros css dinâmicos
            """
            css_params = [{ "nome" : "{{ fpc.%s }}" % field.name, "value" : getattr(fpc, field.name)} for field in fpc._meta.fields if field.name.startswith("css_")] 
            with open(css_file,'r') as f:
                linhas_css_file = []
                for line in f.readlines():
                    for p in css_params:
                        line = line.replace(p["nome"], p["value"])
                    linhas_css_file.append(line)
            with open(css_file_dinamico, 'w') as f:
                for line in linhas_css_file:
                    f.write(line)
            
            
            """
                Gera o arquivo fpc_concat.css
            """
            
            print("Criando arquivo %s." % css_concat_gz_path)
            
            # lista de arquivos css para concatenar
            css_files_para_concat = (static_path + "js%sbootstrap%scss%sbootstrap.min.css" % (os.sep, os.sep, os.sep),
                                     static_path + "js%sbootstrap%scss%sbootstrap-docs.min.css" % (os.sep, os.sep, os.sep),
                                     static_path + "js%sDT_bootstrap%sDT_bootstrap.css" % (os.sep, os.sep),
                                     static_path + "js%sbootstrap-datetimepicker%scss%sbootstrap-datetimepicker.min.css" % (os.sep, os.sep, os.sep),
                                     static_path + "js%sDataTables%smedia%scss%sjquery.dataTables.css" % (os.sep, os.sep, os.sep, os.sep),
                                     static_path + "css%sfpc_img.css" % (os.sep),
                                     static_path + "css%sfpc_dinamico.css" % (os.sep)
                                     #static_path + "font-awesome%scss%sfont-awesome.min.css" % (os.sep, os.sep)
                                     )
            #print("Arquivos css: ", css_files_para_concat)
            
            # Concatena cada arquivo no arquivo fpc_concat.css
            css_concat_file = open(css_concat_path, 'w')
            for filename in css_files_para_concat:
                shutil.copyfileobj(open(filename, 'r'), css_concat_file)
            css_concat_file.close()
            
            
            # Utiliza o cssminifier para otimizar o css
            if settings.USE_CSSMINIFIER:
                with open(css_concat_path, 'rb') as f_in:
                    params = urlencode([
                        ('input', f_in.read() ),
                      ])
                
                
                headers = { "Content-type": "application/x-www-form-urlencoded" }
                conn = HTTPConnection('cssminifier.com')
                conn.request('POST', '/raw', params, headers)
                response = conn.getresponse()
                css_compilado = response.read()
                conn.close()
                with open(css_concat_path, 'wb') as f_out:
                    f_out.write(css_compilado)
            
            
            # Compacta o arquivo css para gzip
            utils.fpcDeleteFileSeguro(css_concat_gz_path)
            if settings.USE_GZIP:
                f_in = open(css_concat_path, 'rb')
                f_out = gzip.open(css_concat_gz_path, 'wb')
                f_out.writelines(f_in)
                f_out.close()
                f_in.close()
            
            
            # Gera o manifesto de cache do HTML5
            utils.fpcDeleteFileSeguro(manifest_file)
            if settings.HTML5_CACHE:
                with open(manifest_file, "w") as f_in_manifest:
                    manifest_str = ["CACHE MANIFEST\n",
                                    "#%s\n" % str(datetime.today()),
                                    "CACHE:\n",
                                    "/eliot/static/img/fpc/fpc_img.png\n", 
                                    "/eliot/static/js/fpc_concat.js\n",
                                    "/eliot/static/css/fpc_concat.css\n",
                                    "/eliot/static/css/bootstrap.css.map\n",
                                    "/eliot/static/fonts/glyphicons-halflings-regular.woff\n",
                                    "/eliot/static/images/sort_asc.png\n",
                                    "/eliot/static/images/sort_desc.png\n",
                                    "/eliot/static/images/sort_both.png\n",
                                    "/eliot/static/js/jquery/jquery-2.1.3.min.map\n",
                                    "/eliot/static/js/bootstrap/css/bootstrap.css.map\n",
                                    "NETWORK:\n",
                                    "*"]
                    f_in_manifest.writelines(manifest_str)
                
            
            """
                Gera o arquivo fpc_concat.js
            """
            
            print("Criando arquivo %s." % js_concat_gz_path)
            
            # lista de arquivos js para concatenar
            js_files_para_concat = (static_path + "js%sjquery%sjquery-2.1.3.min.js" % (os.sep, os.sep),
                                    static_path + "js%sjquery.maskedinput.min.js" % (os.sep),
                                    static_path + "js%sbootstrap%sjs%sbootstrap.min.js" % (os.sep, os.sep, os.sep),
                                    static_path + "js%sbootstrap-datetimepicker%sjs%sbootstrap-datetimepicker.min.js" % (os.sep, os.sep, os.sep),
                                    static_path + "js%sbootstrap-datetimepicker%sjs%slocales%sbootstrap-datetimepicker.pt-BR.js" % (os.sep, os.sep, os.sep, os.sep),
                                    static_path + "js%sDataTables%smedia%sjs%sjquery.dataTables.min.js" % (os.sep, os.sep, os.sep, os.sep),
                                    static_path + "js%sDT_bootstrap%sDT_bootstrap.js" % (os.sep, os.sep),
                                    static_path + "js%sfpc.js" % (os.sep))
            #print("Arquivos js fixos do header: ", js_files_para_concat)
            
            # Gera a lista dos js dos módulos
            js_modulos = []
            for m in settings.STATIC_SCRIPTS: 
                js_modulos.append(m),                           
            

            # Concatena cada arquivo no arquivo fpc_concat.js
            js_concat_file = open(js_concat_path, 'w')
            for filename in js_files_para_concat:
                try:
                    shutil.copyfileobj(open(filename, 'r'), js_concat_file)
                except:
                    print("Atenção: Falha ao acessar aquivo %s." % filename)
            for filename in js_modulos:
                try:
                    shutil.copyfileobj(open(filename, 'r'), js_concat_file)
                except:
                    print("Atenção: Falha ao acessar aquivo %s." % filename)
            js_concat_file.close()
            
            
            
            # Utiliza o compilador closure para otimizar o javascript
            if settings.USE_CLOSURE_COMPILE:
                with open(js_concat_path, 'rb') as f_in:
                    js_code = f_in.read()
                    params = urlencode([
                        ('js_code', js_code ),
                        ('compilation_level', 'SIMPLE_OPTIMIZATIONS'),  #WHITESPACE_ONLY
                        ('output_format', 'text'),
                        ('output_info', 'compiled_code'),
                      ])
                
                headers = { "Content-type": "application/x-www-form-urlencoded" }
                conn = HTTPConnection('closure-compiler.appspot.com')
                conn.request('POST', '/compile', params, headers)
                response = conn.getresponse()
                js_compilado = response.read()
                conn.close()
                with open(js_concat_path, 'wb') as f_out:
                    f_out.write(js_compilado)
                
            
            
            # Compacta o arquivo js para gzip
            utils.fpcDeleteFileSeguro(js_concat_gz_path)
            if settings.USE_GZIP:
                f_in = open(js_concat_path, 'rb')
                f_out = gzip.open(js_concat_gz_path, 'wb')
                f_out.writelines(f_in)
                f_out.close()
                f_in.close()        
                
            
            
            """
                ************* Fim da geração dos arquivos js e css compactados da aplicação ***********************
            """
            

            
    @classmethod
    def cadastra_transacoes(cls):
        
        # Autenticar
        ts = Transacao()
        ts.nome = 'Autenticar'
        ts.titulo = 'Autenticar'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_autenticar'
        ts.posicao = 1
        ts.formModel = 'fpc.forms.AutenticarForm'
        ts.model = 'fpc.models.User'
        try:
            ts.save()
        except:
            pass
        
        
        # Sobre
        ts = Transacao()
        ts.nome = 'Sobre'
        ts.titulo = 'Sobre'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_sobre'
        ts.posicao = 1
        ts.formModel = 'fpc.forms.SobreForm'
        ts.model = 'fpc.models.User'
        try:
            ts.save()
        except:
            pass;
        
        
        ###################################### Módulo de administração ######################################

        # Módulo de administração
        ts_adm = Transacao.objects.get_or_new(nome='ts_adm')
        ts_adm.nome = 'ts_adm'
        ts_adm.titulo = 'Módulo de Administração'
        ts_adm.tipoTransacao = 'S'
        ts_adm.posicao = 1
        ts_adm.image_url = 'class glyphicon glyphicon-book'
        ts_adm.formModel = 'fpc.forms.SistemaForm'
        try:
            ts_adm.save()
        except:
            pass
        
         
        # opção gerenciamento de usuários
        ts_gerencia_usuario = Transacao.objects.get_or_new(nome='ts_gerencia_usuario')
        ts_gerencia_usuario.nome = 'ts_gerencia_usuario'
        ts_gerencia_usuario.titulo = 'Gerenciamento de Usuários'
        ts_gerencia_usuario.tipoTransacao = 'F'
        ts_gerencia_usuario.posicao = 1
        ts_gerencia_usuario.formModel = 'fpc.forms.PainelForm'
        ts_gerencia_usuario.image_url = 'class glyphicon glyphicon-list-alt'
        ts_gerencia_usuario.transacaoPai_id = ts_adm.id
        try:
            ts_gerencia_usuario.save()
        except:
            pass
         

        # opção gerenciamento de interface com o usuário
        ts_gerencia_ui = Transacao.objects.get_or_new(nome='ts_gerencia_ui')
        ts_gerencia_ui.nome = 'ts_gerencia_ui'
        ts_gerencia_ui.titulo = 'Gerenciamento das Configurações do Framework'
        ts_gerencia_ui.tipoTransacao = 'F'
        ts_gerencia_ui.posicao = 2
        ts_gerencia_ui.formModel = 'fpc.forms.PainelForm'
        ts_gerencia_ui.image_url = 'class glyphicon glyphicon-list-alt'
        ts_gerencia_ui.transacaoPai_id = ts_adm.id
        try:
            ts_gerencia_ui.save()
        except:
            ts_gerencia_ui = Transacao.objects.get(nome='ts_gerencia_ui')


        # cadastro de departamentos
        ts = Transacao.objects.get_or_new(nome='ts_cad_departamento')
        ts.nome = 'ts_cad_departamento'
        ts.titulo = 'Cadastro de Departamentos'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 1
        ts.formModel = 'adm.forms.DepartamentoForm'
        ts.model = 'adm.models.Departamento'
        ts.image_url = 'class glyphicon glyphicon glyphicon-tree-deciduous'
        ts.transacaoPai_id = ts_gerencia_usuario.id
        try:
            ts.save()
        except:
            pass;

         

        # menu cadastro de usuários
        ts = Transacao.objects.get_or_new(nome='ts_cad_usuario')
        ts.nome = 'ts_cad_usuario'
        ts.titulo = 'Cadastro de Usuários'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 2
        ts.formModel = 'adm.forms.UsuarioForm'
        ts.model = 'adm.models.Usuario'
        ts.image_url = 'class glyphicon glyphicon glyphicon glyphicon-user'
        ts.transacaoPai_id = ts_gerencia_usuario.id
        try:
            ts.save()
        except:
            pass;


        # menu personalizar tela principal
        ts = Transacao.objects.get_or_new(nome='ts_config_fpc')
        ts.nome = 'ts_config_fpc'
        ts.titulo = 'Personalizar Framework'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/adm.views.personalizar_framework'
        ts.posicao = 1
        ts.formModel = 'adm.forms.FpcConfigForm'
        ts.model = 'fpc.models.Fpc'
        ts.image_url = 'class glyphicon glyphicon glyphicon glyphicon-user'
        ts.transacaoPai_id = ts_adm.id
        try:
            ts.save()
        except:
            pass;


        # cadastro de sistemas
        ts = Transacao.objects.get_or_new(nome='ts_cad_sistema')
        ts.nome = 'ts_cad_sistema'
        ts.titulo = 'Cadastro de Sistemas'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 3
        ts.formModel = 'adm.forms.SistemaForm'
        ts.model = 'adm.models.Sistema'
        ts.image_url = 'class glyphicon glyphicon glyphicon-asterisk'
        ts.transacaoPai_id = ts_adm.id
        try:
            ts.save()
        except:
            pass;


        ###################################### Módulo Estoque ######################################

        # Sistema Estoque
        ts = Transacao()
        ts.nome = 'mod_estoque'
        ts.titulo = 'Estoque'
        ts.tipoTransacao = 'S'
        ts.posicao = 2
        ts.image_url = 'class glyphicon glyphicon-folder-close'
        ts.formModel = 'fpc.forms.SistemaForm'
        try:
            ts.save()
        except:
            pass;


        # menu Estoque
        ts = Transacao()
        ts.nome = 'cad_estoque'
        ts.titulo = 'Cadastro'
        ts.tipoTransacao = 'F'
        ts.posicao = 1
        ts.formModel = 'fpc.forms.PainelForm'
        ts.image_url = 'class glyphicon glyphicon-list-alt'
        ts.transacaoPai = Transacao.objects.get(nome='mod_estoque')
        try:
            ts.save()
        except:
            pass;


        # menu Cadastro de grupo 
        ts = Transacao()
        ts.nome = 'cad_grupo'
        ts.titulo = 'Cadastro de Grupos'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 1
        ts.formModel = 'estoque.forms.GrupoProdutoForm'
        ts.model = 'estoque.models.GrupoProduto'
        ts.image_url = 'class glyphicon glyphicon glyphicon-asterisk'
        ts.transacaoPai = Transacao.objects.get(nome='cad_estoque')
        try:
            ts.save()
        except:
            pass;


        # menu Cadastro de subgrupo 
        ts = Transacao()
        ts.nome = 'cad_subgrupo'
        ts.titulo = 'Cadastro de Subgrupos'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 1
        ts.formModel = 'estoque.forms.SubgrupoProdutoForm'
        ts.model = 'estoque.models.SubgrupoProduto'
        ts.image_url = 'class glyphicon glyphicon glyphicon-asterisk'
        ts.transacaoPai = Transacao.objects.get(nome='cad_estoque')
        try:
            ts.save()
        except:
            pass;


        # menu Cadastro de produto 
        ts = Transacao()
        ts.nome = 'cad_produto'
        ts.titulo = 'Cadastro de Produtos'
        ts.tipoTransacao = 'T'
        ts.transacao_url = '/fpc.views.fpc_exibe_pesquisa'
        ts.posicao = 1
        ts.formModel = 'estoque.forms.ProdutoForm'
        ts.model = 'estoque.models.Produto'
        ts.image_url = 'class glyphicon glyphicon glyphicon-asterisk'
        ts.transacaoPai = Transacao.objects.get(nome='cad_estoque')
        try:
            ts.save()
        except:
            pass;
    
    
    
