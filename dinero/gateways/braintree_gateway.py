import braintree
from braintree.exceptions import NotFoundError

from dinero.exceptions import *
from dinero.gateways.base import Gateway


CREDITCARD_ERRORS = {
    '91701': [GatewayException],  # Cannot provide both a billing address and a billing address ID.
    '91702': [GatewayException],  # Billing address ID is invalid.
    '91704': [GatewayException],  # Customer ID is required.
    '91705': [GatewayException],  # Customer ID is invalid.
    '91708': [InvalidCardError],  # Cannot provide expiration_date if you are also providing expiration_month and expiration_year.
    '91718': [GatewayException],  # Token is invalid.
    '91719': [GatewayException],  # Credit card token is taken.
    '91720': [GatewayException],  # Credit card token is too long.
    '91721': [GatewayException],  # Token is not an allowed token.
    '91722': [GatewayException],  # Payment method token is required.
    '81723': [InvalidCardError],  # Cardholder name is too long.
    '81703': [InvalidCardError],  # Credit card type is not accepted by this merchant account.
    '81718': [GatewayException],  # Credit card number cannot be updated to an unsupported card type when it is associated to subscriptions.
    '81706': [InvalidCardError],  # CVV is required.
    '81707': [InvalidCardError],  # CVV must be 3 or 4 digits.
    '81709': [InvalidCardError],  # Expiration date is required.
    '81710': [InvalidCardError],  # Expiration date is invalid.
    '81711': [InvalidCardError],  # Expiration date year is invalid.
    '81712': [InvalidCardError],  # Expiration month is invalid.
    '81713': [InvalidCardError],  # Expiration year is invalid.
    '81714': [InvalidCardError],  # Credit card number is required.
    '81715': [InvalidCardError],  # Credit card number is invalid.
    '81716': [InvalidCardError],  # Credit card number must be 12-19 digits.
    '81717': [InvalidCardError],  # Credit card number is not an accepted test number.
    '91723': [GatewayException],  # Update Existing Token is invalid.
}

CUSTOMER_ERRORS = {
    '91602': [GatewayException],  # Custom field is invalid.
    '91609': [GatewayException],  # Customer ID has already been taken.
    '91610': [GatewayException],  # Customer ID is invalid.
    '91611': [GatewayException],  # Customer ID is not an allowed ID.
    '91612': [GatewayException],  # Customer ID is too long.
    '91613': [GatewayException],  # Id is required
    '81601': [GatewayException],  # Company is too long.
    '81603': [GatewayException],  # Custom field is too long.
    '81604': [GatewayException],  # Email is an invalid format.
    '81605': [GatewayException],  # Email is too long.
    '81606': [GatewayException],  # Email is required if sending a receipt.
    '81607': [GatewayException],  # Fax is too long.
    '81608': [GatewayException],  # First name is too long.
    '81613': [GatewayException],  # Last name is too long.
    '81614': [GatewayException],  # Phone is too long.
    '81615': [GatewayException],  # Website is too long.
    '81616': [GatewayException],  # Website is an invalid format.
}

ADDRESS_ERRORS = {
    '81801': [GatewayException],  # Address must have at least one field fill in.
    '81802': [GatewayException],  # Company is too long.
    '81804': [GatewayException],  # Extended address is too long.
    '81805': [GatewayException],  # First name is too long.
    '81806': [GatewayException],  # Last name is too long.
    '81807': [GatewayException],  # Locality is too long.
    '81813': [GatewayException],  # Postal code can only contain letters, numbers, spaces, and hyphens.
    '81808': [GatewayException],  # Postal code is required.
    '81809': [GatewayException],  # Postal code may contain no more than 9 letter or number characters.
    '81810': [GatewayException],  # Region is too long.
    '81811': [GatewayException],  # Street address is required.
    '81812': [GatewayException],  # Street address is too long.
    '91803': [GatewayException],  # Country name is not an accepted country.
    '91815': [GatewayException],  # Inconsistent country
    '91816': [GatewayException],  # Country code alpha-3 is not accepted
    '91817': [GatewayException],  # Country code numeric is not accepted
    '91814': [GatewayException],  # Country code alpha-2 is not accepted
    '91818': [GatewayException],  # Too many addresses per customer
}

