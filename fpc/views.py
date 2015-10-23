# -*- coding: utf-8 -*-

from adm.models import Usuario
import copy
import datetime
import decimal
from django.contrib import auth
from django.contrib.auth import logout
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.query import QuerySet, ValuesQuerySet, ValuesListQuerySet
from django.db.utils import DatabaseError, IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from eliot import settings
from fpc.forms import AutenticarForm, FpcOperacaoForm, FpcForm
from fpc.models import Fpc, Transacao, FpcValidation, FpcModel, EmsModel, \
    EmsException
from fpc.services import FpcService
from fpc.utils import FpcCache
from functools import reduce
import importlib
from io import StringIO
import json
import operator
from urllib.parse import unquote


def json_encode(obj):
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
        return obj.strftime("%d/%m/%Y")
    if isinstance(obj, FpcModel):
        return obj.get_values_flat()
    raise TypeError(repr(obj) + " is not JSON serializable")


class FpcJsonMessage(HttpResponse):
    def __init__(self, *args):
        # message, tipo="info", params = {}
        if len(args) >= 2:
            message = args[0]
            if isinstance(message, EmsException):
                response_json = message
            else:
                if isinstance(message, FpcValidation): 
                    message = {"errors" : message.errors,
                                "warnings" : message.warnings,
                                "infos" :  message.infos}
                 
                    message_json = message.msg_json
                else:
                    message_json = json.dumps(message)
                tipo = args[1]
                if len(args) == 3:
                    params = args[2]
                    params_json = json.dumps(params, default=json_encode)
                    response_json = '{"message":%s,"tipo":"%s", "params":[%s]}' % (message_json, tipo, params_json)
                else:
                    response_json = '{"message":%s,"tipo":"%s"}' % (message_json, tipo) 
        # obj
        elif len(args) == 1:
            value = args[0]
            if isinstance(value, FpcModel):
                obj = value
                response_json = json.dumps(obj.get_values_flat())
            elif isinstance(value, QuerySet):
                lista = list(value)
                response_json = json.dumps(lista, default=json_encode)
            elif isinstance(value, list) or isinstance(value, tuple):
                lista = value
                response_json = json.dumps(lista, default=json_encode)
            else:
                response_json = json.dumps(value, default=json_encode)
        else:
            response_json = ""
        super(FpcJsonMessage, self).__init__(content=response_json, content_type="application/json")


__ts_cache = FpcCache()
def fpc_request(view_func):
    def _wrapped_view_func(request, *args, **kwargs): 
        if not request.user.is_authenticated(): 
            return fpc_autenticar(request)
        Fpc.setCurrentUser(request.user)
        if "ts" in request.GET:
            ts_id = request.GET['ts']
            ts = __ts_cache.get(ts_id)
            if ts == None:
                request.ts = Transacao.objects.get(id=ts_id)
                __ts_cache.set(ts_id, request.ts)
            else:
                request.ts = ts
        try:
            response = view_func(request, *args, **kwargs)
        except FpcValidation as e:
            response = FpcJsonMessage(e, "erro")
        except ValidationError as e:
            response = FpcJsonMessage(e.message, "erro")
        except IntegrityError as e:
            response = FpcJsonMessage("Atenção: %s" % e.args[0], "erro")
        except DatabaseError as e:
            response = FpcJsonMessage("Database erro: %s" % e.args[0], "erro")
        except Exception as e:
            response = FpcJsonMessage("Erro: %s" % e.args[0], "erro")
        return response
    return _wrapped_view_func


@fpc_request
def fpc_sobre(request):
    request.ts = Transacao.objects.get(transacao_url="/fpc.views.fpc_sobre")
    form = FpcForm.get_form(request)
    template = form.createTemplate()
    response = HttpResponse(template)
    return response


def fpc_autenticar(request):
    request.ts = Transacao.objects.get(transacao_url="/fpc.views.fpc_autenticar")
    form = FpcForm.get_form(request)
    template = form.createTemplate()
    response = HttpResponse(template)
    return response

    
