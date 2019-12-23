from carton.cart import Cart
from decimal import Decimal
from django import forms
from django.conf import settings
from django.contrib.auth.decorators import permission_required, login_required
from django.core.mail import send_mail
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django_mako_plus import view_function, jscontext
from squareconnect.rest import ApiException
from squareconnect.apis.locations_api import LocationsApi
from squareconnect.apis.transactions_api import TransactionsApi
import datetime, re, traceback, logging, squareconnect

from account.models import Sale, SaleItem
from catalog.models import Product


@view_function
@login_required(login_url='/account/login')
def process_request(request):
    """  """
    context = {}
    return request.dmp.render('cart.html', context)


@view_function
@login_required(login_url='/account/login')
def add(request):
    cart = Cart(request.session)
    product = Product.objects.get(id=request.GET.get('product_id'))
    cart.add(product, price=product.price)
    return HttpResponse("Added")
