# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1577004544.8969018
_enable_loop = True
_template_filename = '/Users/jacob/history/places/templates/index.html'
_template_uri = 'index.html'
_source_encoding = 'utf-8'
import django_mako_plus
import django.utils.html
_exports = ['content']


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    pass
def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, '/home/templates/base.htm', _template_uri)
def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        def content():
            return render_content(context._locals(__M_locals))
        places = context.get('places', UNDEFINED)
        self = context.get('self', UNDEFINED)
        len = context.get('len', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'content'):
            context['self'].content(**pageargs)
        

        __M_writer('\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_content(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def content():
            return render_content(context)
        places = context.get('places', UNDEFINED)
        self = context.get('self', UNDEFINED)
        len = context.get('len', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('\n    <div class="container">\n')
        if len(places) > 0:
            __M_writer('            <div id="occurrences-list">\n')
            for place in places:
                __M_writer('                    <div class="row">\n                        <div>\n                            <h2>\n                                <a href="/places/')
                __M_writer(django_mako_plus.ExpressionPostProcessor(self)( place.id ))
                __M_writer('/">')
                __M_writer(django_mako_plus.ExpressionPostProcessor(self)( place.name ))
                __M_writer('</a>\n                            </h2>\n                        </div>\n                    </div>\n                    <hr />\n')
            __M_writer('            </div>\n')
        else:
            __M_writer('            <p class="lead">\n                Hell is other people.\n            </p>\n            <p>\n                If you have any questions, please <a href="/contact/">contact me</a>.\n            </p>\n')
        __M_writer('    </div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "/Users/jacob/history/places/templates/index.html", "uri": "index.html", "source_encoding": "utf-8", "line_map": {"29": 0, "39": 1, "44": 27, "50": 3, "59": 3, "60": 5, "61": 6, "62": 7, "63": 8, "64": 11, "65": 11, "66": 11, "67": 11, "68": 17, "69": 18, "70": 19, "71": 26, "77": 71}}
__M_END_METADATA
"""
