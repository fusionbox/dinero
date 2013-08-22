import uuid
import datetime

from test.utils import transact

import dinero


def test_customer_transaction():
    options = {
        'email': '{0}@example.com'.format(uuid.uuid4()),
        'number': '4' + '1' * 15,
        'month': '12',
        'year': str(datetime.date.today().year + 1),
    }

    try:
        customer = dinero.Customer.create(gateway_name='authorize.net',
                                          **options)
        transaction = transact(customer=customer,
                               gateway_name='authorize.net')
    finally:
        # cleanup
        try:
            transaction.refund()
        finally:
            customer.delete()
