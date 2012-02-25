import random
import dinero
from dinero.exceptions import *

## These tests require that you provide settings for authorize.net and set up
## your account to reject invalid CVV and AVS responses
import authorize_net_configuration


## For information on how to trigger specific errors, see http://community.developer.authorize.net/t5/Integration-and-Testing/Triggering-Specific-Transaction-Responses-Using-Test-Account/td-p/4361


def test_customer_transaction():
    options = {
        'email': 'someone@fusionbox.com',
        'number': '4' + '1' * 15,
        'month': '12',
        'year': '2012',
    }
    price = float(random.randint(1, 100000)) / 100

    customer = dinero.Customer.create(**options)
    transaction = dinero.Transaction.create(price, customer=customer)
    transaction.refund()
    customer.delete()
