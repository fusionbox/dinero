import dinero
from dinero.exceptions import *

## These tests require that you provide settings for authorize.net and set up
## your account to reject invalid CVV and AVS responses
import authorize_net_configuration


## For information on how to trigger specific errors, see http://community.developer.authorize.net/t5/Integration-and-Testing/Triggering-Specific-Transaction-Responses-Using-Test-Account/td-p/4361


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

    customer = dinero.Customer.create(gateway_name='authorize.net', **options)
    try:
        assert customer.customer_payment_profile_id, 'customer.customer_payment_profile_id is not set'
    except AttributeError:
        assert False, 'customer.customer_payment_profile_id is not set'
    for key, val in options.iteritems():
        try:
            assert val == getattr(customer, key), 'customer.%s != options[%s]' % (key, key)
        except AttributeError:
            assert False, 'customer.%s is not set' % key
    customer.delete()


def test_retrieve_nonexistant_customer():
    try:
        customer = dinero.Customer.retrieve(1234567890, gateway_name='authorize.net')
        if customer:
            customer.delete()
            customer = dinero.Customer.retrieve(1234567890, gateway_name='authorize.net')
    except CustomerNotFoundError:
        pass
    else:
        assert False, "CustomerNotFoundError expected"


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

    customer = dinero.Customer.create(gateway_name='authorize.net', **options)
    customer = dinero.Customer.retrieve(customer.customer_id, gateway_name='authorize.net')
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

    customer = dinero.Customer.create(gateway_name='authorize.net', **options)
    customer_id = customer.customer_id

    customer = dinero.Customer.retrieve(customer_id, gateway_name='authorize.net')
    customer.company = new_company
    customer.save()

    customer = dinero.Customer.retrieve(customer_id, gateway_name='authorize.net')
    assert customer.company == new_company, 'Customer new_company is "%s" not "%s"' % (customer.company, new_company)
    customer.delete()


def test_create_customer_with_number_change():
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
    new_number = '4' + '2' * 15
    new_last_4_test = '2222'
    new_year = '2013'
    new_month = '11'

    customer = dinero.Customer.create(gateway_name='authorize.net', **options)
    customer.company = new_company
    customer.number = new_number
    customer.year = new_year
    customer.month = new_month
    customer.save()

    customer = dinero.Customer.retrieve(customer.customer_id, gateway_name='authorize.net')
    customer.delete()

    assert customer.company == new_company, 'Customer new_company is "%s" not "%s"' % (customer.company, new_company)
    assert customer.last_4 == new_last_4_test, 'Customer new_last_4 is "%s" not "%s"' % (customer.last_4, new_last_4_test)


def test_CRUD_customer_with_number_change():
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
    new_number = '4' + '2' * 15
    new_last_4_test = '2222'
    new_year = '2012'
    new_month = '12'

    customer = dinero.Customer.create(gateway_name='authorize.net', **options)
    customer_id = customer.customer_id

    customer = dinero.Customer.retrieve(customer_id, gateway_name='authorize.net')
    customer.company = new_company
    customer.number = new_number
    customer.year = new_year
    customer.month = new_month
    customer.save()

    customer = dinero.Customer.retrieve(customer_id, gateway_name='authorize.net')
    customer.delete()
    assert customer.company == new_company, 'Customer new_company is "%s" not "%s"' % (customer.company, new_company)
    assert customer.last_4 == new_last_4_test, 'Customer new_last_4 is "%s" not "%s"' % (customer.last_4, new_last_4_test)


def test_CRUD_customer_with_number_addition():
    options = {
        'email': 'someone@fusionbox.com',
    }
    number = '4' + '2' * 15
    year = '2012'
    month = '12'

    customer = dinero.Customer.create(gateway_name='authorize.net', **options)
    customer.number = number
    customer.year = year
    customer.month = month
    customer.save()
    customer.delete()
