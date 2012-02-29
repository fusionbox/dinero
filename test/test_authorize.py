import random
import dinero
from dinero.exceptions import *

## These tests require that you provide settings for authorize.net and set up
## your account to reject invalid CVV and AVS responses
import authorize_net_configuration


## For information on how to trigger specific errors, see http://community.developer.authorize.net/t5/Integration-and-Testing/Triggering-Specific-Transaction-Responses-Using-Test-Account/td-p/4361


def transact(desired_errors, price=None, number='4' + '1' * 15, month='12', year='2030', **kwargs):
    if not price:
        price = float(random.randint(1, 100000)) / 100

    try:
        transaction = dinero.Transaction.create(price, number=number, month=month, year=year, **kwargs)
    except PaymentException as e:
        for error in desired_errors:
            assert error in e
        assert desired_errors
    else:
        assert not desired_errors, 'was supposed to throw %s' % str(desired_errors)
        return transaction


def test_avs():
    # AVS data provided is invalid or AVS is not allowed for the card type that was used.
    transact([AVSError], zip=46203)

    # Address: No Match ZIP Code: No Match
    transact([AVSError], zip=46205)


def test_cvv():
    # CVV Code N, does not match
    transact([CVVError], cvv=901)


def test_cvv_and_avs():
    transact([CVVError, AVSError], cvv=901, zip=46203)


def test_expiry():
    transact([ExpiryError], year='2010')


def test_invalid_card():
    transact([InvalidCardError], number='4' + '1' * 14)


def test_invalid_card_and_expiry():
    transact([InvalidCardError, ExpiryError], number='4' + '1' * 14, month='12', year='2010')


def test_invalid_amount():
    transact([InvalidAmountError], -1)


def test_declined():
    transact([CardDeclinedError], zip=46282)


def test_duplicate():
    price = float(random.randint(100000, 1000000)) / 100
    transact([], price)
    transact([DuplicateTransactionError], price)


def test_successful():
    transact([])


def test_cant_refund_unsettled():
    txn = transact([])
    try:
        dinero.get_gateway().refund(txn, txn.price)
    except PaymentException as e:
        assert RefundError in e
    else:
        assert False, "must raise an exception"


def test_cant_refund_more():
    txn = transact([])
    try:
        dinero.get_gateway().refund(txn, txn.price + 1)
    except PaymentException as e:
        assert RefundError in e
    else:
        assert False, "must raise an exception"


def test_invalid_txn():
    txn = transact([])
    txn.transaction_id = '0'
    try:
        dinero.get_gateway().refund(txn, txn.price)
    except PaymentException as e:
        assert InvalidTransactionError in e
    else:
        assert False, "must raise an exception"