def fpc_login(request):
    request.ts = Transacao.objects.get(transacao_url="/fpc.views.fpc_autenticar")
    user = None
    try:
        username = request.POST["username"]
        password = request.POST["password"]
        if username != "" and password != "":
            #user = Usuario.objects.autentica(login=username, senha=password)
            user = auth.authenticate(username=username, password=password)
    except Exception:
        pass
        
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            Fpc.getFpc().user = user
            return HttpResponseRedirect("/eliot/index.html")
        else:
            return HttpResponseRedirect("/eliot/erro_autenticar.html")
    else:
        return HttpResponseRedirect("/eliot/erro_autenticar.html")
    
    
def fpc_erro_autenticar(request):
    return render(request, "fpc_erro_autenticar.html", {"html5_cache": settings.HTML5_CACHE,
                                                       "fpc" : Fpc.getFpc(),
                                                       "settings" : settings}) 
    

@fpc_request
def fpc_logout(request):
    logout(request)
    return fpc_autenticar(request)    


@fpc_request 
def fpc_exibe_sistema(request):
    return fpc_executa_transacao(request)


@fpc_request
def fpc_exibe_sistemas(request):
    lista_sistemas = Transacao.getListaSistemas()
    return render(request, "fpc_painel.html", {"lista_sistemas" : lista_sistemas})


@fpc_request
def fpc_executa_transacao(request):
    ts = request.ts
    if ts.tipoTransacao == "S":
        form = FpcForm.get_form(request)
        template = form.createTemplate()
        response = HttpResponse(template)
        return response
    elif ts.tipoTransacao == "T":
        form = FpcForm.get_form(request)
        template = form.createTemplate(FpcOperacaoForm.pesquisa)
    elif ts.tipoTransacao == "F": 
        form = FpcForm.get_form(request)
        template = form.createTemplate()
    else:
        return FpcJsonMessage("Tipo de transação inválido", "erro")
    return FpcJsonMessage("", "info", {"template" : template, 
                                       "ts" : ts.pk, 
                                       "tipoTs" : ts.tipoTransacao})

@fpc_request
def fpc_exibe_pesquisa(request):
    ts = request.ts
    form = FpcForm.get_form(request)
    template = form.createTemplate(FpcOperacaoForm.pesquisa)
    return FpcJsonMessage("", "info", {"template" : template, 
                                       "ts" : ts.pk, 
                                       "tipoTs" : ts.tipoTransacao})


@fpc_request
def fpc_consultar(request):
    form = FpcForm.get_form(request)
    template = form.createTemplate(FpcOperacaoForm.consulta)
    return FpcJsonMessage("", "info", {"template" : template, "ts" : request.ts.pk})
    


@fpc_request
def fpc_index(request): 
    lista_sistemas = Transacao.getListaSistemas()
    return render(request, "fpc_index.html", {"html5_cache": settings.HTML5_CACHE,
                                              "user"  : request.user,
                                              "lista_sistemas" : lista_sistemas,
                                              "fpc" : Fpc.getFpc(),
                                              "settings" : settings}) 
 
   
