import braintree

from dinero.exceptions import PaymentException, GatewayException
from dinero.gateways.base import Gateway


class Braintree(Gateway):
    def __init__(self, options):
        environment = braintree.Environment.Sandbox # TODO: autodetect live vs. test

        braintree.Configure.configure(
                environment,
                options['merchant_id'],
                options['public_key'],
                options['private_key'],
                )

    def charge(self, price, options):
        resp = braintree.Transaction.sale({
            'amount': price,
            'credit_card': {
                'number': options['number'],
                'expiration_month': options['month'],
                'expiration_year': options['year'],
                'cvv': options.get('cvv'),
                },
            'billing': {
                'first_name': options.get('first_name'),
                'last_name': options.get('last_name'),
                'address': options.get('address'),
                'locality': options.get('city'),
                'region': options.get('state'),
                'postal_code': options.get('zip'),
                },
            'options': {
                'submit_for_settlement': True,
                },
            })

        return {
                'price': price,
                'transaction_id': resp.id,

                }

    def void(self, transaction):
        raise NotImplementedError

    def refund(self, transaction, amount):
        raise NotImplementedError

    def retrieve(self, transaction_id):
        raise NotImplementedError