TRANSACTION_ERRORS = {
    '81501': [InvalidAmountError],  # Amount cannot be negative.
    '81502': [InvalidAmountError],  # Amount is required.
    '81503': [InvalidAmountError],  # Amount is an invalid format.
    '81528': [InvalidAmountError],  # Amount is too large.
    '81509': [InvalidTransactionError],  # Credit card type is not accepted by this merchant account.
    '81527': [InvalidTransactionError],  # Custom field is too long.
    '91501': [InvalidTransactionError],  # Order ID is too long.
    '91530': [InvalidTransactionError],  # Cannot provide a billing address unless also providing a credit card.
    '91504': [RefundError],              # Transaction can only be voided if status is authorized or submitted_for_settlement.
    '91505': [RefundError],              # Cannot refund credit
    '91506': [RefundError],              # Cannot refund a transaction unless it is settled.
    '91507': [RefundError],              # Cannot submit for settlement unless status is authorized.
    '91508': [InvalidTransactionError],  # Need a customer_id, payment_method_token, credit_card, or subscription_id.
    '91526': [InvalidTransactionError],  # Custom field is invalid
    '91510': [InvalidTransactionError],  # Customer ID is invalid.
    '91511': [InvalidTransactionError],  # Customer does not have any credit cards.
    '91512': [InvalidTransactionError],  # Transaction has already been refunded.
    '91513': [InvalidTransactionError],  # Merchant account ID is invalid.
    '91514': [InvalidTransactionError],  # Merchant account is suspended.
    '91515': [InvalidTransactionError],  # Cannot provide both payment_method_token and credit_card attributes.
    '91516': [InvalidTransactionError],  # Cannot provide both payment_method_token and customer_id unless the payment_method belongs to the customer.
    '91527': [InvalidTransactionError],  # Cannot provide both payment_method_token and subscription_id unless the payment method belongs to the subscription.
    '91517': [InvalidTransactionError],  # Credit card type is not accepted by this merchant account.
    '91518': [InvalidTransactionError],  # Payment method token is invalid.
    '91519': [InvalidTransactionError],  # Processor authorization code cannot be set unless for a voice authorization.
    '91521': [InvalidTransactionError],  # Refund amount cannot be more than the authorized amount.
    '91538': [InvalidTransactionError],  # Cannot refund transaction with suspended merchant account.
    '91522': [InvalidTransactionError],  # Settlement amount cannot be more than the authorized amount.
    '91529': [InvalidTransactionError],  # Cannot provide both subscription_id and customer_id unless the subscription belongs to the customer.
    '91528': [InvalidTransactionError],  # Subscription ID is invalid.
    '91523': [InvalidTransactionError],  # Transaction type is invalid.
    '91524': [InvalidTransactionError],  # Transaction type is required.
    '91525': [InvalidTransactionError],  # Vault is disabled.
    '91531': [InvalidTransactionError],  # Subscription status must be past due
    '91547': [InvalidTransactionError],  # Merchant Account does not support refunds
    '81531': [InvalidAmountError],  # Amount must be greater than zero
    '81534': [InvalidAmountError],  # Tax amount cannot be negative.
    '81535': [InvalidAmountError],  # Tax amount is an invalid format.
    '81536': [InvalidAmountError],  # Tax amount is too large.
    '91537': [InvalidTransactionError],  # Purchase order number is too long.
    '91539': [InvalidTransactionError],  # Voice Authorization is not allowed for this card type
    '91540': [InvalidTransactionError],  # Transaction cannot be cloned if payment method is stored in vault
    '91541': [InvalidTransactionError],  # Cannot clone voice authorization transactions
    '91542': [InvalidTransactionError],  # Unsuccessful transaction cannot be cloned.
    '91543': [InvalidTransactionError],  # Credits cannot be cloned.
    '91544': [InvalidTransactionError],  # Cannot clone transaction without submit_for_settlement flag.
    '91545': [InvalidTransactionError],  # Voice Authorizations are not supported for this processor
    '91546': [InvalidTransactionError],  # Credits are not supported by this processor
    '91548': [InvalidTransactionError],  # Purchase order number is invalid
}

