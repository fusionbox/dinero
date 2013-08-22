from contextlib import contextmanager
import random

import dinero
from dinero.exceptions import PaymentException


def transact(price=None, number='4' + '1' * 15,
             month='12', year='2030', **kwargs):
    """
    Helper for creating test transactions.  Please specify gateway_name.
    """
    if price is None:
        price = float(random.randint(1, 100000)) / 100

    return dinero.Transaction.create(
        price,
        number=number,
        month=month,
        year=year,
        **kwargs
    )


@contextmanager
def assertRaises(exception):
    try:
        yield
    except Exception as e:
        assert isinstance(e, exception)
    else:
        assert False, "Did not raise %r" % exception


@contextmanager
def assertRaisesError(*desired_errors):
    """
    Like assertRaises, but just for checking which errors a PaymentException
    contains.

    with assertRaisesError(AVSError):
        # do something
    """
    try:
        yield
    except PaymentException as e:
        for error in desired_errors:
            assert error in e
    else:
        assert False, "Did not raise %r" % desired_errors
