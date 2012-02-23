import random
import dinero
from dinero.exceptions import *
from lxml import etree

## These tests require that you provide settings for authorize.net and set up
## your account to reject invalid CVV and AVS responses
import authorize_net_configuration


## For information on how to trigger specific errors, see http://community.developer.authorize.net/t5/Integration-and-Testing/Triggering-Specific-Transaction-Responses-Using-Test-Account/td-p/4361


def trimmy(s):
    return ''.join(line.lstrip() for line in s.splitlines())


def test_create_delete_customer():
    options = {
        'email': 'someone@fusionbox.com',

        'first_name': 'Joey',
        'last_name': 'Shabadoo',
        'company': 'Shabadoo, Inc.',
        'phone': '000-000-0000',
        'fax': '000-000-0001',
        'address': '123 somewhere st',
        'state': 'SW',
        'city': 'somewhere',
        'zip': '12345',
        'country': 'US',

        'number': '4' + '1' * 15,
        'month': '12',
        'year': '2012',
    }

    customer = dinero.Customer.create(**options)
    assert customer.customer_payment_profile_id, 'customer.customer_payment_profile_id is not set'
    for key, val in options.iteritems():
        assert val == getattr(customer, key), 'customer.%s != options[%s]' % (key, key)
    customer.delete()


def test_create_retrieve_delete_customer():
    options = {
        'email': 'someone@fusionbox.com',

        'first_name': 'Joey',
        'last_name': 'Shabadoo',
        'company': 'Shabadoo, Inc.',
        'phone': '000-000-0000',
        'fax': '000-000-0001',
        'address': '123 somewhere st',
        'state': 'SW',
        'city': 'somewhere',
        'zip': '12345',
        'country': 'US',

        'number': '4' + '1' * 15,
        'month': '12',
        'year': '2012',
    }

    customer = dinero.Customer.create(**options)
    customer = dinero.Customer.retrieve(customer.customer_id)
    customer.delete()


def test_CRUD_customer():
    options = {
        'email': 'someone@fusionbox.com',

        'first_name': 'Joey',
        'last_name': 'Shabadoo',
        'company': 'Shabadoo, Inc.',
        'phone': '000-000-0000',
        'fax': '000-000-0001',
        'address': '123 somewhere st',
        'state': 'SW',
        'city': 'somewhere',
        'zip': '12345',
        'country': 'US',

        'number': '4' + '1' * 15,
        'month': '12',
        'year': '2012',
    }
    new_company = 'Joey Junior, Inc.'

    customer = dinero.Customer.create(**options)
    customer_id = customer.customer_id

    customer = dinero.Customer.retrieve(customer_id)
    customer.company = new_company
    customer.save()

    customer = dinero.Customer.retrieve(customer_id)
    assert customer.company == new_company, 'Customer new_company is "%s" not "%s"' % (customer.company, new_company)
    customer.delete()


def test_retrieve_nonexistant_customer():
    try:
        customer = dinero.Customer.retrieve(1234567890)
        if customer:
            customer.delete()
            customer = dinero.Customer.retrieve(1234567890)
    except CustomerNotFoundError:
        pass
    else:
        assert False, "CustomerNotFoundError expected"

# import dinero ; import test.authorize_net_configuration ; customer = dinero.Customer.retrieve(6632317)