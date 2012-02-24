import dinero
from dinero.exceptions import *

## These tests require that you provide settings for authorize.net and set up
## your account to reject invalid CVV and AVS responses
import authorize_net_configuration


## For information on how to trigger specific errors, see http://community.developer.authorize.net/t5/Integration-and-Testing/Triggering-Specific-Transaction-Responses-Using-Test-Account/td-p/4361


def test_create_customer_no_email_error():
    options = {
    }

    try:
        customer = dinero.Customer.create(**options)
        customer.delete()
        assert False, "InvalidCustomerException should be raised"
    except InvalidCustomerException:
        pass


def test_create_customer_no_payment_info_error():
    options = {
        'email': 'someone@fusionbox.com',
    }

    try:
        customer = dinero.Customer.create(**options)
        customer.delete()
        assert False
    except InvalidCustomerException:
        pass