@fpc_request    
def fpc_pesquisar(request):
    form = FpcForm.get_form(request)

    field = None
    filtro = None
    model = None
    if "field" in request.GET:
        field = request.GET["field"][1:-1]
    else:
        filtro = request.GET["filtro"][1:-1]
    filtroIds = request.GET["filtroIds"][1:-1]
    limit_ini = int(request.GET['start']) 
    limit_fim = limit_ini + int(request.GET['length'])
    
    # Obtem o model da pesquisa 
    if field is not None:
        field = getattr(form.model, field)
        model = field.related.model
        nome_model_field = str(model)[8:-2]
        form = FpcForm.create_form(request, nome_model_field, request.ts, request.user)
    else:
        model = form.model 
    
    fields = form.getTuplaCamposGrid()

    # Verificar se deve ordenar os dados
    sort = []
    if 'order[0][column]' in request.GET:
        for i in range(0, len(fields)):
            if 'order[%d][column]' % i in request.GET:  
                if request.GET['order[%d][dir]' % i] == "asc": 
                    sort.append(fields[i])
                    #result = result.order_by(tuplaCamposGrid[i])
                else:
                    sort.append("-" + fields[i])
                    #result = result.order_by("-" + tuplaCamposGrid[i])

    #if model.Meta == EmsModel.Meta:
    result =  model.objects.pesquisar(filtro, fields, limit_ini, limit_fim, sort, filtroIds)
    """else:
        # Verifica os filtros a incluir  
        if filtro != None and len(filtro) > 0: 
            expr = []
            campos = filtro.split(".@.")
            result = None
            for c in campos:
                fname, fvalue = c.split(":") 
                fvalue = unquote(fvalue)
                expr.append(("%s__contains" % fname, fvalue))
            
            q_expr = [Q(x) for x in expr]    
            q_expr = reduce(operator.and_, q_expr)
    
            # Verifica filtro de ids inseridos
            if filtroIds != "":
                listaIds = filtroIds.split(",")
                q_expr2 = Q(("id__in", listaIds))    
                result = model.objects.values_list(*tuplaCamposGrid).filter(q_expr | q_expr2)
            else:
                result = model.objects.values_list(*tuplaCamposGrid).filter(q_expr)
        else:
            result = model.objects.values_list(*tuplaCamposGrid).all()
            
        # Verifica se foi incluído filtro na grid
        if request.GET['search[value]'] != "":
            expr = []
            fvalue = request.GET['search[value]']
            for c in tuplaCamposGrid:
                fname = c
                expr.append(("%s__contains" % fname, fvalue))
            q_expr = [Q(x) for x in expr]    
            result = result.filter(reduce(operator.or_, q_expr))
        
        if result.exists():
            
            # Verificar se deve ordenar os dados
            sort = []
            if 'order[0][column]' in request.GET:
                for i in range(0, len(tuplaCamposGrid)):
                    if 'order[%d][column]' % i in request.GET:  
                        if request.GET['order[%d][dir]' % i] == "asc": 
                            sort.append(tuplaCamposGrid[i])
                            #result = result.order_by(tuplaCamposGrid[i])
                        else:
                            sort.append("-" + tuplaCamposGrid[i])
                            #result = result.order_by("-" + tuplaCamposGrid[i])
            sort = sort.join(",")
           
            result = result[limit_ini:limit_fim]
            qtdRegistros = result.count()
            jstr_row = StringIO()
            jstr_row.write('{"draw": %s,"recordsTotal": "%s","recordsFiltered": "%s","data" : [' % (request.GET['draw'], qtdRegistros, qtdRegistros))
            is_consulta = request.GET["isconsulta"] == 'true'
            for x in range(0, len(result)):
                row = result[x]
                value_cod = row[0]
                if is_consulta:
                    value_desc = row[2]
                    if value_desc == None:
                        value_desc = ""
                    jstr_row.write('["<input type=\'radio\' data-str=\'%s - %s\' name=\'f_id\' value=\'%s\'/>",' % (value_cod, value_desc, value_cod))
                else:
                    jstr_row.write('["<input type=\'radio\' name=\'f_id\' value=\'%s\'/>",' % value_cod)
                for i in range(1, len(tuplaCamposGrid)-1):
                    value_row = row[i]
                    if value_row == None:
                        value_row = ""
                    jstr_row.write('"%s",' % value_row)
                desc_lookup = row[len(tuplaCamposGrid)-1]
                if desc_lookup == None: 
                    desc_lookup = ""
                if x < qtdRegistros-1:
                    jstr_row.write('"%s"],' % desc_lookup)
                else:
                    jstr_row.write('"%s"]]}' % desc_lookup)
            jstr = jstr_row.getvalue()
            jstr_row.close()
        else:
            jstr = '{"draw": %s,"recordsTotal": "0","recordsFiltered": "0","data" : []}' % request.GET['draw']
    """
   
    if isinstance(result, ValuesListQuerySet):
        result = list(result)
        result = json.dumps(result, default=json_encode)
    return HttpResponse(result)


