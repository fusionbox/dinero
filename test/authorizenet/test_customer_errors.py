import uuid

from test.utils import assertRaises

import dinero
from dinero.exceptions import InvalidCustomerException, InvalidCardError


def test_create_customer_no_email_error():
    with assertRaises(InvalidCustomerException):
        customer = dinero.Customer.create(gateway_name='authorize.net')

        # delete just in case it didn't raise an error
        customer.delete()


def test_create_customer_not_enough_payment_info_error():
    options = {
        'email': '{0}@example.com'.format(uuid.uuid4()),
        'number': '4' + '1' * 14
    }

    with assertRaises(InvalidCardError):
        customer = dinero.Customer.create(gateway_name='authorize.net', **options)
        # delete just in case it didn't raise an error
        customer.delete()
