# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1577004544.9155378
_enable_loop = True
_template_filename = '/Users/jacob/history/home/templates/base.htm'
_template_uri = '/home/templates/base.htm'
_source_encoding = 'utf-8'
import django_mako_plus
import django.utils.html
_exports = ['title', 'head_scripts', 'main_menu', 'base_content', 'breadcrumb', 'page_header', 'fluid_content', 'content', 'footer', 'scripts']


from django.utils import timezone 

import datetime 

def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        request = context.get('request', UNDEFINED)
        STATIC_URL = context.get('STATIC_URL', UNDEFINED)
        def scripts():
            return render_scripts(context._locals(__M_locals))
        def main_menu():
            return render_main_menu(context._locals(__M_locals))
        def base_content():
            return render_base_content(context._locals(__M_locals))
        def fluid_content():
            return render_fluid_content(context._locals(__M_locals))
        def page_header():
            return render_page_header(context._locals(__M_locals))
        def head_scripts():
            return render_head_scripts(context._locals(__M_locals))
        def content():
            return render_content(context._locals(__M_locals))
        def breadcrumb():
            return render_breadcrumb(context._locals(__M_locals))
        self = context.get('self', UNDEFINED)
        def footer():
            return render_footer(context._locals(__M_locals))
        __M_writer = context.writer()
        __M_writer('\n')
        __M_writer('\n\n<!DOCTYPE html>\n<html lang="en" xml:lang="en">\n    <head>\n        <meta charset="UTF-8" />\n        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">\n        <meta name="google" content="notranslate">\n        <meta http-equiv="Content-Language" content="en">\n        <!-- <meta property="og:image" content="https://www.history.com')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('home/media/images/ju1.jpg" /> -->\n        <meta property="og:type" content="website" />\n        <!-- <meta property="og:url" content="https://www.history.com/" /> -->\n        <!-- <meta property="og:title" content="History" /> -->\n        <!-- <meta property="og:description" content="Utah\'s submission tournament leader" /> -->\n\n        <!-- <link rel="shortcut icon" href="')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('home/media/favicon.ico" type="image/x-icon" />\n        <link rel="icon" href="')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('home/media/favicon.ico" type="image/x-icon" /> -->\n\n        <title>')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'title'):
            context['self'].title(**pageargs)
        

        __M_writer(' | JTF</title>\n\n')
        __M_writer('        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">\n        <!-- ## jQuery datetimepicker CSS\n        <link rel="stylesheet" href="')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('home/scripts/datetimepicker/jquery.datetimepicker.css" /> -->\n        <!-- ## jQuery UI CSS\n        <link rel="stylesheet" href="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/themes/smoothness/jquery-ui.css"> -->\n        <!-- ## jQuery DataTables CSS\n        <link rel="stylesheet" href="https://cdn.datatables.net/1.10.16/css/dataTables.bootstrap.min.css" /> -->\n\n')
        __M_writer('        <script src="http://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>\n')
        __M_writer('        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>\n')
        __M_writer('        <script src="https://use.fontawesome.com/1a7f0f40be.js"></script>\n\n        <!-- ## emulate tab\n        <script src="')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('home/scripts/emulatetab.joelpurra.js"></script>\n')
        __M_writer('        <script src="')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('home/scripts/plusastab.joelpurra.js"></script>\n')
        __M_writer('        <script src="')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('home/scripts/jquery.loadmodal.js"></script>\n')
        __M_writer('        <script src="')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('home/scripts/jquery.form.js"></script>\n')
        __M_writer('        <script src="')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('home/scripts/spin.js" defer></script>\n')
        __M_writer('        <script src="')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('home/scripts/jquery.tablednd.js" defer></script>\n')
        __M_writer('        <script src="')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('home/scripts/list.js" defer></script>\n')
        __M_writer('        <script src="')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('home/scripts/datetimepicker/jquery.datetimepicker.full.js" defer></script> -->\n        <!-- ## cookies\n        <script src="https://cdn.jsdelivr.net/npm/js-cookie@2/src/js.cookie.min.js"></script>\n')
        __M_writer('        <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js" defer></script>\n')
        __M_writer('        <script src="https://cdn.datatables.net/1.10.16/js/jquery.dataTables.min.js" defer></script>\n        <script src="https://cdn.datatables.net/1.10.16/js/dataTables.bootstrap.min.js" defer></script> -->\n\n        <!-- <script src=\'https://maps.googleapis.com/maps/api/js?v=3.exp&key=AIzaSyBZqpNyAkIBNL2LBeG-eWR1VvFWaZ2HBIc\'></script> -->\n\n')
        __M_writer('        ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'head_scripts'):
            context['self'].head_scripts(**pageargs)
        

        __M_writer('\n\n')
        __M_writer('        <script src="/django_mako_plus/dmp-common.min.js"></script>\n        ')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( django_mako_plus.links(self) ))
        __M_writer('\n\n')
        __M_writer("        <!--<link href='http://fonts.googleapis.com/css?family=Oxygen:400,300,700' rel='stylesheet' type='text/css'>-->\n    </head>\n    <body>\n        ")
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'main_menu'):
            context['self'].main_menu(**pageargs)
        

        __M_writer('\n        <div id="main">\n          ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'base_content'):
            context['self'].base_content(**pageargs)
        

        __M_writer('\n        </div>\n\n        <footer id="footer">\n            <div class="container text-center">\n                ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'footer'):
            context['self'].footer(**pageargs)
        

        __M_writer('\n            </div>\n        </footer>\n\n')
        __M_writer('        ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'scripts'):
            context['self'].scripts(**pageargs)
        

        __M_writer('\n    </body>\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def title():
            return render_title(context)
        __M_writer = context.writer()
        __M_writer('Home')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_head_scripts(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def head_scripts():
            return render_head_scripts(context)
        __M_writer = context.writer()
        __M_writer('\n        ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_main_menu(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        request = context.get('request', UNDEFINED)
        def main_menu():
            return render_main_menu(context)
        self = context.get('self', UNDEFINED)
        STATIC_URL = context.get('STATIC_URL', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('\n            ')

        menu_items = [
            [ 'History',    'occurrences'   ],
            [ 'People',     'people'        ],
            [ 'Places',     'places'        ],
            [ 'Quotes',     'quotes'        ],
            [ 'Sources',    'sources'        ],
            [ 'Contact',    'contact'       ],
        ]
                    
        
        __M_writer('\n            <nav class="navbar navbar-inverse">\n                <div class="container-fluid">\n                    <div class="navbar-header">\n                        <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">\n                            <span class="icon-bar"></span>\n                            <span class="icon-bar"></span>\n                            <span class="icon-bar"></span>\n                        </button>\n                        <a class="navbar-brand" href="/">\n                            <!-- <img class="img-responsive" style="height: 110px; visibility: hidden;" src="')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('home/media/images/logo.png" />\n                            <div id="navbar-logo" style="position: absolute; top: 0; left: 0; padding: 0 0.5rem; background-color: #991314; height: 127px; border-bottom: 1px solid black; border-bottom-right-radius: 72px; border-left: 1px solid black;">\n                                <img class="img-responsive" style="height: inherit; position: relative;" src="')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('home/media/images/logo.png" />\n                            </div> -->\n                        </a>\n                    </div>\n                    <div class="collapse navbar-collapse">\n                        <ul id="main-menu" class="nav navbar-nav">\n')
        for title, app in menu_items:
            __M_writer('                                <li class="nav-item ')
            __M_writer(django_mako_plus.ExpressionPostProcessor(self)( 'active' if True else '' ))
            __M_writer('">\n                                    <a class="nav-link" href="/')
            __M_writer(django_mako_plus.ExpressionPostProcessor(self)( app ))
            __M_writer('/">')
            __M_writer(django_mako_plus.ExpressionPostProcessor(self)( title ))
            __M_writer('</a>\n                                </li>\n')
        __M_writer('                        </ul>\n                        <ul class="nav navbar-nav navbar-right">\n')
        if not request.user.is_authenticated:
            __M_writer('                                <li class="nav-item">\n                                    <a href="/account/register/" class="nav-link">\n                                        <span class="glyphicon glyphicon-user" style="margin-right: 0.1rem;"></span> Register\n                                    </a>\n                                </li>\n                                <li class="nav-item">\n                                    <a href="/account/login?ajax=True" class="nav-link modal-trigger" id="login-button">\n                                        <span class="glyphicon glyphicon-log-in" style="margin-right: 0.3rem;"></span> Login\n                                    </a>\n                                </li>\n')
        else:
            if True in (request.user.is_superuser, request.user.groups.filter(name='Administrators').exists(), request.user.groups.filter(name='Referees').exists(), request.user.groups.filter(name='Stagers').exists()):
                __M_writer('                                    <li class="dropdown">\n                                        <a class="dropdown-toggle nav-link" data-toggle="dropdown" href="#">\n                                            Administration <span class="caret"></span>\n                                        </a>\n                                        <ul class="dropdown-menu">\n                                            <li><a href="/events/manage/">Event Administration</a></li>\n')
                if request.user.is_superuser:
                    __M_writer('                                                <li><a href="/administration/">Site Administration</a></li>\n                                                <ul class="dropdown-menu-level-2">\n                                                    <!-- <li><a href="/administration/appearance/">Appearance</a></li>\n                                                    <li><a href="/administration/content/">Content</a></li> -->\n                                                    <li><a href="/admin/">Database</a></li>\n                                                </ul>\n')
                __M_writer('                                        </ul>\n                                    </li>\n')
            __M_writer('                                <li class="dropdown">\n                                    <a class="dropdown-toggle nav-link" data-toggle="dropdown" href="#">\n                                        Account <span class="caret"></span>\n                                    </a>\n                                    <ul class="dropdown-menu">\n                                        <li><a href="/account/profile/">Profile</a></li>\n                                        <li><a href="/account/orders/">Orders</a></li>\n                                        <li><a href="/account/settings/">Settings &amp; Privacy</a></li>\n                                        <li role="separator" class="divider"></li>\n                                        <li><a href="/account/logout/"><span class="glyphicon glyphicon-log-out"></span> Logout</a></li>\n                                    </ul>\n                                </li>\n')
        __M_writer('                        </ul>\n                    </div>\n                </div>\n            </nav>\n        ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_base_content(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def base_content():
            return render_base_content(context)
        def fluid_content():
            return render_fluid_content(context)
        def page_header():
            return render_page_header(context)
        def content():
            return render_content(context)
        def breadcrumb():
            return render_breadcrumb(context)
        __M_writer = context.writer()
        __M_writer('\n              <div class="container-fluid">\n                  <ol class="breadcrumb" style="margin-left: 18.8rem; padding: 1rem 1rem;">\n                      ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'breadcrumb'):
            context['self'].breadcrumb(**pageargs)
        

        __M_writer('\n                  </ol>\n                  <h1 class="page-header text-center" style="margin-top: 0;">\n                      ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'page_header'):
            context['self'].page_header(**pageargs)
        

        __M_writer('\n                  </h1>\n                  ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'fluid_content'):
            context['self'].fluid_content(**pageargs)
        

        __M_writer('\n              </div>\n              <div id="feedback-modal" class="modal fade" tabindex="-1" role="dialog">\n                  <div class="modal-dialog">\n                      <div class="modal-content">\n                          <div class="modal-header">\n                              <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>\n                              <h4 class="modal-title"></h4>\n                          </div>\n                          <div class="modal-body">\n                              <p id="feedback-modal-message" class="text-center"></p>\n                          </div>\n                          <div class="modal-footer">\n                              <a id="feedback-modal-confirm-btn" href="" class="btn btn-primary">OK</a>\n                              <button type="button" class="btn btn-default cancel-button" data-dismiss="modal">Cancel</button>\n                          </div>\n                      </div><!-- /.modal-content -->\n                  </div><!-- /.modal-dialog -->\n              </div><!-- /.modal -->\n          ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_breadcrumb(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def breadcrumb():
            return render_breadcrumb(context)
        __M_writer = context.writer()
        __M_writer('\n                      ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_page_header(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def page_header():
            return render_page_header(context)
        __M_writer = context.writer()
        __M_writer('\n                      ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_fluid_content(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def content():
            return render_content(context)
        def fluid_content():
            return render_fluid_content(context)
        __M_writer = context.writer()
        __M_writer('\n                      <div id="content" class="container">\n                          ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'content'):
            context['self'].content(**pageargs)
        

        __M_writer('\n                      </div>\n                  ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_content(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def content():
            return render_content(context)
        __M_writer = context.writer()
        __M_writer('\n                          ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_footer(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        self = context.get('self', UNDEFINED)
        def footer():
            return render_footer(context)
        __M_writer = context.writer()
        __M_writer("\n                    <span class='copyright'>&copy; ")
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( datetime.date.today().year ))
        __M_writer(' Jacob Fredericksen</span>\n                    &nbsp;\n                    <span class=\'privacy-and-terms\'><a href="/privacy_policy/">Privacy</a> &middot; <a href="/terms_of_use/" style="display: inline-block">Terms of Use</a></span>\n                    <span class=\'back-to-top\'><a href="#">Back to top</a></span>\n                ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_scripts(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def scripts():
            return render_scripts(context)
        __M_writer = context.writer()
        __M_writer('\n        ')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "/Users/jacob/history/home/templates/base.htm", "uri": "/home/templates/base.htm", "source_encoding": "utf-8", "line_map": {"18": 1, "20": 2, "22": 0, "48": 1, "49": 2, "50": 11, "51": 11, "52": 17, "53": 17, "54": 18, "55": 18, "60": 20, "61": 23, "62": 25, "63": 25, "64": 32, "65": 34, "66": 36, "67": 39, "68": 39, "69": 41, "70": 41, "71": 41, "72": 43, "73": 43, "74": 43, "75": 45, "76": 45, "77": 45, "78": 47, "79": 47, "80": 47, "81": 49, "82": 49, "83": 49, "84": 51, "85": 51, "86": 51, "87": 53, "88": 53, "89": 53, "90": 57, "91": 59, "92": 65, "97": 66, "98": 69, "99": 70, "100": 70, "101": 73, "106": 158, "111": 194, "116": 204, "117": 209, "122": 210, "128": 20, "134": 20, "140": 65, "146": 65, "152": 76, "161": 76, "162": 77, "173": 86, "174": 96, "175": 96, "176": 98, "177": 98, "178": 104, "179": 105, "180": 105, "181": 105, "182": 106, "183": 106, "184": 106, "185": 106, "186": 109, "187": 111, "188": 112, "189": 122, "190": 123, "191": 124, "192": 130, "193": 131, "194": 138, "195": 141, "196": 154, "202": 160, "216": 160, "221": 164, "226": 168, "231": 175, "237": 163, "243": 163, "249": 167, "255": 167, "261": 170, "269": 170, "274": 173, "280": 172, "286": 172, "292": 199, "299": 199, "300": 200, "301": 200, "307": 209, "313": 209, "319": 313}}
__M_END_METADATA
"""
