import braintree
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
)
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

braintree.Configuration.configure(
    braintree.Environment.Sandbox,
    "ngtd9ntm7yrvb38y",
    "vg89ywm9g6q7nxrm",
    "ea86a42756b6b15a421b82dff5f10ade",
)


@app.route("/token")
def index():

    # Generate client token for the dropin ui
    client_token = braintree.ClientToken.generate({})

    return client_token


@app.route("/proc", methods=['GET', 'POST'])
def proc():
    result = braintree.Transaction.sale(
        {
            "amount": request.json['amount'],
            "payment_method_nonce": request.json['paymentMethodNonce'],
            "customer": {"first_name": request.json['name']},
        }
    )

    if result.is_success:
        return "OK"
    else:
        return "NO"


@app.route('/public/<path:path>')
def send_public(path):
    return send_from_directory('public', path)


if __name__ == "__main__":
    app.run()