VALIDATION_ERRORS = {}  # all the dictionaries
VALIDATION_ERRORS.update(CREDITCARD_ERRORS)
VALIDATION_ERRORS.update(CUSTOMER_ERRORS)
VALIDATION_ERRORS.update(ADDRESS_ERRORS)
VALIDATION_ERRORS.update(TRANSACTION_ERRORS)

GATEWAY_REJECTION_REASONS = {
    'avs':         [AVSError],
    'avs_and_cvv': [AVSError, CVVError],
    'cvv':         [CVVError],
    'duplicate':   [DuplicateTransactionError],
}

PROCESSOR_RESPONSE_ERRORS = {
    '2000': [CardDeclinedError],          # Do Not Honor
    '2001': [CardDeclinedError],          # Insufficient Funds
    '2002': [CardDeclinedError],          # Limit Exceeded
    '2003': [CardDeclinedError],          # Cardholder's Activity Limit Exceeded
    '2004': [ExpiryError],                # Expired Card
    '2005': [InvalidCardError],           # Invalid Credit Card Number
    '2006': [ExpiryError],                # Invalid Expiration Date
    '2007': [InvalidCardError],           # No Account
    '2008': [InvalidCardError],           # Card Account Length Error
    '2009': [InvalidTransactionError],    # No Such Issuer
    '2010': [CVVError],                   # Card Issuer Declined CVV
    '2011': [CardDeclinedError],          # Voice Authorization Required
    '2012': [CardDeclinedError],          # Voice Authorization Required - Possible Lost Card
    '2013': [CardDeclinedError],          # Voice Authorization Required - Possible Stolen Card
    '2014': [CardDeclinedError],          # Voice Authorization Required - Fraud Suspected
    '2015': [CardDeclinedError],          # Transaction Not Allowed
    '2016': [DuplicateTransactionError],  # Duplicate Transaction
    '2017': [CardDeclinedError],          # Cardholder Stopped Billing
    '2018': [CardDeclinedError],          # Cardholder Stopped All Billing
    '2019': [InvalidTransactionError],    # Invalid Transaction
    '2020': [CardDeclinedError],          # Violation
    '2021': [CardDeclinedError],          # Security Violation
    '2022': [CardDeclinedError],          # Declined - Updated Cardholder Available
    '2023': [InvalidTransactionError],    # Processor Does Not Support This Feature
    '2024': [InvalidTransactionError],    # Card Type Not Enabled
    '2025': [InvalidTransactionError],    # Set Up Error - Merchant
    '2026': [InvalidTransactionError],    # Invalid Merchant ID
    '2027': [InvalidTransactionError],    # Set Up Error - Amount
    '2028': [InvalidTransactionError],    # Set Up Error - Hierarchy
    '2029': [InvalidTransactionError],    # Set Up Error - Card
    '2030': [InvalidTransactionError],    # Set Up Error - Terminal
    '2031': [InvalidTransactionError],    # Encryption Error
    '2032': [InvalidTransactionError],    # Surcharge Not Permitted
    '2033': [InvalidTransactionError],    # Inconsistent Data
    '2034': [InvalidTransactionError],    # No Action Taken
    '2035': [CardDeclinedError],          # Partial Approval For Amount In Group III Version
    '2036': [RefundError],                # Authorization could not be found to reverse
    '2037': [RefundError],                # Already Reversed
    '2038': [CardDeclinedError],          # Processor Declined
    '2039': [InvalidTransactionError],    # Invalid Authorization Code
    '2040': [InvalidTransactionError],    # Invalid Store
    '2041': [CardDeclinedError],          # Declined - Call For Approval
    '2043': [CardDeclinedError],          # Error - Do Not Retry, Call Issuer
    '2044': [CardDeclinedError],          # Declined - Call Issuer
    '2045': [CardDeclinedError],          # Invalid Merchant Number
    '2046': [CardDeclinedError],          # Declined
    '2047': [CardDeclinedError],          # Call Issuer. Pick Up Card.
    '2048': [InvalidAmountError],         # Invalid Amount
    '2049': [InvalidTransactionError],    # Invalid SKU Number
    '2050': [InvalidTransactionError],    # Invalid Credit Plan
    '2051': [InvalidTransactionError],    # Credit Card Number does not match method of payment
    '2052': [InvalidTransactionError],    # Invalid Level III Purchase
    '2053': [CardDeclinedError],          # Card reported as lost or stolen
    '2054': [RefundError],                # Reversal amount does not match authorization amount
    '2055': [InvalidTransactionError],    # Invalid Transaction Division Number
    '2056': [InvalidTransactionError],    # Transaction amount exceeds the transaction division limit
    '2057': [CardDeclinedError],          # Issuer or Cardholder has put a restriction on the card
    '2058': [CardDeclinedError],          # Merchant not MasterCard SecureCode enabled.
    '2059': [AVSError],                   # Address Verification Failed
    '2060': [AVSError, CVVError],         # Address Verification and Card Security Code Failed
}


