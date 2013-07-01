from django import template
from django.core.exceptions import ObjectDoesNotExist

from django.template import  Node, resolve_variable,Variable
import math
from django.conf import settings


register = template.Library()

class SetVarNode(template.Node):

    def __init__(self, var_name, var_value):
        self.var_name = var_name
        self.var_value = var_value

    def render(self, context):
        try:
            value = template.Variable(self.var_value).resolve(context)
        except template.VariableDoesNotExist:
            value = ""
        context[self.var_name] = value
        return u""

def set_var(parser, token):
    """
        {% set <var_name>  = <var_value> %}
    """
    parts = token.split_contents()
    if len(parts) < 4:
        raise template.TemplateSyntaxError("'set' tag must be of the form:  {% set <var_name>  = <var_value> %}")
    return SetVarNode(parts[1], parts[3])

class AddGetParameter(Node):
    def __init__(self, values):
        self.values = values

    def render(self, context):
        req = resolve_variable('request',context)
        params = req.GET.copy()
        for key, value in self.values.items():
            params[key] = Variable(value).resolve(context)
        return '?%s' %  params.urlencode()


@register.tag
def add_get_parameter(parser, token):
    """
    {% load add_get_parameter %}
    <a href="{% add_get_paramater param1='const_value',param2=variable_in_context %}">
    Link with modified params
     for instances when u want to search and paginate
    </a>
    """
    from re import split
    contents = split(r'\s+', token.contents, 2)[1]
    pairs = split(r',', contents)

    values = {}

    for pair in pairs:
        s = split(r'=', pair, 2)
        values[s[0]] = s[1]

    return AddGetParameter(values)

register.tag('set', set_var)

@register.filter(name='age')
def age(value):
    """Compute the age of an individual from days"""
    if value and value > 100:
        return int(math.floor((value/365)))
    
@register.filter(name='language_str')
def language_str(value):
    """Return the language str"""
    language_tuple = getattr(settings, 'LANGUAGES', None)
    if language_tuple:
        for lang, lang_str in language_tuple:
            if lang == value:
                return lang_str
                break
    else:
        return value
