# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1577098511.57762
_enable_loop = True
_template_filename = '/Users/jacob/history/home/templates/base.htm'
_template_uri = '/home/templates/base.htm'
_source_encoding = 'utf-8'
import django_mako_plus
import django.utils.html
_exports = ['title', 'main_menu', 'base_content', 'breadcrumb', 'page_header', 'fluid_content', 'content', 'footer', 'scripts']


from django.utils import timezone 

import datetime 

def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        def breadcrumb():
            return render_breadcrumb(context._locals(__M_locals))
        self = context.get('self', UNDEFINED)
        def main_menu():
            return render_main_menu(context._locals(__M_locals))
        def base_content():
            return render_base_content(context._locals(__M_locals))
        def page_header():
            return render_page_header(context._locals(__M_locals))
        def content():
            return render_content(context._locals(__M_locals))
        STATIC_URL = context.get('STATIC_URL', UNDEFINED)
        def scripts():
            return render_scripts(context._locals(__M_locals))
        def fluid_content():
            return render_fluid_content(context._locals(__M_locals))
        request = context.get('request', UNDEFINED)
        def footer():
            return render_footer(context._locals(__M_locals))
        __M_writer = context.writer()
        __M_writer('\n')
        __M_writer('\n\n<!DOCTYPE html>\n<html lang="en" xml:lang="en">\n    <head>\n        <meta charset="UTF-8" />\n        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">\n        <meta name="google" content="notranslate">\n        <meta http-equiv="Content-Language" content="en">\n        <!-- <meta property="og:image" content="https://www.history.com')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('home/media/images/ju1.jpg" /> -->\n        <meta property="og:type" content="website" />\n        <!-- <meta property="og:url" content="https://www.history.com/" /> -->\n        <!-- <meta property="og:title" content="History" /> -->\n        <!-- <meta property="og:description" content="Utah\'s submission tournament leader" /> -->\n\n        <title>')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'title'):
            context['self'].title(**pageargs)
        

        __M_writer(' | JTF</title>\n\n        <link rel="icon" href="')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('home/media/favicon.ico" type="image/x-icon" />\n\n        <!-- Font Awesome -->\n        <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.11.2/css/all.css">\n\n        <!-- ## jQuery datetimepicker CSS\n        <link rel="stylesheet" href="')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('home/scripts/datetimepicker/jquery.datetimepicker.css" /> -->\n        <!-- ## jQuery UI CSS\n        <link rel="stylesheet" href="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/themes/smoothness/jquery-ui.css"> -->\n        <!-- ## jQuery DataTables CSS\n        <link rel="stylesheet" href="https://cdn.datatables.net/1.10.16/css/dataTables.bootstrap.min.css" /> -->\n\n        <!-- Latest compiled and minified Bootstrap CSS -->\n        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css">\n        <!-- Material Design Bootstrap CSS -->\n        <link rel="stylesheet" href="')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('mdb/css/mdb.min.css">\n\n        <!-- jQuery library -->\n        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>\n        <!-- Popper JS -->\n        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script>\n        <!-- Latest compiled Bootstrap JavaScript -->\n        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js"></script>\n        <!-- Material Design Bootstrap core JavaScript -->\n        <script type="text/javascript" src="')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( STATIC_URL ))
        __M_writer('mdb/js/mdb.min.js"></script>\n\n        <!-- ## emulate tab\n        <script src="')
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
        __M_writer('        <script src="/django_mako_plus/dmp-common.min.js"></script>\n        ')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( django_mako_plus.links(self) ))
        __M_writer('\n\n')
        __M_writer('        <!--<link href=\'http://fonts.googleapis.com/css?family=Oxygen:400,300,700\' rel=\'stylesheet\' type=\'text/css\'>-->\n    </head>\n    <body>\n        <nav class="navbar navbar-expand-sm bg-dark navbar-dark">\n            <!-- Logo -->\n            <a class="navbar-brand" href="#">\n                Logo\n                <!--<img src="" alt="Logo" style="width:40px;">-->\n            </a>\n\n            <!-- Toggler/collapser button -->\n            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#collapsibleNavbar">\n                <span class="navbar-toggler-icon"></span>\n            </button>\n\n            <!-- Links -->\n            <div class="collapse navbar-collapse" id="collapsibleNavbar">\n                <ul class="navbar-nav">\n                    ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'main_menu'):
            context['self'].main_menu(**pageargs)
        

        __M_writer('\n                </ul>\n\n                <form class="form-inline my-2 my-lg-0 ml-auto" action="/search">\n                    <div class="input-group">\n                        <input class="form-control" type="search" placeholder="Search" aria-label="Search">\n                        <div class="input-group-append">\n                            <button class="btn btn-outline-white btn-md my-2 my-sm-0 ml-3" type="submit">\n                                <i class="fas fa-search"></i>\n                            </button>\n                        </div>\n                    </div>\n                </form>\n\n<!--                &lt;!&ndash; Navbar text&ndash;&gt;-->\n<!--                <span class="navbar-text">-->\n<!--                </span>-->\n\n                <ul class="navbar-nav ml-auto nav-flex-icons">\n                    <li class="nav-item">\n                        <a class="nav-link waves-effect waves-light">\n                            <i class="fab fa-twitter"></i>\n                        </a>\n                    </li>\n                    <li class="nav-item">\n                        <a class="nav-link waves-effect waves-light">\n                            <i class="fab fa-google-plus-g"></i>\n                        </a>\n                    </li>\n                    <li class="nav-item">\n                        <button class="btn btn-sm align-middle btn-outline-white" type="button">Patreon</button>\n                    </li>\n                    <li class="nav-item dropdown">\n                        <a class="nav-link dropdown-toggle" id="navbarDropdownMenuLink-333" data-toggle="dropdown"\n                           aria-haspopup="true" aria-expanded="false">\n                            <i class="fas fa-user"></i>\n                        </a>\n                        <div class="dropdown-menu dropdown-menu-right dropdown-default"\n                             aria-labelledby="navbarDropdownMenuLink-333">\n                            <a class="dropdown-item" href="#">Action</a>\n                            <a class="dropdown-item" href="#">Another action</a>\n                            <a class="dropdown-item" href="#">Something else here</a>\n                        </div>\n                    </li>\n                </ul>\n            </div>\n\n        </nav>\n        <nav class="navbar navbar-inverse">\n\n            <div class="collapse navbar-collapse">\n                <ul id="main-menu" class="navbar-nav justify-content-center">\n                </ul>\n                <ul class="nav navbar-nav navbar-right">\n')
        if not request.user.is_authenticated:
            __M_writer('                        <li class="nav-item">\n                            <a href="/account/register/" class="nav-link">\n                                <span class="glyphicon glyphicon-user" style="margin-right: 0.1rem;"></span> Register\n                            </a>\n                        </li>\n                        <li class="nav-item">\n                            <a href="/account/login?ajax=True" class="nav-link modal-trigger" id="login-button">\n                                <span class="glyphicon glyphicon-log-in" style="margin-right: 0.3rem;"></span> Login\n                            </a>\n                        </li>\n')
        else:
            if True in (request.user.is_superuser, request.user.groups.filter(name='Administrators').exists(), request.user.groups.filter(name='Referees').exists(), request.user.groups.filter(name='Stagers').exists()):
                __M_writer('                            <li class="dropdown">\n                                <a class="dropdown-toggle nav-link" data-toggle="dropdown" href="#">\n                                    Administration <span class="caret"></span>\n                                </a>\n                                <ul class="dropdown-menu">\n                                    <li><a href="/events/manage/">Event Administration</a></li>\n')
                if request.user.is_superuser:
                    __M_writer('                                        <li><a href="/administration/">Site Administration</a></li>\n                                        <ul class="dropdown-menu-level-2">\n                                            <!-- <li><a href="/administration/appearance/">Appearance</a></li>\n                                            <li><a href="/administration/content/">Content</a></li> -->\n                                            <li><a href="/admin/">Database</a></li>\n                                        </ul>\n')
                __M_writer('                                </ul>\n                            </li>\n')
            __M_writer('                        <li class="dropdown">\n                            <a class="dropdown-toggle nav-link" data-toggle="dropdown" href="#">\n                                Account <span class="caret"></span>\n                            </a>\n                            <ul class="dropdown-menu">\n                                <li><a href="/account/profile/">Profile</a></li>\n                                <li><a href="/account/orders/">Orders</a></li>\n                                <li><a href="/account/settings/">Settings &amp; Privacy</a></li>\n                                <li role="separator" class="divider"></li>\n                                <li><a href="/account/logout/"><span class="glyphicon glyphicon-log-out"></span> Logout</a></li>\n                            </ul>\n                        </li>\n')
        __M_writer('                </ul>\n            </div>\n        </nav>\n        <div id="main">\n          ')
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


def render_main_menu(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        self = context.get('self', UNDEFINED)
        def main_menu():
            return render_main_menu(context)
        __M_writer = context.writer()
        __M_writer('\n                        <!-- Dropdown -->\n                        <li class="nav-item dropdown active">\n                            <a class="nav-link dropdown-toggle" href="#" id="navbardrop" data-toggle="dropdown">\n                                History\n                            </a>\n                            <div class="dropdown-menu">\n                                ')

        menu_items = [
            ['Occurrences', 'occurrences'   ],
            ['People',      'people'        ],
            ['Places',      'places'        ],
            ['Quotes',      'quotes'        ],
            ['Sources',     'sources'       ],
            ['Topics',      'topics'        ],
        ]
                                        
        
        __M_writer('\n')
        for title, app in menu_items:
            __M_writer('                                    <a class="dropdown-item" href="/history/')
            __M_writer(django_mako_plus.ExpressionPostProcessor(self)( app ))
            __M_writer('/">')
            __M_writer(django_mako_plus.ExpressionPostProcessor(self)( title ))
            __M_writer('</a>\n                                <!--                        <li class="nav-item ')
            __M_writer(django_mako_plus.ExpressionPostProcessor(self)( 'active' if False else '' ))
            __M_writer('">-->\n                                <!--                            <a class="nav-link" href="/')
            __M_writer(django_mako_plus.ExpressionPostProcessor(self)( app ))
            __M_writer('/">')
            __M_writer(django_mako_plus.ExpressionPostProcessor(self)( title ))
            __M_writer('</a>-->\n                                <!--                        </li>-->\n')
        __M_writer('                            </div>\n                        </li>\n                    ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_base_content(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def breadcrumb():
            return render_breadcrumb(context)
        def base_content():
            return render_base_content(context)
        def page_header():
            return render_page_header(context)
        def content():
            return render_content(context)
        def fluid_content():
            return render_fluid_content(context)
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
{"filename": "/Users/jacob/history/home/templates/base.htm", "uri": "/home/templates/base.htm", "source_encoding": "utf-8", "line_map": {"18": 1, "20": 2, "22": 0, "46": 1, "47": 2, "48": 11, "49": 11, "54": 17, "55": 19, "56": 19, "57": 25, "58": 25, "59": 34, "60": 34, "61": 43, "62": 43, "63": 46, "64": 46, "65": 48, "66": 48, "67": 48, "68": 50, "69": 50, "70": 50, "71": 52, "72": 52, "73": 52, "74": 54, "75": 54, "76": 54, "77": 56, "78": 56, "79": 56, "80": 58, "81": 58, "82": 58, "83": 60, "84": 60, "85": 60, "86": 64, "87": 66, "88": 72, "89": 73, "90": 73, "91": 76, "96": 119, "97": 173, "98": 174, "99": 184, "100": 185, "101": 186, "102": 192, "103": 193, "104": 200, "105": 203, "106": 216, "111": 254, "116": 264, "117": 269, "122": 270, "128": 17, "134": 17, "140": 94, "147": 94, "148": 101, "159": 110, "160": 111, "161": 112, "162": 112, "163": 112, "164": 112, "165": 112, "166": 113, "167": 113, "168": 114, "169": 114, "170": 114, "171": 114, "172": 117, "178": 220, "192": 220, "197": 224, "202": 228, "207": 235, "213": 223, "219": 223, "225": 227, "231": 227, "237": 230, "245": 230, "250": 233, "256": 232, "262": 232, "268": 259, "275": 259, "276": 260, "277": 260, "283": 269, "289": 269, "295": 289}}
__M_END_METADATA
"""
