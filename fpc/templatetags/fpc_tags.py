# -*- coding: utf-8 -*-

from collections import OrderedDict
from django import template

from fpc.forms import FpcForm


register = template.Library()

@register.filter
def fpc_is_list(value):
    return type(value) is list

@register.filter
def fpc_is_tupla(value):
    return type(value) is tuple

@register.filter
def fpc_is_fieldset(value):
    return type(value) is list
        
@register.filter
def fpc_is_ajax_tab(value, layout):
    return layout.isAjaxTab(value)

@register.filter
def fpc_url_tab(tab, layout):
    return layout.getUrlAjaxTab(tab)

@register.filter
def fpc_is_tab(value):
    return type(value) is OrderedDict

@register.filter
def fpc_is_form(value):
    return isinstance(value, FpcForm)

@register.filter
def fpc_tab_is_visible(tab, layout):
    return layout.isTabVisible(tab)

@register.filter
def fpc_tab_caption(tab, layout):
    return layout.getTabCaption(tab)

@register.filter
def fpc_inc (value):
    return value + 1

@register.filter
def fpc_type(value):
    return type(value)


