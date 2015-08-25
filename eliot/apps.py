# -*- coding: utf-8 -*-

from datetime import datetime
from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
import gzip
from http.client import HTTPConnection  
import os
import shutil
import sys
from urllib.parse import urlencode

from fpc import utils
from fpc.models import Fpc, Transacao


class EliotConfig(AppConfig):
    name = 'eliot'
    label = "Eliot"
    verbose_name = "Eliot"
    
    def ready(self):
        
        print("Iniciando deploy, aguarde...")
        print("Linha de comando: %s" % sys.argv)
         
        # As inicializações a seguir só devem ocorrer em deploy  
        if not ("syncdb" in sys.argv or "evolve" in sys.argv) :
        
            """
                Cadastra o objeto Fpc para armazenar configurações no banco
            """
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
            Transacao.cadastra_ts_fixa()
            
            
            
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
            
            static_path = os.path.join(settings.SETTINGS_PATH, "static/")
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
            for m in settings.FPC_REGISTER_MODULES: 
                js_modulos.append('%s%s%s%sscripts.js' % (settings.SETTINGS_PATH, os.sep, m, os.sep)),                           
            

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
                    params = urlencode([
                        ('js_code', f_in.read() ),
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
            

            
    
    
    
