# -*- coding: utf-8 -*-

from _io import StringIO
from collections import OrderedDict
import copy
import datetime
from decimal import Decimal
import decimal
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.context_processors import csrf
from django.core.exceptions import ValidationError
from django.db import models
import django.db.models.fields
from django.db.models.query import QuerySet
from django.http import HttpResponse, QueryDict
from django.shortcuts import render
from django.template.context import RequestContext
from django.template.loader import render_to_string
from eliot import settings
from fpc.models import Transacao, FpcTipoField, FpcModel, Fpc, FpcValidation
from fpc.utils import FpcException
import json
from threading import RLock


class FpcCssStyle(object):
    
    def __init__(self):
        self._styles = {}
        self._default_styles = {}
    
    def add_style(self, css_attr, value):
        if not (css_attr in self._default_styles and self._default_styles[css_attr] == value): 
            self._styles[css_attr] = value

    def add_default_style(self, css_attr, value):
        self._default_styles[css_attr] = value
            
    def add_string(self, css_string, replace=True):
        if css_string != "":
            for css in css_string.split(";"):
                if css != None and len(css) > 3 and ":" in css:
                    attr = css.split(":")
                    attr_name = attr[0]
                    attr_val = attr[1]
                    if replace:
                        self.add_style(attr_name, attr_val)
                    else:
                        if not attr_name in self._styles:
                            self.add_style(attr_name, attr_val)

    def get_value(self):
        value = ";".join(["%s:%s" % (css_attr, self._styles.get(css_attr)) for css_attr in self._styles.keys()])
        if value != "":
            return "style='%s'" % value
        else:
            return ""
          


class FpcWidget(object):

    def __init__(self, owner=None, **kargs):
        self.owner = None
        self.form = None
        self.ts_id = None
        
        # tags importantes
        self.id = ""
        self.name = ""
        self.label = ""
        self.value = ""
        self.css = FpcCssStyle()
        self.css.add_default_style("width", "100%")
        self.css_label = FpcCssStyle()
        self.css_label.add_default_style("display", "block")
        self.size = None
    
        # tags acessórias
        self.autofocus = None
        self.title = None
        self.hidden = None
        self.tabindex = None
    
        # events
        self.listener = ""

        self.setOwner(owner)
        if "id" in kargs:
            self.id = kargs["id"]
        if "name" in kargs:
            self.name = kargs["name"]
        if "label" in kargs:
            self.label = kargs["label"]
        if "value" in kargs:
            self.value = kargs["value"]
        if "css" in kargs:
            self.css.add_string(kargs["css"])
        if "css_label" in kargs:
            self.css_label.add_string(kargs["css_label"])
        if "size" in kargs:
            self.size = kargs["size"]
        if "autofocus" in kargs:
            self.autofocus = kargs["autofocus"]
        if "title" in kargs:
            self.title = kargs["title"]
        if "hidden" in kargs:
            self.hidden = kargs["hidden"]
        if "tabindex" in kargs:
            self.tabindex = kargs["tabindex"]
        if "listener" in kargs:
            self.listener = kargs["listener"]



    def getTagListener(self):
        if self.listener != "" and self.listener != None:
            return "data-listener='%s'" % self.listener
        else:
            return ""
       
        
    def getTagAcessorias(self):
        """
            Retorna uma string formatada com as tags acessórias ser incluído nos elementos. 
            Essa implementação padrão possivelmente poderá ser utilizada em todos os widgets descendentes
        """
        result = StringIO()
        if self.autofocus != None:
            result.write("autofocus ")
        if self.title != None:
            result.write("title='%s' " % self.title)
        if self.hidden != None:
            result.write("hidden ")
        if self.tabindex != None:
            result.write("tabindex='%d' " % self.tabindex)
        event_tag = result.getvalue()
        result.close()
        return event_tag
        
        
    def setOwner(self, owner):
        self.owner = owner
        if self.owner != None:
            self.form = self.owner.form
            
            css_label_layout = self.owner.css_label
            if css_label_layout != None and css_label_layout != "": 
                self.css_label.add_string(css_label_layout, replace=False)
            
            css_input_layout = self.owner.css_input
            if css_input_layout != None and css_input_layout != "": 
                self.css_input.add_string(css_input_layout)
            

    def _createTag(self):
        pass
    
    def tag(self):
        return self._createTag()



