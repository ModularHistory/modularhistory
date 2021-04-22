import braintree
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

braintree.Configuration.configure(
    braintree.Environment.Sandbox,
    "ngtd9ntm7yrvb38y",
    "vg89ywm9g6q7nxrm",
    "ea86a42756b6b15a421b82dff5f10ade",
)


@api_view(['GET'])
def get_token(request):

    # Generate client token for the dropin ui
    client_token = braintree.ClientToken.generate({})

    return Response(client_token)


@api_view(['GET', 'POST'])
def proc(request):
    result = braintree.Transaction.sale(
        {
            "amount": request.json['amount'],
            "payment_method_nonce": request.json['paymentMethodNonce'],
            "customer": {"first_name": request.json['name']},
        }
    )

    if result.is_success:
        return Response("OK")
    else:
        return Response("NO")