def _convert_amount(price):
    if isinstance(price, str):
        amount = price
        price = float(price)
    else:
        amount = '%.2f' % float(price)
    return amount, price


def check_for_errors(result):
    if not result.is_success:
        if result.transaction:
            if result.transaction.gateway_rejection_reason:
                raise PaymentException([
                    # instantiate an exception for every class in GATEWAY_REJECTION_REASONS[result.transaction.gateway_rejection_reason]
                    error_class(result.transaction.processor_response_text) for error_class in GATEWAY_REJECTION_REASONS[result.transaction.gateway_rejection_reason]
                    ])
            if result.transaction.processor_response_code in PROCESSOR_RESPONSE_ERRORS:
                raise PaymentException([
                    # instantiate an exception for every class in PROCESSOR_RESPONSE_ERRORS[result.transaction.processor_response_code]
                    error_class(result.transaction.processor_response_text) for error_class in PROCESSOR_RESPONSE_ERRORS[result.transaction.processor_response_code]
                    ])
            raise PaymentException(result.transaction.processor_response_text)

        # sometimes duplicate errors are returned, don't know why, but let's just use one.
        error_codes = {}
        for error in result.errors.deep_errors:
            print vars(error)
            if error.code in VALIDATION_ERRORS:
                error_codes[error.code] = [
                    # instantiate an exception for every class in VALIDATION_ERRORS[error.code]
                    error_class(error.message) for error_class in VALIDATION_ERRORS[error.code]
                    ]
            else:
                error_codes[error.code] = [GatewayException(error.message)]
        flattened_errors = []
        for errors in error_codes.values():
            flattened_errors.extend(errors)
        raise PaymentException(flattened_errors)


class Braintree(Gateway):
    def __init__(self, options):
        environment = braintree.Environment.Sandbox  # TODO: autodetect live vs. test

        braintree.Configuration.configure(
                environment,
                options['merchant_id'],
                options['public_key'],
                options['private_key'],
                )

    def charge(self, price, options):
        amount, price = _convert_amount(price)

        credit_card = {
            'number': str(options['number']),
            'expiration_month': str(options['month']).zfill(2),
            'expiration_year': str(options['year']),
        }
        if options.get('cvv'):
            credit_card['cvv'] = options['cvv']

        billing = {}
        billing_fields = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'street_address': 'address',
            'locality': 'city',
            'region': 'state',
            'postal_code': 'zip',
            'country_name': 'country',
        }
        for braintree_field, field in billing_fields.iteritems():
            if field in options:
                billing[braintree_field] = options[field]

        result = braintree.Transaction.sale({
            'amount': amount,
            'credit_card': credit_card,
            'billing': billing,
            'options': {
                'submit_for_settlement': True,
            },
        })

        check_for_errors(result)
        return {
                'price': price,
                'transaction_id': result.transaction.id,
                }

    def void(self, transaction):
        try:
            result = braintree.Transaction.void(transaction.transaction_id, amount)
        except NotFoundError as e:
            raise PaymentException([InvalidTransactionError(e)])

        check_for_errors(result)
        return True

    def refund(self, transaction, price):
        amount, price = _convert_amount(price)

        try:
            result = braintree.Transaction.refund(transaction.transaction_id, amount)
        except NotFoundError as e:
            raise PaymentException([InvalidTransactionError(e)])

        check_for_errors(result)
        return True

    def retrieve(self, transaction_id):
        raise NotImplementedError

    def create_customer(self):
        raise NotImplementedError

    def update_customer(self, customer_id):
        raise NotImplementedError

    def delete_customer(self, customer_id):
        raise NotImplementedError