class FpcButton(FpcWidget):
    
    def __init__(self, owner=None, **kargs):
        self.type = "button"
        FpcWidget.__init__(self, owner, **kargs)
        if "type" in kargs:
            self.type = kargs["type"]
        
    
    def _createTag(self):
        return r'<button id="%s" type="%s" %s %s class="btn btn-default btn-xs">%s</button>' % (self.id, self.type, self.getTagListener(), self.getTagAcessorias(), self.label)
     


class FpcNovaLinha(FpcWidget):
    
    def __init__(self, owner=None, **kargs):
        FpcWidget.__init__(self, owner, **kargs)

        
    def _createTag(self):
        return r'<span class="fpc_nl"></span>'



class FpcGrid(FpcWidget):
    field = None
    lazy = True
    def __init__(self, owner=None, field=None, lazy=True, **kargs):
        self.field, self.lazy = field, lazy
        FpcWidget.__init__(self, owner, **kargs)
    
    def _createTag(self):
        return render_to_string("fpc_grid.html",  {"field" : self, 
                                                   "form" : self.form, 
                                                   "tsowner" : self.owner.form.ts, 
                                                   "ts" : self.form.ts, 
                                                   "lazy" : self.lazy and self.owner.modo_lazy})
    
    
class FpcColumn(FpcWidget):
    def __init__(self, owner=None, **kargs):
        FpcWidget.__init__(self, owner, **kargs)
    
    def _createTag(self):
        return r'<table onpageshow="javascript:alert(\'ok\')"><tr><td>teste</td><td>teste</td><td>teste</td></tr><tr><td>teste</td><td>teste</td><td>teste</td></tr></table>'

    
