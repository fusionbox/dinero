import re
import braintree
from braintree.exceptions import (
    NotFoundError,
    AuthenticationError as BraintreeAuthenticationError,
    )

from dinero.exceptions import *
from dinero.gateways.base import Gateway


# CVV RESPONSES
# M = Match
# N = Does not Match
# U = Not Verified
# I = Not Provided
# A = Not Applicable
CVV_SUCCESSFUL_RESPONSES = ['M']

# AVS POSTAL CODE RESPONSE CODE
# M = Matches
# N = Does not Match
# U = Not Verified
# I = Not Provided
# A = Not Applicable
AVS_ZIP_SUCCESSFUL_RESPONSES = ['M'],

# AVS STREET ADDRESS CODE RESPONSE CODE
# M = Matches
# N = Does not Match
# U = Not Verified
# I = Not Provided
# A = Not Applicable
AVS_ADDRESS_SUCCESSFUL_RESPONSES = ['M']


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
    '81715': [InvalidTransactionError],  # Credit card number is invalid.
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


def check_for_transaction_errors(result):
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

        check_for_errors(result)


def check_for_errors(result):
    if not result.is_success:
        error_codes = {}
        for error in result.errors.deep_errors:
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
        if not flattened_errors:
            PaymentException([result.message])
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

        # Auto-discover if this is a real account or a developer account.  Tries
        # to access both end points and see which one works.
        try:
            self.retrieve('0')
        except BraintreeAuthenticationError:
            environment = braintree.Environment.Production  # TODO: autodetect live vs. test

            braintree.Configuration.configure(
                    environment,
                    options['merchant_id'],
                    options['public_key'],
                    options['private_key'],
                    )
        except PaymentException:
            pass

    def charge(self, price, options):
        amount, price = _convert_amount(price)

        submit = {
            'amount': amount,
            'options': {
                'submit_for_settlement': True,
            },
        }

        if 'customer' in options:
            submit['customer_id'] = options['customer'].customer_id
            if 'credit_card_token' in options:
                submit['payment_method_token'] = options['credit_card_token']
        else:
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

            customer = {}
            customer_fields = {
                'first_name': 'first_name',
                'last_name': 'last_name',
                'email': 'email',
                'website': 'website',
                'company': 'company',
            }
            for braintree_field, field in customer_fields.iteritems():
                if field in options:
                    customer[braintree_field] = options[field]

            submit['credit_card'] = credit_card
            submit['billing'] = billing
            if customer:
                submit['customer'] = customer

        result = braintree.Transaction.sale(submit)

        check_for_transaction_errors(result)
        return self._transaction_to_transaction_dict(result.transaction)

    def _transaction_to_transaction_dict(self, transaction):
        try:
            print(transaction.customer)
        except:
            pass

        ret = {
            'transaction_id': transaction.id,
            'avs_zip_successful': transaction.avs_postal_code_response_code in AVS_ZIP_SUCCESSFUL_RESPONSES,
            'avs_address_successful': transaction.avs_street_address_response_code in AVS_ADDRESS_SUCCESSFUL_RESPONSES,
            'cvv_successful': transaction.cvv_response_code in CVV_SUCCESSFUL_RESPONSES,
            'auth_code': transaction.processor_authorization_code,
            'price': transaction.amount,
            'account_number': transaction.credit_card_details.masked_number,
            'card_type': transaction.credit_card_details.card_type,
            'last_4': transaction.credit_card_details.last_4,
        }
        ret['avs_successful'] = ret['avs_zip_successful'] and ret['avs_address_successful']
        if transaction.customer:
            ret.update({
                'first_name': transaction.customer['first_name'],
                'last_name': transaction.customer['last_name'],
                'email': transaction.customer['email'],
                'website': transaction.customer['website'],
                'company': transaction.customer['company'],
                })

        if transaction.custom_fields:
            for field, value in transaction.custom_fields.iteritems():
                ret[field] = value

        return ret

    def void(self, transaction):
        try:
            result = braintree.Transaction.void(transaction.transaction_id)
        except NotFoundError as e:
            raise PaymentException([InvalidTransactionError(e)])

        check_for_transaction_errors(result)
        return True

    def refund(self, transaction, price):
        amount, price = _convert_amount(price)

        try:
            result = braintree.Transaction.refund(transaction.transaction_id, amount)
        except NotFoundError as e:
            raise PaymentException([InvalidTransactionError(e)])

        check_for_transaction_errors(result)
        return True

    def retrieve(self, transaction_id):
        try:
            result = braintree.Transaction.find(transaction_id)
        except NotFoundError as e:
            raise PaymentException([InvalidTransactionError(e)])

        return self._transaction_to_transaction_dict(result)

    def create_customer(self, options):
        customer, address, credit_card = self._create_all_from_dict(options)
        try:
            result = braintree.Customer.create(customer)
            check_for_errors(result)
            if address:
                address['customer_id'] = result.customer.id
                address_result = braintree.Address.create(address)
                if not address_result.is_success:
                    result.braintree.Customer.delete(result.customer.id)
                    check_for_errors(address_result)
                result.customer.addresses = [address_result.address]

            if credit_card:
                credit_card['customer_id'] = result.customer.id
                credit_card_result = braintree.CreditCard.create(credit_card)
                if not credit_card_result.is_success:
                    result.braintree.Customer.delete(result.customer.id)
                    check_for_errors(credit_card_result)
                result.customer.credit_cards = [credit_card_result.credit_card]

        except NotFoundError as e:
            raise PaymentException([InvalidTransactionError(e)])

        profile = {}
        profile.update(options)
        profile['customer_id'] = result.customer.id

        return profile

    def retrieve_customer(self, customer_id):
        try:
            customer_result = braintree.Customer.find(str(customer_id))
        except NotFoundError as e:
            raise CustomerNotFoundError(e)

        return self._customer_from_customer_result(customer_result)

    def delete_customer(self, customer_id):
        try:
            result = braintree.Customer.delete(str(customer_id))
        except NotFoundError as e:
            raise CustomerNotFoundError(e)

        check_for_errors(result)
        return True

    def update_customer(self, customer_id, options):
        customer, address, credit_card = self._create_all_from_dict(options)

        credit_card_token = None
        address_id = None
        try:
            credit_card_token = options['credit_card_token']
        except KeyError:
            customer_result = braintree.Customer.find(customer_id)
            if customer_result.credit_cards:
                credit_card_token = customer_result.credit_cards[0].token

        try:
            address_id = options['address_id']
        except KeyError:
            customer_result = braintree.Customer.find(customer_id)
            if customer_result.addresses:
                address_id = customer_result.addresses[0].id

        try:
            if customer:
                customer_result = braintree.Customer.update(customer_id, customer)
                check_for_errors(customer_result)

            if address and address_id:
                address_result = braintree.Address.update(customer_id, address_id, address)
                check_for_errors(address_result)

            if credit_card and credit_card_token:
                credit_card_result = braintree.CreditCard.update(credit_card_token, credit_card)
                check_for_errors(credit_card_result)
        except NotFoundError as e:
            raise CustomerNotFoundError(e)

        return True

    def _customer_from_customer_result(self, customer_result):
        ret = {}

        gets = {
            'customer_id':                 'id',
            'first_name':                  'first_name',
            'last_name':                   'last_name',
            'company':                     'company',
            'phone':                       'phone',
            'fax':                         'fax',
            'address':                     'addresses[0].street_address',
            'state':                       'addresses[0].locality',
            'city':                        'addresses[0].region',
            'zip':                         'addresses[0].postal_code',
            'country':                     'addresses[0].country_code_alpha2',
            'last_4':                      'credit_cards[0].last_4',
            # braintree specific
            'credit_card_token':           'credit_cards[0].token',
            'address_id':                  'addresses[0].id',
        }

        for key, kvp in gets.iteritems():
            try:
                kvp = kvp.replace('[', '.').replace(']', '')
                search = kvp.split('.')
                val = customer_result
                while search:
                    current_key = search.pop(0)
                    if re.match('[0-9]+$', current_key):
                        val = val[int(current_key)]
                    else:
                        val = getattr(val, current_key)

                ret[key] = val
            except KeyError:
                pass

        if 'last_4' in ret:
            ret['number'] = 'X' * 12 + ret['last_4']
            # now it's in the form "XXXXXXXXXXXX1234"

        return ret

    def _create_all_from_dict(self, options):
        customer = {}
        address = {}
        credit_card = {}

        customer_fields = {
            'email': 'email',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'company': 'company',
            'phone': 'phone',
            'fax': 'fax',
        }
        for field, braintree_field in customer_fields.iteritems():
            if field in options:
                customer[braintree_field] = options[field]

        address_fields = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'company': 'company',
            'address': 'street_address',
            'state': 'locality',
            'city': 'region',
            'zip': 'postal_code',
            'country': 'country_name',
        }
        for field, braintree_field in address_fields.iteritems():
            if field in options:
                address[braintree_field] = options[field]

        credit_card_fields = {
            # 'merchant_account_id': self.gateway_options['merchant_id'],
            'number': 'number',
            'month': 'expiration_month',
            'year': 'expiration_year',
        }
        for field, braintree_field in credit_card_fields.iteritems():
            if field in options:
                credit_card[braintree_field] = options[field]

        if address:
            credit_card['billing_address'] = address

        return customer, address, credit_card