@fpc_request    
def fpc_manter_cadastro(request):    
    obj_id = request.GET["id"]
    ts = request.ts
    form = FpcForm.get_form(request)
    obj = form.model.objects.get(pk=obj_id)
    template = form.createTemplate(FpcOperacaoForm.edicao)
    response = FpcJsonMessage("", "info", {"template" : template, 
                                           "update_values" : obj.get_values(), 
                                           "id" : obj.pk, 
                                           "ts" : ts.pk })
    return response

    

@fpc_request    
def fpc_novo_cadastro(request):    
    ts = request.ts
    form = FpcForm.get_form(request)
    obj = form.model()
    template = form.createTemplate(FpcOperacaoForm.novo)
    response = FpcJsonMessage("", "info", {"template" : template, 
                                           "update_values" : obj.get_values(), 
                                           "ts" : ts.pk})
    return response


@fpc_request    
def fpc_salvar_cadastro(request):
    ts = request.ts
    form = FpcForm.get_form(request)
    model_class = form.model
    obj_id = request.GET["id"]
    obj_json = request.GET["form"]
    is_insert = obj_id == None or obj_id == "" 
    # Validações de segurança da operação
    if is_insert:
        if not form.permiteInclusao:
            return FpcJsonMessage("Você não tem permissão para realizar esta inclusão.", "erro")
    else:
        if not form.permiteEdicao:
            return FpcJsonMessage("Você não tem permissão para realizar esta edição.", "erro")
    
    try:
        if is_insert:
            obj = model_class.objects.insert_json(obj_json)
        else:
            obj = model_class.objects.update_json(int(obj_id), obj_json)
        
        update_values = obj.get_update_values()
        grid_dados = "["
        for fld in form.campos_grid_pesquisa:
            fld_value = obj.get_valor_formatado(fld)
            grid_dados = '%s"%s",' % (grid_dados, fld_value)
        grid_dados = grid_dados[0:-1] + "]"
        response = FpcJsonMessage("Registro salvo com sucesso!", "info", {"update_values" : update_values, 
                                                                          "grid_dados" : grid_dados, 
                                                                          "id" : obj.pk, 
                                                                          "ts" : ts.pk })
    except FpcValidation as e:
        response = FpcJsonMessage(e, "erro")
    except ValidationError as e:
        response = FpcJsonMessage(e.message, "erro")
    except IntegrityError as e:
        response = FpcJsonMessage("Atenção: %s" % e.args[0], "erro")
    except DatabaseError as e:
        response = FpcJsonMessage("Database erro: %s" % e.args[0], "erro")
    except EmsException as e:
        response = FpcJsonMessage(e, "erro")
    except Exception as e:
        response = FpcJsonMessage("Erro: %s" % e.args[0], "erro")
    return response


@fpc_request    
def fpc_exibe_ajax_tab(request):
    try:    
        ts = request.ts
        form = FpcForm.get_form(request)
        vId = request.GET["id_obj"]
        vForm = request.GET["form"]
        obj = form.DeSerializeForm(vId, values=vForm)
        update_values = obj.get_update_values()
        template_or_tab = request.GET["template"]
        operacao = FpcOperacaoForm.asValue(operacao_str = request.GET["operacao"])
        id_tab = request.GET["id_tab"]
        h_tab = request.GET["h_tab"]
        if template_or_tab[0:4] == "tab:":
            template = form.createTemplate(operacao, ajax_tab = template_or_tab[4:])
        elif template_or_tab[0:4] == "url:":
            function_string = template_or_tab[4:]
            mod_name, func_name = function_string.rsplit('.', 1)
            mod = importlib.import_module(mod_name)
            func = getattr(mod, func_name)
            template = func(request)
        else:
            template = render_to_string(template_or_tab,  {'form' : form, "ts" : ts.pk})
        response = FpcJsonMessage("", "info", { "update_values" : update_values, 
                                                        "id" : obj.pk, 
                                                        "ts" : ts.pk, 
                                                        "id_tab" : id_tab,
                                                        "h_tab" : h_tab,
                                                        "template" : template})
        return response
    except ValidationError as e:
        response = FpcJsonMessage(e.message, "erro")
    except DatabaseError as e:
        response = FpcJsonMessage("Database erro: %s" % e.args[0], "erro")
    except Exception as e:
        response = FpcJsonMessage("Erro: %s" % e.args[0], "erro")
    return response

    