class FpcField(FpcWidget):

    def __init__(self, owner=None, field=None, **kargs):
        if field != None and not isinstance(field, models.Field):
            raise FpcException("Field não é do tipo correto.")
        self.field = None
        self.key = None
        self.widthGrid = 80
        self.formModelFK = None
        self.tipo = None
        if "mini_button" in kargs:
            self.mini_button = kargs["mini_button"]
        else:
            self.mini_button = False
        if "mini_button_icon" in kargs:
            self.mini_button_icon = kargs["mini_button_icon"]
        else:
            self.mini_button_icon = "glyphicon-search"
        if "type" in kargs:
            self.type = kargs["type"]
        else:
            self.type = "text"
        self.mini_button_onclick = ""
        FpcWidget.__init__(self, owner, **kargs)
        self.setField(field)


    def setField(self, field):
        self.field = field
        if self.field != None:
            if self.name == None or self.name == "":
                self.name = self.field.name
            if self.label == None or self.label == "":
                try:
                    self.label = self.field.verbose_name
                except:
                    self.label = ""
            if self.tipo == None:
                self.tipo = FpcModel.get_tipo_field(self.field)
            if self.size == None and hasattr(self.field, "size"):
                self.size = self.field.size
            self.value = ""

    
    def _createTag(self):
        onchange_tag = ""
        required_tag = ""
        default_tag = ""
        editable_tag = ""
        insertable_tag = ""
        destaca_campo_tag = ""
        lazy_tag = ""
        if hasattr(self.field, "render"): 
            render = self.field.render
        else:
            render = "input"
        iscombobox =  render == "combobox"
        isradio = render == "radio"
        is_model_fpc = issubclass(self.form.model, FpcModel)

        if self.form.destacaCampos and not self.field.blank:
            destaca_campo_tag = "data-destaca"

        if not self.field.blank:
            required_tag = "data-required"
            
        if self.field.default != django.db.models.fields.NOT_PROVIDED and self.field.default != None and is_model_fpc:
            default_tag = 'data-default="%s"' % self.form.model.get_valor_default_formatado(self.field)

        if hasattr(self.field, "onchange") and self.field.onchange:
            onchange_tag = "data-on-change"

        if hasattr(self.field, "editable") and not self.field.editable:
            editable_tag = "data-no-editable"
                
        if hasattr(self.field, "insertable") and not self.field.insertable:
            insertable_tag = "data-no-insertable"

        if hasattr(self.field, "lazy") and self.field.lazy:
            lazy_tag = "data-lazy"

        # Seta um max_length mesmo que o atributo não tenha sido definido
        if self.field.max_length == None:
            max_length = 60
        else:
            max_length = self.field.max_length
        max_length_tag = 'maxlength="%d"' % max_length

        if self.size != None:
            self.css.add_style("width", self.size) 

        if self.hidden:
            hidden_tag = "hidden"
        else:
            hidden_tag = ""

        # As próximas definições são baseadas no tipo de input            
        if self.tipo == FpcTipoField.text:
            if iscombobox:
                data_type_tag = 'data-type="combobox"'
            else:
                data_type_tag = 'data-type="text"'
            if not iscombobox and hasattr(self.field, "caixa_alta") and self.field.caixa_alta:
                caixa_alta_tag = "data-caixa-alta"
                self.css.add_style("text-transform", "uppercase")
            else:
                caixa_alta_tag = ""
            if not iscombobox and hasattr(self.field, "mascara") and self.field.mascara != None:
                mascara_tag = "data-mascara='%s'" % self.field.mascara
                if self.field.mascara_placeholder != None:
                    masc_placeholder_tag = "data-mascara-placeholder='%s'" % self.field.mascara_placeholder
                else:
                    masc_placeholder_tag = ""
            else:
                mascara_tag = ""
                masc_placeholder_tag = ""
            if iscombobox:
                tag_escolha = "<option value='-'>Selecione uma opção</option>%s" % ("".join(['<option value="%s">%s</option>' % (tupla[0], tupla[1]) for tupla in self.field.choices]))
                result = r'<select id="%s" width="100" data-field="%s" class="form-control" %s data-value="%s" %s %s %s %s %s %s %s %s>%s</select>' % (self.id, self.name, self.css.get_value(), self.value, required_tag, data_type_tag, editable_tag, insertable_tag, default_tag, onchange_tag, tag_escolha, destaca_campo_tag, self.getTagListener())
            else:
                result = r'<input id="%s" data-field="%s" class="form-control" type="text" %s %s value="%s" data-value="%s" %s %s %s %s %s %s %s %s %s %s %s/>' % (self.id, self.name, max_length_tag, self.css.get_value(), self.value, self.value, required_tag, data_type_tag, caixa_alta_tag, mascara_tag, masc_placeholder_tag, editable_tag, insertable_tag, default_tag, onchange_tag, self.getTagListener(), destaca_campo_tag)
        elif self.tipo == FpcTipoField.number:
            if iscombobox:
                data_type_tag = 'data-type="combobox"'
            else:
                if isradio:
                    data_type_tag = 'data-type="radio"'
                else:
                    data_type_tag = 'data-type="numero"'
            self.widthGrid = 40
            if hasattr(self.field, "auto_increment") and self.field.auto_increment:
                auto_inc_tag = "data-auto-increment"
            else:
                auto_inc_tag = ""
            if iscombobox:
                tag_escolha = "<option value='-'>Selecione uma opção</option>%s" % ("".join(['<option value="%s">%s</option>' % (tupla[0], tupla[1]) for tupla in self.field.choices]))
                result = r'<select id="%s" data-field="%s" class="form-control" %s data-value="%s" %s %s %s %s %s %s %s %s>%s</select>' % (self.id, self.name, self.css.get_value(), self.value, required_tag, data_type_tag, editable_tag, insertable_tag, default_tag, onchange_tag, destaca_campo_tag, lazy_tag, tag_escolha)
            else:
                if isradio:
                    idx_radio = 0
                    result = ""
                    for radio_value in self.field.choices:
                        id_radio = "%s_%d" % (self.id, idx_radio) 
                        label_radio = '<label for="%s">%s</label>' % (id_radio, radio_value[1])
                        result = result + r'<input id="%s" name="f_%s" data-field="%s" class="form-control" type="radio" %s value="%s" data-value="%s" %s %s %s %s %s %s %s %s %s/>%s' % (id_radio, self.name, self.name, data_type_tag, radio_value[0], radio_value[0], required_tag, auto_inc_tag, editable_tag, insertable_tag, self.css.get_value(), default_tag, onchange_tag, destaca_campo_tag, hidden_tag, label_radio)
                        idx_radio = idx_radio + 1
                else:
                    result = r'<input id="%s" data-field="%s" class="form-control" type="%s" %s  %s value="%s" data-value="%s" %s %s %s %s %s %s %s %s %s/>' % (self.id, self.name, self.type, max_length_tag, data_type_tag, self.value, self.value, required_tag, auto_inc_tag, editable_tag, insertable_tag, self.css.get_value(), default_tag, onchange_tag, destaca_campo_tag, hidden_tag)
        elif self.tipo == FpcTipoField.decimal:
            data_type_tag = 'data-type="decimal"'
            if self.field.max_digits != None:
                max_length = self.field.max_digits
            else: 
                max_length = 10 
            max_length_tag = 'maxlength="%d"' % max_length
            result = r'<input id="%s" data-field="%s" class="form-control" type="text" %s  %s value="%s" data-value="%s" %s data-decimal-places="%s" %s %s %s %s %s %s/>' % (self.id, self.name, max_length_tag, data_type_tag, self.value, self.value, required_tag, self.field.decimal_places, editable_tag, insertable_tag, onchange_tag, self.css.get_value(), default_tag, destaca_campo_tag)
        elif self.tipo == FpcTipoField.date:
            data_type_tag = 'data-type="data"'
            data_format_tag = r'data-format="dd/MM/yyyy"'
            self.mini_button = True
            self.mini_button_icon = "glyphicon-calendar"
            self.mini_button_onclick = ""
            self.css.add_style("width", "100px;")
            result = r'<input id="%s" data-field="%s" class="form-control" %s type="text" %s  %s value="%s" data-value="%s" %s %s %s/>' % (self.id, self.name, self.css.get_value(), data_type_tag, data_format_tag, self.value, self.value, required_tag, default_tag, destaca_campo_tag)
        elif self.tipo == FpcTipoField.lookup:
            data_type_tag = 'data-type="lookup"'
            max_length_tag = "120"
            model_str_fk = str(self.field.rel.to)[8:-2] 
            if model_str_fk != "FpcForm.models.FpcControle": 
                self.ts_id = Transacao.getIdByModel(model_str_fk)
            self.mini_button = True
            self.mini_button_icon = "glyphicon-search"
            self.mini_button_onclick = 'onclick="fpc.consultar(\'%s\', \'%s\')"' % (self.ts_id, self.id)
            self.css.add_style("width", "290px;")
            result = r'<input id="%s" data-field="%s" class="form-control" %s type="text" %s value="%s" data-value="%s" %s readonly %s %s/>' % (self.id, self.name, self.css.get_value(), data_type_tag, self.value, self.key, required_tag, default_tag, destaca_campo_tag)
        else:
            raise ValidationError("FpcField %s não pode ser renderizado." % self.name)
        
        if self.mini_button:
            result = '<div class="input-group">%s<span class="input-group-btn"><button type="button" %s class="btn btn-default btn-xs"><i class="glyphicon %s"></i></button></span></div>' % (result, self.mini_button_onclick, self.mini_button_icon) 

        if self.type != "hidden":
            if self.owner.tipo == "form-horizontal":
                if self.owner.label_grid is None:
                    label_grid = "col-sm-2 col-md-2 col-xs-2 col-lg-2"
                else:
                    label_grid = self.owner.label_grid 
                if self.owner.input_grid is None:
                    input_grid = "col-sm-10 col-md-10 col-xs-10 col-lg-10"
                else:
                    input_grid = self.owner.input_grid 
    
                result = "<div class='%s'>%s</div>" % (input_grid, result)
                result = "<label class='%s control-label' for='%s' %s>%s</label>%s" % (label_grid, self.id, self.css_label.get_value(), self.label, result) 
            else:
                result = "<label class='control-label' for='%s' %s>%s</label>%s" % (self.id, self.css_label.get_value(), self.label, result) 
        return result

        
