import braintree  # type: ignore
from decouple import config
from rest_framework.decorators import api_view
from rest_framework.response import Response

braintree.Configuration.configure(
    braintree.Environment.Sandbox,
    merchant_id=config('BRAINTREE_MERCHANT_ID', default=''),
    public_key=config('BRAINTREE_PUBLIC_KEY', default=''),
    private_key=config('BRAINTREE_PRIVATE_KEY', default=''),
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
            'payment_method_nonce': request.data['payment_method_nonce'],
            'customer': {'first_name': request.data['name']},
        }
    )

    if result.is_success:
        return Response('OK')
    else:
        return Response('NO')
