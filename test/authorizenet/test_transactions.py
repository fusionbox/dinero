import random
from functools import partial

from test.utils import assertRaisesError, transact

import dinero
from dinero.exceptions import (
    AVSError, CVVError, InvalidCardError, InvalidAmountError, RefundError,
    ExpiryError, CardDeclinedError, DuplicateTransactionError,
)


# For information on how to trigger specific errors, see
# http://community.developer.authorize.net/t5/Integration-and-Testing/Triggering-Specific-Transaction-Responses-Using-Test-Account/td-p/4361


transact = partial(transact, gateway_name='authorize.net')


def test_successful():
    transact()


def test_successful_with_customer():
    transact(customer_id=123, email='joeyjoejoejunior@example.com')


def test_successful_retrieve():
    transaction = transact()
    transaction_retrieved = dinero.Transaction.retrieve(transaction.transaction_id, gateway_name='authorize.net')
    assert transaction == transaction_retrieved, 'Transactions are not "equal"'


def test_successful_retrieve_with_customer():
    transaction = transact(customer_id=123, email='joeyjoejoejunior@example.com')
    transaction_retrieved = dinero.Transaction.retrieve(transaction.transaction_id, gateway_name='authorize.net')
    assert transaction == transaction_retrieved, 'Transactions are not "equal"'
    assert transaction_retrieved.customer_id == 123, 'Transaction.customer_id is not 123, it is %s' % repr(transaction_retrieved.customer_id)
    assert transaction_retrieved.email == 'joeyjoejoejunior@example.com', 'Transaction.email is not "joeyjoejoejunior@example.com", it is %s' % repr(transaction_retrieved.email)


def test_avs():
    # AVS data provided is invalid or AVS is not allowed for the card type that was used.
    with assertRaisesError(AVSError):
        transact(zip=46203)

    # Address: No Match ZIP Code: No Match
    with assertRaisesError(AVSError):
        transact(zip=46205)


def test_cvv():
    # CVV Code N, does not match
    with assertRaisesError(CVVError):
        transact(cvv=901)


def test_cvv_and_avs():
    with assertRaisesError(CVVError, AVSError):
        transact(cvv=901, zip=46203)


def test_expiry():
    with assertRaisesError(ExpiryError):
        transact(year='2010')


def test_invalid_card():
    with assertRaisesError(InvalidCardError):
        transact(number='4' + '1' * 14)


def test_invalid_card_and_expiry():
    with assertRaisesError(InvalidCardError, ExpiryError):
        transact(number='4' + '1' * 14, month='12', year='2010')


def test_invalid_amount():
    with assertRaisesError(InvalidAmountError):
        transact(-1)


def test_declined():
    with assertRaisesError(CardDeclinedError):
        transact(zip=46282)


def test_duplicate():
    price = float(random.randint(100000, 1000000)) / 100
    transact(price)
    with assertRaisesError(DuplicateTransactionError):
        transact(price)


def test_cant_refund_unsettled():
    txn = transact()
    with assertRaisesError(RefundError):
        dinero.get_gateway('authorize.net').refund(txn, txn.price)


def test_cant_refund_more():
    txn = transact()
    with assertRaisesError(RefundError):
        dinero.get_gateway('authorize.net').refund(txn, txn.price + 1)


# Authorize.Net stopped returning a valid response for this in development
# mode.
#
# def test_invalid_txn():
#     txn = transact()
#     txn.transaction_id = '0'
#     with assertRaisesError(InvalidTransactionError):
#         dinero.get_gateway('authorize.net').refund(txn, txn.price)