class FpcOperacaoForm :
    pesquisa = 0
    novo = 1
    edicao = 2  
    consulta = 3
    itens = 4  
    
    @classmethod
    def asValue(self, operacao_str):
        if operacao_str == "pesquisa":
            return self.pesquisa
        elif operacao_str == "novo":
            return self.novo
        elif operacao_str == "edicao":
            return self.edicao
        elif operacao_str == "consulta":
            return self.consulta
        else:
            raise ValueError("O parâmetro operacao_str '%s' informado é inválido." % operacao_str)
         


class FpcLayout(object):

    def __init__(self, form, meta_layout, meta_template, operacao, ajax_tab, modo_lazy):
        self.form = form
        self.meta_layout = meta_layout
        if isinstance(self.meta_layout, dict): 
            self.layout = OrderedDict(sorted(self.meta_layout.copy().items(), key=lambda t: t[0][0:1]))
        else:
            self.layout = self.meta_layout
        self._model = self.form.model
        self._operacao = operacao
        self._ajax_tab = ajax_tab
        self.modo_lazy = modo_lazy
        self._lazy_fields = None
        if self._ajax_tab != None:
            self.layout = self.layout[self._ajax_tab]
        self.meta_template = meta_template
        self.tipo = "form-inline"
        self.label_grid = None
        self.input_grid = None
        self.css_form_group = ""
        self.css_label = None
        self.css_input = None
        self._createLayout()
    
    def isAjaxTab(self, tab):
        return type(self.layout[tab]) is str or ":ajax" in tab


    def getUrlAjaxTab(self, tab):
        content_tab = self.layout[tab]
        if type(content_tab) is str:   
            return content_tab
        else:
            return "tab:%s" % tab        


    def isTabVisible(self, tab):
        if ":" in tab[2:]:
            if self._operacao != None:
                if self._operacao == FpcOperacaoForm.novo and ":no_insert" in tab:
                    return False
                elif self._operacao == FpcOperacaoForm.edicao and ":no_edit" in tab:
                    return False
        return True
    
    
    def getTabCaption(self, tab):
        if ":" in tab:
            tab = tab.split(":")
            return tab[1]
        else:
            return tab


    def _addLazyField(self, field):
        if self._lazy_fields == None:
            self._lazy_fields = {}
        self._lazy_fields[field.id] = field
        
        
    def getWidgetById(self, value):
        return self._lazy_fields[value]


    def _createLayoutItem(self, item, superior, tab):
        if isinstance(item, list):
            fieldset = []
            for i in range(len(item)):
                fieldset.append(self._createLayoutItem(item[i], item, tab))
            return fieldset
        elif isinstance(item, tuple):
            tupla = []
            for i in range(len(item)):
                tupla.append(self._createLayoutItem(item[i], item, tab))
                if superior is None and self.tipo == "form-inline":
                    tupla.append({ "field" : FpcNovaLinha(), "is_nl" : True })
            return tuple(tupla)
        else:
            self._widgetCount = self._widgetCount + 1
            if isinstance(item, FpcButton):
                field = copy.deepcopy(item)
                field.setOwner(self)
            elif isinstance(item, FpcField):
                field = copy.deepcopy(item) 
                field.setOwner(self)
                field.setField(self.form.field_by_name(field.name))
            elif isinstance(item, FpcGrid):
                field = copy.deepcopy(item)
                field.setOwner(self)
                if field.field is not None:
                    field.form = self.form.carregaFormularioFilho(field.field)
                if field.lazy:
                    self._addLazyField(field)
                
            elif isinstance(item, FpcForm):
                ts = Transacao.objects.get(model=item.model_str)
                field = type(item)(ts = ts, user = self.form._user, owner = self, itens = item._itens) 
                field.createTemplate(self._request, FpcOperacaoForm.itens)
            else:
                if ":" in item:
                    item, f_id = item.split(":")
                    field = FpcField(owner = self, field = self.form.field_by_name(item), id = f_id)
                else:
                    field = FpcField(owner = self, field = self.form.field_by_name(item))
                item = field;

            if field.id == "" or field.id == None:
                field.id = "f_%s%d" % (self._id_prefix, self._widgetCount)
                         
            field = { "field" : field }
            return field
    
    
    def _createLayout(self):
        self._widgetCount = 0              
        agora = datetime.datetime.now()
        self._id_prefix = "%s%s%s" % (agora.hour, agora.minute, agora.second)
        if self.layout == None or len(self.layout) == 0:
            return () 
        if isinstance(self.layout, dict):
            # Lê configurações da chave _config se for informado pelo programador 
            if "_config" in self.layout:
                content_tab = self.layout["_config"]
                if "tipo" in content_tab:
                    self.tipo = content_tab["tipo"]
                if "label_grid" in content_tab:
                    self.label_grid = content_tab["label_grid"]
                if "input_grid" in content_tab:
                    self.input_grid = content_tab["input_grid"]
                if "css_form_group" in content_tab:
                    self.css_form_group = content_tab["css_form_group"]
                    self.css_form_group = 'style="%s"' % self.css_form_group 
                if "css_label" in content_tab:
                    self.css_label = content_tab["css_label"]
                if "css_input" in content_tab:
                    self.css_input = content_tab["css_input"]
                self.layout.pop("_config")

            for tab in self.layout:
                if not self.isAjaxTab(tab):
                    content_tab = self.layout[tab]
                    if isinstance(content_tab, tuple) or isinstance(content_tab, list):
                        item = self._createLayoutItem(content_tab, None, content_tab)
                        self.layout[tab] = item
        else:
            self.layout = self._createLayoutItem(self.layout, None, self.layout)
            
        
    def render_template(self):
        if hasattr(self.form, "model") and hasattr(self.form.model, "service_url"):
            service_url = self.form.model.service_url
        else:
            service_url = ""
        context_params = {"layout" : self, 
                          "form" : self.form, 
                          "ts" : self.form.ts, 
                          "modo_lazy" : self.modo_lazy, 
                          "opcao" : "layout",
                          "settings" : settings,
                          "service_url" : service_url,
                          "form_base" : self.form.__class__.__base__.__name__
                           }
        if hasattr(self.form, "get_context_params"):
            context_params.update(self.form.get_context_params())
        context = RequestContext(self.form.request, context_params)
        return render_to_string(self.meta_template, context)