@fpc_request    
def fpc_field_onchange(request):
    try:
        ts = request.ts
        form = FpcForm.get_form(request)
        vId = request.GET["id"]
        vForm = request.GET["form"]
        field_name = request.GET["field"] 
        field_id = request.GET["field_id"]
        operacao = request.GET["operacao"]
        obj = form.DeSerializeForm(vId, values=vForm)
        obj_copy = copy.deepcopy(obj)
        obj.onChange(field_name)
        obj.checkUpdateFields(obj_copy)
        update_values = obj.get_update_values()
        response = FpcJsonMessage("", "info", { "update_values" : update_values, 
                                                        "id" : obj.pk, 
                                                        "ts" : ts.pk, 
                                                        "field" : field_name, 
                                                        "field_id" : field_id,
                                                        "operacao" : operacao })
    except ValidationError as e:
        response = FpcJsonMessage(e.message, "erro")
    except DatabaseError as e:
        response = FpcJsonMessage("Database erro: %s" % e.args[0], "erro")
    except Exception as e:
        response = FpcJsonMessage("Erro: %s" % e.args[0], "erro")
    return response


@fpc_request    
def fpc_lazy_field(request):
    try:
        ts = request.ts
        form = FpcForm.get_form(request)
        vId = request.GET["id"]
        vForm = request.GET["form"]
        field_name = request.GET["field"] 
        field_id = request.GET["field_id"]
        operacao = request.GET["operacao"]
        op_form = FpcOperacaoForm.asValue(operacao)
        obj = form.DeSerializeForm(vId, values=vForm)
        form.setObject(obj)
        template = form.createTemplate(op_form, ajax_tab=None, modo_lazy=False, field_id=field_id)
        return FpcJsonMessage("", "info", { "content" : template, 
                                                    "id" : obj.pk, 
                                                    "ts" : ts.pk, 
                                                    "field" : field_name, 
                                                    "field_id" : field_id,
                                                    "operacao" : operacao })
    except ValidationError as e:
        response = FpcJsonMessage(e.message, "erro")
    except DatabaseError as e:
        response = FpcJsonMessage("Database erro: %s" % e.args[0], "erro")
    except Exception as e:
        response = FpcJsonMessage("Erro: %s" % e.args[0], "erro")
    return response

  
def fpc_service_get(request, *args, **kwargs):    
    """ Obtem o objeto pelo seu respectivo id 
        Ex.: eliot/api1/sca/produto/1?fields=(fields)
    """
    try:
        api = kwargs["api"]
        service = FpcService.get_service_by_api(api)
        fields = request.GET["fields"] if "fields" in request.GET else None
        obj_id = kwargs["obj_id"]
        modificador = kwargs["modificador"]
        if modificador == "count" or modificador == "exists":
            result = service.findby('pk', obj_id, op='exact', fields=fields, modificador=modificador)
        elif modificador == "update":
            try:    
                obj = request.GET["obj"]
                obj = json.loads(obj)
            except Exception as e:
                raise ValueError("Objeto inválido ou não informado: ", e.__str__())
            result = service.update(obj_id, obj)
        else:
            try:
                result = service.get(obj_id=obj_id, fields=fields)
            except:
                return FpcJsonMessage({})
        return FpcJsonMessage(result)
    except Exception as e:
        return fpc_service_erro(e)


def fpc_service_all(request, *args, **kwargs):    
    """ Retorna todos os objetos do modelo 
        Ex.: eliot/api1/sca/produto/(count|exists)?fields=(fields)&sort=(campos)&paginador=x,y
    """
    try:
        api = kwargs["api"]
        service = FpcService.get_service_by_api(api)
        fields = request.GET["fields"] if "fields" in request.GET else None
        sort = request.GET["sort"] if "sort" in request.GET else None
        paginador = request.GET["paginador"] if "paginador" in request.GET else None
        is_count = kwargs["count"] == "count"
        if is_count:
            result = service.count()
        else:
            is_exists = kwargs["exists"] == "exists"
            if is_exists:
                result = service.exists()
            else:
                result = service.all(fields, sort, paginador)  
        return FpcJsonMessage(result)
    except Exception as e:
        return fpc_service_erro(e)


