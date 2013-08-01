import os
import random
import dinero
from dinero.exceptions import *

## These tests require that you provide settings for authorize.net and set up
## your account to reject invalid CVV and AVS responses
try:
    import authorize_net_configuration
except ImportError:
    LOGIN_ID = os.environ["AUTHNET_LOGIN_ID"]
    TRANSACTION_KEY = os.environ["AUTHNET_TRANSACTION_KEY"]
    dinero.configure({
        'auth.net': {
            'type': 'dinero.gateways.AuthorizeNet',
            'login_id': LOGIN_ID,
            'transaction_key': TRANSACTION_KEY,
            'default': True,
        }
    })


## For information on how to trigger specific errors, see http://community.developer.authorize.net/t5/Integration-and-Testing/Triggering-Specific-Transaction-Responses-Using-Test-Account/td-p/4361


def transact(desired_errors, price=None, number='4' + '1' * 15, month='12', year='2030', **kwargs):
    if not price:
        price = float(random.randint(1, 100000)) / 100

    try:
        transaction = dinero.Transaction.create(price, number=number, month=month, year=year, gateway_name='authorize.net', **kwargs)
    except PaymentException as e:
        if not desired_errors:
            print repr(e)
            assert False, e.message
        else:
            for error in desired_errors:
                assert error in e, str(error) + ' not in desired_errors'
    else:
        assert not desired_errors, 'was supposed to throw %s' % str(desired_errors)
        return transaction


def test_successful():
    transact([])


def test_successful_with_customer():
    transact([], customer_id=123, email='joeyjoejoejunior@example.com')


def test_successful_retrieve():
    transaction = transact([])
    transaction_retrieved = dinero.Transaction.retrieve(transaction.transaction_id, gateway_name='authorize.net')
    assert transaction == transaction_retrieved, 'Transactions are not "equal"'


def test_successful_retrieve_with_customer():
    transaction = transact([], customer_id=123, email='joeyjoejoejunior@example.com')
    transaction_retrieved = dinero.Transaction.retrieve(transaction.transaction_id, gateway_name='authorize.net')
    assert transaction == transaction_retrieved, 'Transactions are not "equal"'
    assert transaction_retrieved.customer_id == 123, 'Transaction.customer_id is not 123, it is %s' % repr(transaction_retrieved.customer_id)
    assert transaction_retrieved.email == 'joeyjoejoejunior@example.com', 'Transaction.email is not "joeyjoejoejunior@example.com", it is %s' % repr(transaction_retrieved.email)


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


def test_cant_refund_unsettled():
    txn = transact([])
    try:
        dinero.get_gateway('authorize.net').refund(txn, txn.price)
    except PaymentException as e:
        assert RefundError in e
    else:
        assert False, "must raise an exception"


def test_cant_refund_more():
    txn = transact([])
    try:
        dinero.get_gateway('authorize.net').refund(txn, txn.price + 1)
    except PaymentException as e:
        assert RefundError in e
    else:
        assert False, "must raise an exception"


# def test_invalid_txn():
#     """
#     FAILS
#     """
#     txn = transact([])
#     txn.transaction_id = '0'
#     try:
#         dinero.get_gateway('authorize.net').refund(txn, txn.price)
#     except PaymentException as e:
#         assert InvalidTransactionError in e
#     else:
#         assert False, "must raise an exception"