class FpcForm(FpcWidget):
    
    def __init__(self, request, ts = None, owner=None, **kargs):
        FpcWidget.__init__(self, owner, **kargs)
        self.request = request
        self.name = str(type(self))[8:-2]
        self.ts = ts
        try:
            self.model_str = str(self.Meta.model)[8:-2]
            self.model = self.Meta.model
        except:
            self.model_str = None
            self.model = None
        try:
            self.destacaCampos = self.Meta.destacaCampos
        except:
            self.destacaCampos = False
        try:
            self.js_class = self.Meta.js_class
        except: 
            self.js_class = self.name.split(".")[2] 
        try:
            self.titulo = self.Meta.titulo
        except:
            try:
                self.titulo = self.model_str[self.model_str.rindex(".")+1:]
            except:
                self.titulo = None
        try:
            self.css_class = self.Meta.css_class
        except: 
            self.css_class = "form" 


    def get_meta_layout_and_template_by_operacao(self, operacao):
        try:
            meta_layout = self.Meta.layout
        except:
            meta_layout = None 
        try:
            meta_template = self.Meta.template
        except:
            meta_template = "fpc_form.html"
        return (meta_layout, meta_template)


    def get_context_params(self):
        breadcrumb = self.ts.get_breadcrumb()
        return { "breadcrumb" : breadcrumb,
                 "fpc" : Fpc.getFpc() }


    def get_operacao_default(self):
        return None


    def _createTag(self):
        return self.layout.render_template()

    
    def field_by_name(self, field_name):
        if field_name == 'pk':
            return self.model._meta.pk
        if hasattr(self.model, "field_by_name"):
            return self.model.field_by_name(field_name)
        else:
            return self.model._meta.get_field_by_name(field_name)[0]            

    
    # cache dos formulários
    __form_instances = {}
    __lock = RLock()


    @staticmethod
    def get_form(request):
        ts = request.ts
        if (ts.pageController != None and ts.formModel == None):
            formModel = "fpc.forms.FpcPageForm"
        else:
            formModel = ts.formModel
        return FpcForm.create_form(request, formModel, ts, request.user)
    
    
    @staticmethod
    def create_form(request, model_str, ts, user, owner=None):
        form = None
        if settings.MANTEM_FORM_CACHE:
            nome_form_cache = "fpc_usu%s_%s_%s_%d" % (user.id, model_str, request.session.session_key, ts.id)
            with FpcForm.__lock:
                form = FpcForm.__form_instances.get(nome_form_cache)

        if form is None:
            imp = model_str.split(".")
            pacote = imp[0]
            modulo = imp[1]
            classe = imp[2]
            if modulo == "forms":
                model_class = eval("__import__('%s.%s').%s.%s" % (pacote, modulo, modulo, classe))
            else:
                modulo = "forms"
                model_class = eval("__import__('%s.%s').%s.%s%s" % (pacote, modulo, modulo, classe, "Form"))
            form = model_class(request=request, ts=ts, user=user, owner=owner)
            if settings.MANTEM_FORM_CACHE:
                with FpcForm.__lock:
                    FpcForm.__form_instances[nome_form_cache] = form
                
        return form 


    def createTemplate(self, operacao=None, ajax_tab=None, modo_lazy=True, field_id=None):
        if (operacao == None):
            operacao = self.get_operacao_default()
        nome_template_cache = "fpc_%s%s%s%s%s" % (self.ts.id, operacao, ajax_tab, modo_lazy, field_id)
        template = cache.get(nome_template_cache, None)
        if template is None:
            meta_layout, meta_template = self.get_meta_layout_and_template_by_operacao(operacao)
            if meta_layout != None:
                self.layout = FpcLayout(self, meta_layout, meta_template, operacao, ajax_tab, modo_lazy)
            else:
                self.layout = FpcLayout(self, (), meta_template, operacao, ajax_tab, modo_lazy)
            if field_id is not None:
                template = self.layout.getWidgetById(field_id).tag()
            else:
                template = self.layout.render_template()
            cache.set(nome_template_cache, template)
            self.layout = None
        return template


    def carregaFormularioFilho(self, nome_field):
        field = getattr(self.model, nome_field)
        model = field.related.model
        nome_model_field = str(model)[8:-2]
        ts_filho = Transacao.getTsByModel(nome_model_field)
        form_model_filho = self.carregaFormulario(None, model_str=nome_model_field, ts=ts_filho, user=self._user, owner=self)
        return form_model_filho
    
    
    def DeSerializeForm(self, vId, values):
        is_edicao = vId != ""
        if is_edicao:
            obj = self.model.objects.get(pk=vId)
        else:
            obj = self.model()
        update_fields = []
        values = QueryDict(values)

        for nome_attr in values:
            val_attr = values[nome_attr]
            field = self.field_by_name(nome_attr)
            tipo = FpcModel.get_tipo_field(field)
            if val_attr == "":
                val_attr = None
            if tipo == FpcTipoField.lookup:
                nome_attr += "_id"
            elif tipo == FpcTipoField.date: 
                if val_attr != "":
                    try:
                        val_attr = datetime.datetime.strptime(val_attr, "%d/%m/%Y")
                    except:
                        val_attr = None
            elif tipo == FpcTipoField.decimal:
                try:
                    val_attr = Decimal(val_attr.replace(",", ".")) 
                except:
                    val_attr = None           
            elif tipo == FpcTipoField.number:
                try:
                    val_attr = int(val_attr)
                except:
                    val_attr = None
            elif tipo == FpcTipoField.text:
                if hasattr(field, "caixa_alta") and field.caixa_alta and val_attr != "" and val_attr != None:
                    val_attr = val_attr.upper()
            if getattr(obj, nome_attr) != val_attr:
                setattr(obj, nome_attr, val_attr)
                update_fields.append(nome_attr)
            
        obj.update_fields = update_fields

        return obj
    

    
    
