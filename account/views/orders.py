from decimal import Decimal
from django import forms
from django.conf import settings
from django.contrib.auth.decorators import permission_required, login_required
from django.core.mail import send_mail
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django_mako_plus import view_function, jscontext
from squareconnect.rest import ApiException
from squareconnect.apis.locations_api import LocationsApi
from squareconnect.apis.transactions_api import TransactionsApi

import re, traceback, logging, squareconnect, uuid

from account.models import Sale, SaleItem, Return
from catalog.models import Product, Registration


@view_function
@login_required(login_url='/account/login')
def process_request(request):
    """  """
    context = {}
    return request.dmp.render('orders.html', context)


@view_function
@login_required(login_url='/account/login')
def receipt(request, sale_id=None):
    """The initial checkout page in which the user enters/verifies shipping info."""
    sale = get_object_or_404(Sale, pk=sale_id)
    total_payments_received = Decimal('0.00')
    for payment in sale.payments.all():
        total_payments_received += payment.amount
    items = SaleItem.objects.filter(sale=sale)
    # print(">>> Items:")
    # for item in items:
    #     print(">>> \n%s, $%s\n" % (item.name, item.price))
    # Render the template
    context = {
        'sale': sale,
        'items': items,
        'total_payments_received': total_payments_received,
        'is_email': False,
    }
    if 'email' in request.GET:
        # Send the order confirmation email
        print(">>> Sending receipt...")
        context['request'] = request
        context['is_email'] = True
        # message = render_to_string('account/receipt.email.html', context=context, request=request, using='django_mako_plus')
        message = render_to_string('account/receipt_partial.html', context=context, request=request, using='django_mako_plus')
        try:
            success = send_mail('Receipt', message, 'DO.NOT.REPLY.history@gmail.com', [request.user.email], html_message=message)
            print('>>> The receipt was emailed succcessfully!')
        except Exception as e:
            print('>>> The receipt was not emailed successfully.\n%s' % e)
    context['is_email'] = False
    context['receipt_partial'] = render_to_string('account/receipt_partial.html', context=context, request=request, using='django_mako_plus')
    return request.dmp.render('receipt.html', context)


@view_function
@login_required(login_url='/account/login')
def refund(request, sale_id=None):
    """View for processing order refunds"""

    sale = get_object_or_404(Sale, pk=sale_id)

    squareconnect.configuration.access_token = settings.SQUARE_ACCESS_TOKEN
    transaction_id = sale.transaction_id

    squareconnect.configuration.access_token = settings.SQUARE_ACCESS_TOKEN
    instance = LocationsApi()
    try:
        response = instance.list_locations() # ListLocations
        print(response.locations)
    except ApiException as e:
        print('Exception when calling LocationsApi->list_locations: %s\n' % e)

    for location in response.locations:
        if location.capabilities and 'CREDIT_CARD_PROCESSING' in location.capabilities:
            location_id = location.id
            break
    else:
        raise Exception('No valid locations could be retrieved.')

    if request.method == 'POST':
        refund_amount = Decimal('0.00')
        items = []
        for key in request.POST:
            if 'item' in key:
                item = SaleItem.objects.get(id=request.POST.get(key))
                refund_amount += item.price
                items.append(item)

                # Update products accordingly
                product = item.product
                if isinstance(product, Registration):
                    # If product is registration, update event and/or brackets
                    registration = product
                    if registration.division:
                        division = registration.division
                        for dp in sale.customer.participations.filter(event=division.event)[0].division_participations.filter(division=division):
                            dp.withdraw()
                    elif registration.event:
                        event = registration.event
                        for ep in sale.customer.participations.filter(event=event):
                            ep.withdraw()

        if len(items) >= len(sale.items.all()):
            amount = { 'amount': int(sale.total*100), 'currency': 'USD' }
        else:
            if sale.discount:
                refund_amount -= sale.discount
            amount = { 'amount': int(refund_amount*100), 'currency': 'USD' }
        print('%s' % amount)

        # Retrieve payment method
        instance = TransactionsApi()
        response = instance.retrieve_transaction(location_id, sale.transaction_id)
        transaction = response.transaction
        if len(transaction.tenders) > 1:
            raise Exception('...')
        else:
            tender = transaction.tenders[0]

        # Process the refund
        response = None
        try:
            body = {
                'idempotency_key': str(uuid.uuid1()),
                'tender_id': str(tender.id),
                'reason': str(request.POST.get('reason')),
                'amount_money': amount,
            }
            response = instance.create_refund(location_id, transaction_id, body)
            refund = response.refund
            print (refund)
        except ApiException as e:
            print ('Exception when calling TransactionsApi->charge: %s\n' % e)

        Return.record(user=request.user, sale=sale, amount=refund_amount, items=items)

        return HttpResponseRedirect('/account.orders/%s/receipt/' % sale.id)

    # Render the template
    context = {
        'sale': sale,
        'items': SaleItem.objects.filter(sale=sale),
        jscontext('sale_id'): sale.id,
    }
    return request.dmp.render('refund.html', context)