def fpc_service_findby(request, *args, **kwargs):    
    """
        Executa o método findby para localizar por field_name
        Ex.: eliot/api1/sca/produto/findbynome1/ERVA MATE/(modificador)?fields=(fields)&sort=(campos)&paginador=x,y
    """    
    try:
        api = kwargs["api"]
        service = FpcService.get_service_by_api(api)
        field_name = kwargs["field"]
        value = kwargs["value"]
        field = service.model.field_by_name_insensitive(field_name)
        value = service.model.text_to_value(field, value)
        op = kwargs["op"]
        op = op[2:] if op != "" else "exact" 
        fields = request.GET["fields"] if "fields" in request.GET else None
        sort = request.GET["sort"] if "sort" in request.GET else None
        paginador = request.GET["paginador"] if "paginador" in request.GET else None
        if kwargs["count"] == "count":
            modificador = "count"
        elif kwargs["exists"] == "exists":
            modificador = "exists"
        else:
            modificador = None
        result = service.findby(field.name, value, op, fields, sort, paginador, modificador)
        return FpcJsonMessage(result)  
    except Exception as e:
        return fpc_service_erro(e)


def fpc_service_filtro(request, *args, **kwargs):    
    """
        Executa o método filtro
    """    
    try:
        api = kwargs["api"]
        service = FpcService.get_service_by_api(api)
        try:
            q = request.GET["q"]
        except:
            raise ValueError("Parâmetro filtro não informado.")
        try:
            filtro_json = json.loads(q)
        except Exception as e:
            raise ValueError("Filtro inválido: ", e.__str__())
        fields = request.GET["fields"] if "fields" in request.GET else None
        sort = request.GET["sort"] if "sort" in request.GET else None
        paginador = request.GET["paginador"] if "paginador" in request.GET else None
        if kwargs["count"] == "count":
            modificador = "count"
        elif kwargs["exists"] == "exists":
            modificador = "exists"
        else:
            modificador = None
        result = service.filtro(filtro_json, fields, sort, paginador, modificador)
        return FpcJsonMessage(result)
    except Exception as e:
        return fpc_service_erro(e)


def fpc_service_persist(request, *args, **kwargs):    
    """
        Persiste os dados através do método insert ou update
    """    
    try:
        api = kwargs["api"]
        service = FpcService.get_service_by_api(api)
        try:
            obj = request.GET["obj"]
        except:
            raise ValueError("Parâmetro obj não informado.")
        try:
            obj_json = json.loads(obj)
        except Exception as e:
            raise ValueError("Parâmetro obj inválido: ", e.__str__())
        if kwargs["persist"] == "insert":
            service.insert(obj_json)
        else:
            service.update(obj_json)
        return FpcJsonMessage(True)
    except Exception as e:
        return fpc_service_erro(e)


def fpc_service_metodo(request, *args, **kwargs):
    """
        Executa um método na classe service.
    """    
    try:
        api = kwargs["api"]
        service = FpcService.get_service_by_api(api)
        nome_metodo = kwargs["metodo"]
        metodo = getattr(service, nome_metodo)
        if callable(metodo) and not nome_metodo.startswith("_") and hasattr(metodo, 'fpc_public'):
            if len(request.GET) > 0:
                params = dict(zip(request.GET.keys(), request.GET.values()))
                result = metodo(**params)
            else:
                result = metodo()
            return FpcJsonMessage(result)
        else:
            raise Exception("Método %s não existe.'" % nome_metodo)
    except Exception as e:
        return fpc_service_erro(e)


def fpc_service_erro(e):  
    return FpcJsonMessage(e.__str__(), "error")        
            
    
    
    
        
    