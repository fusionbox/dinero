import dinero
from dinero.exceptions import *

## These tests require that you provide settings for braintree and set up
## your account to reject invalid CVV and AVS responses
import braintree_configuration


## For information on how to trigger specific errors, see http://www.braintreepayments.com/docs/python/reference/processor_responses


def transact(desired_errors, price, number='4' + '1' * 15, month='12', year='2030', **kwargs):
    try:
        transaction = dinero.Transaction.create(price, number=number, month=month, year=year, **kwargs)
    except PaymentException as e:
        if not desired_errors:
            assert False, e
        else:
            for error in desired_errors:
                assert error in e
    else:
        assert not desired_errors, 'was supposed to throw %s' % str(desired_errors)
        return transaction


def test_successful():
    transact([], price='2.00')


def test_avs():
    # AVS data provided is invalid or AVS is not allowed for the card type that was used.
    transact([AVSError], price='2059', zip=46203)


def test_cvv():
    # CVV Code N, does not match
    transact([CVVError], price='2010', cvv=901)


def test_cvv_and_avs():
    transact([CVVError, AVSError], price='2060', cvv=901, zip=46203)


def test_expiry():
    transact([ExpiryError], price='2004.00', year='2010')


def test_invalid_card():
    transact([InvalidCardError], price='2005', number='4' + '1' * 14)


# def test_invalid_card_and_expiry():
#     """
#     FAILS :-(
#     """
#     transact([InvalidCardError, ExpiryError], price='2005', number='4' + '1' * 14, month='12', year='2010')


def test_invalid_amount():
    transact([InvalidAmountError], -1)


def test_declined():
    transact([CardDeclinedError], price='2000')


def test_duplicate():
    transact([], price='3.00')
    transact([DuplicateTransactionError], price='3.00')


def test_cant_refund_unsettled():
    transaction = transact([], price='4.00')
    try:
        dinero.get_gateway().refund(transaction, transaction.price)
    except PaymentException as e:
        assert RefundError in e
    else:
        assert False, "must raise an exception"


def test_cant_refund_more():
    transaction = transact([], price='5.00')
    try:
        dinero.get_gateway().refund(transaction, transaction.price + 1)
    except PaymentException as e:
        assert RefundError in e
    else:
        assert False, "must raise an exception"


def test_invalid_transaction():
    transaction = transact([], price='6.00')
    transaction.transaction_id = '0'
    try:
        dinero.get_gateway().refund(transaction, transaction.price)
    except PaymentException as e:
        assert InvalidTransactionError in e
    else:
        assert False, "must raise an exception"