class FpcCrud(FpcForm):
    _tupla_campos_grid = None
    _field_names = None
    campos = None
    campos_grid_pesquisa = []
    perm = "0000"
    permiteEdicao = False
    permiteInclusao = False
    permiteExcluir = False
    permiteVisualizar = False
    _itens = None
    
    
    def __init__(self, request, ts = None, user = None, owner=None, itens=None, **kargs):
        FpcForm.__init__(self, request, ts, owner, **kargs)
        self._user = user
        self._itens = itens
        if ts != None and user != None:
            self.perm = self.ts.getPermFlags(self._user)
            self.permiteEdicao = self.perm[0] == "1"
            self.permiteInclusao = self.perm[1] == "1"
            self.permiteExcluir = self.perm[2] == "1"
            self.permiteVisualizar = self.perm[3] == "1"
        self._getCampos()
        self._getCamposGridPesquisa()
    

    def _getCampos(self):
        self.campos = self.model._meta.local_fields

            
    def _getCamposGridPesquisa(self):
        if hasattr(self.Meta, "campos_grid_pesquisa"):
            self.campos_grid_pesquisa = []
            for nome_campo in self.Meta.campos_grid_pesquisa:
                try:
                    self.campos_grid_pesquisa.append([campo for campo in self.campos if campo.name == nome_campo][0])
                except IndexError: 
                    pass 
        else:
            self.campos_grid_pesquisa = self.campos[1:]

    
    def getFieldNames(self):
        if self._field_names == None:
            self._field_names = [c.name for c in self.campos if not c.name in ['id', 'controle']]
        return self._field_names
    

    def get_operacao_default(self):
        return FpcOperacaoForm.pesquisa

    
    def get_meta_layout_and_template_by_operacao(self, operacao):
        if operacao == FpcOperacaoForm.pesquisa or operacao == None:
            try:
                meta_layout = self.Meta.layout_pesquisa
            except:
                meta_layout = self.getFieldNames()
            nome_template = "fpc_pesquisa.html"
        elif operacao == FpcOperacaoForm.consulta:
            try:
                try:
                    meta_layout = self.Meta.layout_consulta
                except:
                    meta_layout = self.Meta.layout_pesquisa
            except:
                meta_layout = self.getFieldNames()
            nome_template = "fpc_consulta.html"
        elif operacao == FpcOperacaoForm.itens:
            meta_layout = None
            nome_template = "fpc_cadastro.html"
        else:
            try:
                meta_layout = self.Meta.layout
            except:
                meta_layout = self.getFieldNames()
            nome_template = "fpc_cadastro.html"
        return (meta_layout, nome_template)
    

    def getTuplaCamposGrid(self):
        if self._tupla_campos_grid == None and hasattr(self.Meta, "campos_grid_pesquisa"):
            self._tupla_campos_grid = list(self.Meta.campos_grid_pesquisa)
            self._tupla_campos_grid.insert(0, "pk")
            self._tupla_campos_grid = tuple(self._tupla_campos_grid)
        else:
            self._tupla_campos_grid = self.getFieldNames()
            self._tupla_campos_grid.insert(0, "pk")
            self._tupla_campos_grid = tuple(self._tupla_campos_grid)
        return self._tupla_campos_grid
            
    
    def _createTag(self):
        if self._itens != None:
            return render_to_string("fpc_cadastro_itens.html",  {"form" : self, "ts" : self.ts})
        else:
            return self.layout.render_template()
        
        
    """
        Salva o objeto no banco.
    """            
    def save(self, obj):
        if not obj._state.adding and obj.pk != None and obj.update_fields != None and len(obj.update_fields) > 0:
            obj.save(update_fields=obj.update_fields)
        else:
            obj.save()     
    
    
    def get_context_params(self):
        menus = Transacao.getMenuPrincipaisPorSistema(self.ts)
        lista_sistemas = menus
        breadcrumb = self.ts.get_breadcrumb()
        return { "menus" : menus,
                 "lista_sistemas" : lista_sistemas,
                 "breadcrumb" : breadcrumb,
                 "settings" : settings,
                 "fields_grid_pesquisa" : ",".join(self.getTuplaCamposGrid())
                }

    
