# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1576990730.429603
_enable_loop = True
_template_filename = '/Users/jacob/history/people/templates/index.html'
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
        len = context.get('len', UNDEFINED)
        people = context.get('people', UNDEFINED)
        self = context.get('self', UNDEFINED)
        def content():
            return render_content(context._locals(__M_locals))
        STATIC_URL = context.get('STATIC_URL', UNDEFINED)
        event = context.get('event', UNDEFINED)
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
        len = context.get('len', UNDEFINED)
        people = context.get('people', UNDEFINED)
        self = context.get('self', UNDEFINED)
        def content():
            return render_content(context)
        STATIC_URL = context.get('STATIC_URL', UNDEFINED)
        event = context.get('event', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('\n    <div class="container">\n')
        if len(people) > 0:
            __M_writer('            <div id="people-list">\n')
            for person in people:
                __M_writer('                    <div class="row">\n')
                if False:
                    __M_writer('                        <img class="img-thumbnail" style="width: 20rem; margin-right: 1.5rem; vertical-align: top;" src="')
                    __M_writer(django_mako_plus.ExpressionPostProcessor(self)( event.pictures.filter(is_representative=True)[0].image.url if len(event.pictures.filter(is_representative=True)) > 0 else STATIC_URL+'events/media/default.png' ))
                    __M_writer('" alt="tournament image"/>\n')
                __M_writer('                        <div>\n                            <h2>\n                                <a href="/people/')
                __M_writer(django_mako_plus.ExpressionPostProcessor(self)( person.id ))
                __M_writer('/">')
                __M_writer(django_mako_plus.ExpressionPostProcessor(self)( person.name ))
                __M_writer('</a>\n                            </h3>\n                            <div>\n                                ')
                __M_writer(django_mako_plus.ExpressionPostProcessor(self)( person.birth_date.strftime('%b %d, %Y') if person.birth_date else '---' ))
                __M_writer('\n                            </div>\n                        </div>\n                    </div>\n                    <hr />\n')
            __M_writer('            </div>\n')
        else:
            __M_writer('            <p class="lead">\n                Hell is other people.\n            </p>\n            <p>\n                If you have any questions, please <a href="/contact/">contact me</a>.\n            </p>\n')
        __M_writer('    </div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "/Users/jacob/history/people/templates/index.html", "uri": "index.html", "source_encoding": "utf-8", "line_map": {"29": 0, "41": 1, "46": 33, "52": 3, "63": 3, "64": 5, "65": 6, "66": 7, "67": 8, "68": 9, "69": 10, "70": 10, "71": 10, "72": 12, "73": 14, "74": 14, "75": 14, "76": 14, "77": 17, "78": 17, "79": 23, "80": 24, "81": 25, "82": 32, "88": 82}}
__M_END_METADATA
"""
