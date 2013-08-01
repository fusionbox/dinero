import os
import uuid
import datetime
import random
import dinero
from dinero.exceptions import *

## These tests require that you provide settings for authorize.net and set up
## your account to reject invalid CVV and AVS responses
try:
    import authorize_net_configuration
except ImportError:
    LOGIN_ID = os.environ["AUTHNET_LOGIN_ID"]
    TRANSACTION_KEY = os.environ["AUTHNET_TRANSACTION_KEY"]
    dinero.configure({
        'authorize.net': {
            'type': 'dinero.gateways.AuthorizeNet',
            'login_id': LOGIN_ID,
            'transaction_key': TRANSACTION_KEY,
            'default': True,
        }
    })


## For information on how to trigger specific errors, see http://community.developer.authorize.net/t5/Integration-and-Testing/Triggering-Specific-Transaction-Responses-Using-Test-Account/td-p/4361


def test_customer_transaction():
    options = {
        'email': '{0}@example.com'.format(uuid.uuid4()),
        'number': '4' + '1' * 15,
        'month': '12',
        'year': str(datetime.date.today().year + 1),
    }
    price = float(random.randint(1, 100000)) / 100

    customer = dinero.Customer.create(gateway_name='authorize.net', **options)
    transaction = dinero.Transaction.create(price, customer=customer, gateway_name='authorize.net')
    transaction.refund()
    customer.delete()