class AutenticarForm(FpcForm):
    class Meta:
        model = User
        template = "fpc_autenticar.html"
            

class SobreForm(FpcForm):
    class Meta:
        template = "fpc_sobre.html"
        
    
class SistemaForm(FpcForm):
    class Meta:
        template = "fpc_sistema.html"
    
    def get_context_params(self):
        menus = Transacao.getMenuPrincipaisPorSistema(self.ts)
        lista_sistemas = menus
        breadcrumb = self.ts.get_breadcrumb()
        return { "menus" : menus,
                 "lista_sistemas" : lista_sistemas,
                 "breadcrumb" : breadcrumb,
                 "fpc" : Fpc.getFpc()}
        
    
class PainelForm(FpcForm):
    class Meta:
        template = "fpc_painel.html"
    
    def get_context_params(self):
        ts = self.ts
        lista = ts.getFilhos()
        breadcrumb = ts.get_breadcrumb()
        return {"lista_sistemas" : lista, 
                "breadcrumb" : breadcrumb}
    
    
class FpcPageForm(FpcForm):
    class Meta:
        template = "fpc_page.html"
    
    def get_context_params(self):
        ts = self.ts
        lista = ts.getFilhos()
        breadcrumb = ts.get_breadcrumb()
        return {"lista_sistemas" : lista, 
                "breadcrumb" : breadcrumb,
                "page_controller" : ts.pageController}
    
    