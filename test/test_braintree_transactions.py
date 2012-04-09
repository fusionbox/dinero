import dinero
from dinero.exceptions import *

## These tests require that you provide settings for braintree and set up
## your account to reject invalid CVV and AVS responses
import braintree_configuration


## For information on how to trigger specific errors, see http://www.braintreepayments.com/docs/python/reference/processor_responses


def test_customer_transaction_float():
    options = {
        'email': 'someone@fusionbox.com',
        'number': '4' + '1' * 15,
        'month': '12',
        'year': '2012',
    }
    price = 1.00

    customer = dinero.Customer.create(gateway_name='braintree', **options)
    transaction = dinero.Transaction.create(price, customer=customer, gateway_name='braintree')
    transaction.refund()
    customer.delete()


def test_customer_transaction_str():
    options = {
        'email': 'someone@fusionbox.com',
        'number': '4500600000000061',
        'month': '12',
        'year': '2012',
    }
    price = '1.50'

    customer = dinero.Customer.create(gateway_name='braintree', **options)
    transaction = dinero.Transaction.create(price, customer=customer, gateway_name='braintree')
    transaction.refund()
    customer.delete()
