import braintree  # type: ignore
from decouple import config
from rest_framework.decorators import api_view
from rest_framework.response import Response

braintree.Configuration.configure(
    braintree.Environment.Sandbox,
    merchant_id=config('BRAINTREE_MERCHANT_ID', default='hqscdtx5y45q8gst'),
    public_key=config('BRAINTREE_PUBLIC_KEY', default='gqwntn8ffm8g6pcf'),
    private_key=config('BRAINTREE_PRIVATE_KEY', default='52bd7b66686e3d302208ca55ddac87c2'),
)


@api_view(['GET'])
def get_token(request):
    """Generate and return a client token for Braintree hosted fields."""
    client_token = braintree.ClientToken.generate({})
    return Response(client_token)


@api_view(['GET', 'POST'])
def process(request):
    """Process a transaction."""
    result = braintree.Transaction.sale(
        {
            'amount': request.data['amount'],
            'payment_method_nonce': request.data['paymentMethodNonce'],
            'customer': {'first_name': request.data['name']},
        }
    )

    if result.is_success:
        return Response('OK')
    else:
        return Response('NO')
