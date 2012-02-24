from __future__ import division
import re
import requests
from lxml import etree

from dinero.ordereddict import OrderedDict
from dinero.exceptions import *
from dinero.gateways.base import Gateway

from datetime import date


def xml_post(url, obj):
    resp = requests.post(
            url,
            data=etree.tostring(obj),
            headers={'content-type': 'application/xml'},
            verify=True,
            )

    content = resp.content
    if isinstance(content, unicode) and content[0] == u'\ufeff':
        # authorize.net puts a BOM in utf-8. Shame.
        content = content[1:]
    content = str(content)
    return etree.XML(content)


def prepare_number(number):
    return re.sub('[^0-9Xx]', '', number)


def handle_value(root, key, value):
    if value is not None:
        sub = etree.SubElement(root, key)

        if isinstance(value, dict):
            dict_to_xml(sub, value)
        elif value:
            sub.text = str(value)


def dict_to_xml(root, dictionary, ns=None):
    if isinstance(root, basestring):
        if ns is None:
            nsmap = None
        else:
            nsmap = {None: ns}
        root = etree.Element(root, nsmap=nsmap)

    for key, value in dictionary.iteritems():
        if isinstance(value, list):
            for item in value:
                handle_value(root, key, item)
        else:
            handle_value(root, key, value)

    return root


def get_tag(elem):
    return elem.tag.partition('}')[2] or elem.tag


def xml_to_dict(parent):
    ret = OrderedDict()

    parent_tag = get_tag(parent)
    if parent_tag in ('messages', 'errors'):
        ret[parent_tag[:-1]] = []

    for child in parent:
        tag = get_tag(child)

        if len(child):
            child_value = xml_to_dict(child)
        else:
            child_value = child.text and child.text.strip() or ''

        if tag in ret and isinstance(ret[tag], list):
            x = ret[tag]
            del(ret[tag])
            ret[tag] = x

            ret[tag].append(child_value)
        else:
            ret[tag] = child_value

    return ret


def get_first_of(dict, possibilities, default=None):
    for i in possibilities:
        if i in dict:
            return dict[i]

    return default


RESPONSE_CODE_EXCEPTION_MAP = {
        '8': [ExpiryError],
        '6': [CardInvalidError],
        '37': [CardInvalidError],
        '5': [InvalidAmountError],
        '27': [AVSError],
        '65': [CVVError],
        '45': [AVSError, CVVError],
        '2': [CardDeclinedError],
        '11': [DuplicateTransactionError],
        '54': [RefundError],
        '33': [InvalidTransactionError],
        '44': [CVVError],
        }


def payment_exception_factory(errors):
    exceptions = []
    for code, message in errors:
        try:
            exceptions.extend(exception_class(message) for exception_class in RESPONSE_CODE_EXCEPTION_MAP[code])
        except KeyError:
            raise Exception("I don't recognize this error: {0!r}. Better call the programmers.".format(errors))
    return exceptions


class AuthorizeNet(Gateway):
    ns = 'AnetApi/xml/v1/schema/AnetApiSchema.xsd'
    live_url = 'https://api.authorize.net/xml/v1/request.api'
    test_url = 'https://apitest.authorize.net/xml/v1/request.api'

    def __init__(self, options):
        self.login_id = options['login_id']
        self.transaction_key = options['transaction_key']

        self.url = self.test_url

        # Auto-discover if this is a real account or a developer account.  Tries
        # to access both end points and see which one works.
        try:
            self.retrieve('0')
        except GatewayException as e:
            error_code = e.args[0][0][0]
            if error_code == 'E00007':  # PermissionDenied
                self.url = self.live_url
                try:
                    self.retrieve('0')
                except GatewayException as e:
                    error_code = e.args[0][0][0]
                    if error_code != 'E00040' and error_code != 'E00011':
                        raise
            elif error_code != 'E00040' and error_code != 'E00011':
                raise

    def build_xml(self, root_name, root):
        root.insert(0, 'merchantAuthentication', OrderedDict([
                ('name', self.login_id),
                ('transactionKey', self.transaction_key),
                ]))

        return dict_to_xml(root_name, root, self.ns)

    def check_for_error(self, resp):
        if resp['messages']['resultCode'] == 'Error':
            if 'transactionResponse' in resp:
                raise PaymentException(payment_exception_factory([(errors['errorCode'], errors['errorText'])
                                                                  for errors in resp['transactionResponse']['errors']['error']]))
            else:
                raise GatewayException([(message['code'], message['text'])
                                        for message in resp['messages']['message']])

        # Sometimes Authorize.net is confused and returns errors even though it
        # says that the request was Successful!
        try:
            raise PaymentException(payment_exception_factory([(errors['errorCode'], errors['errorText'])
                                                              for errors in resp['transactionResponse']['errors']['error']]))
        except KeyError:
            pass

    ##|
    ##|  XML BUILDERS
    ##|
    def _payment_xml(self, options):
        year = str(options['year'])
        if year != 'XXXX' and int(year) < 100:
            century = date.today().century // 100
            year = str(century) + str(year)

        # zeropad the month
        expiry = str(year) + '-' + str(options['month']).zfill(2)
        if expiry == 'XXXX-XX':
            expiry = 'XXXX'

        return OrderedDict([
            ('creditCard', OrderedDict([
                ('cardNumber', prepare_number(options['number'])),
                ('expirationDate', expiry),
                ('cardCode', options.get('cvv')),
                ])),
            ])

    def _billto_xml(self, options):
        return OrderedDict([
            ('firstName', options.get('first_name')),
            ('lastName', options.get('last_name')),
            ('company', options.get('company')),
            ('address', options.get('address')),
            ('city', options.get('city')),
            ('state', options.get('state')),
            ('zip', options.get('zip')),
            ('country', options.get('country')),
            ('phoneNumber', options.get('phone')),
            ('faxNumber', options.get('fax')),
            ])

    def _create_customer_xml(self, options):
        # include <billTo> and <payment> fields only if
        # the necessary data was included

        # build <billTo> entry?
        billto_fields = [
            'first_name',
            'last_name',
            'company',
            'address',
            'city',
            'state',
            'zip',
            'country',
            'phone',
            'fax',
            ]
        if any(field in options for field in billto_fields):
            billto = ('billTo', self._billto_xml(options))
        else:
            billto = None

        # build <payment> entry?
        if 'number' in options:
            payment = ('payment', self._payment_xml(options))
        else:
            payment = None

        if billto or payment:
            stuff = []
            if billto:
                stuff.append(billto)
            if payment:
                stuff.append(payment)
            payment_profiles = ('paymentProfiles', OrderedDict(stuff))
        else:
            payment_profiles = None

        stuff = [('email', options['email'])]
        if payment_profiles:
            stuff.append(payment_profiles)
        root = OrderedDict([
            ('profile', OrderedDict(stuff)),
            ])
        return self.build_xml('createCustomerProfileRequest', root)

    def _update_customer_xml(self, customer_id, options):
        stuff = [('email', options['email']), ('customerProfileId', customer_id)]

        root = OrderedDict([
            ('profile', OrderedDict(stuff)),
            ])
        return self.build_xml('updateCustomerProfileRequest', root)

    def _charge_customer_xml(self, customer_id, customer_payment_profile_id, price, options):
        return self.build_xml('createCustomerProfileTransactionRequest', OrderedDict([
                ('transaction', OrderedDict([
                    ('profileTransAuthOnly', OrderedDict([
                        ('amount', price),
                        ('customerProfileId', customer_id),
                        ('customerPaymentProfileId', customer_payment_profile_id),
                        ('cardCode', options.get('cvv')),
                    ])),
                ]))
            ]))

    def transaction_details(self, resp, price):
        ret = {
                'price': price,
                'transaction_id': resp['transId'],
                'avs_result_code': get_first_of(resp, ['avsResultCode', 'AVSResponse']),
                'cvv_result_code': get_first_of(resp, ['cvvResultCode', 'cardCodeResponse']),
                'cavv_result_code': resp.get('cavvResultCode'),
                'response_code': resp['responseCode'],
                'auth_code': resp.get('authCode'),
                }
        try:
            ret['account_number'] = resp['accountNumber']
            ret['card_type'] = resp['accountType']
        except KeyError:
            ret['account_number'] = resp['payment']['creditCard']['cardNumber']
            ret['card_type'] = resp['payment']['creditCard']['cardType']

        try:
            ret['messages'] = [(message['code'], message['description'])
                               for message in resp['messages']['message']]
        except KeyError:
            pass

        return ret

    RESPONSE_CODE = 0
    AUTH_CODE = 4
    TRANSACTION_ID = 6
    ACCOUNT_NUMBER = 50
    ACCOUNT_TYPE = 51

    def transaction_details_direct_response(self, direct_resp, price):
        resp_list = direct_resp.split(',')
        ret = {
                'price': price,
                'response_code': resp_list[self.RESPONSE_CODE],
                'auth_code': resp_list[self.AUTH_CODE],
                'transaction_id': resp_list[self.TRANSACTION_ID],
                'account_number': resp_list[self.ACCOUNT_NUMBER],
                'card_type': resp_list[self.ACCOUNT_TYPE],
                }
        return ret

    def charge(self, price, options):
        if 'customer' in options:
            return self.charge_customer(options['customer'], price, options)

        xml = self.build_xml('createTransactionRequest', OrderedDict([
            ('transactionRequest', OrderedDict([
                ('transactionType', 'authCaptureTransaction'),
                ('amount', price),
                ('payment', self._payment_xml(options)),
                ('billTo', self._billto_xml(options)),
                ('transactionSettings', OrderedDict([
                    ('setting', [
                        OrderedDict([
                            ('settingName', 'duplicateWindow'),
                            ('settingValue', 0),
                            ]),
                        OrderedDict([
                            ('settingName', 'testRequest'),
                            ('settingValue', 'false'),
                            ]),
                        ],)
                    ])),
                ]),),
            ]))

        resp = xml_to_dict(xml_post(self.url, xml))
        self.check_for_error(resp)

        return self.transaction_details(resp['transactionResponse'], price)

    def retrieve(self, transaction_id):
        xml = self.build_xml('getTransactionDetailsRequest', OrderedDict([
            ('transId', transaction_id),
            ]))

        resp = xml_to_dict(xml_post(self.url, xml))
        self.check_for_error(resp)

        return self.transaction_details(resp['transaction'], resp['transaction']['authAmount'])

    def void(self, transaction):
        xml = self.build_xml('createTransactionRequest', OrderedDict([
            ('transactionRequest', OrderedDict([
                ('transactionType', 'voidTransaction'),
                ('refTransId', transaction.transaction_id),
                ])),
            ]))

        resp = xml_to_dict(xml_post(self.url, xml))
        self.check_for_error(resp)

        return True

    def refund(self, transaction, amount):
        xml = self.build_xml('createTransactionRequest', OrderedDict([
            ('transactionRequest', OrderedDict([
                ('transactionType', 'refundTransaction'),
                ('amount', amount),
                ('payment', self._payment_xml({'number': transaction.data['account_number'], 'year': 'XXXX', 'month': 'XX'})),
                ('refTransId', transaction.transaction_id),
                ])),
            ]))

        resp = xml_to_dict(xml_post(self.url, xml))
        self.check_for_error(resp)

        return True

    def create_customer(self, options):
        if 'email' not in options:
            raise InvalidCustomerException('"email" is a required field in Customer.create')

        xml = self._create_customer_xml(options)
        resp = xml_to_dict(xml_post(self.url, xml))
        try:
            self.check_for_error(resp)
        except GatewayException as e:
            error_code = e.args[0][0][0]
            if error_code == 'E00039':  # Duplicate Record
                raise DuplicateCustomerError(e)
            raise

        # make a copy of options
        profile = {}
        profile.update(options)
        # and add information from the createCustomerProfileRequest response
        profile['customer_id'] = resp['customerProfileId']
        profile['customer_payment_profile_id'] = None
        try:
            if resp['customerPaymentProfileIdList'] and resp['customerPaymentProfileIdList']['numericString']:
                profile['customer_payment_profile_id'] = resp['customerPaymentProfileIdList']['numericString']
        except KeyError:
            pass

        return profile

    def _update_customer_payment(self, customer_id, options):
        # update <billTo> and <payment> fields only if
        # the necessary data was included

        # update <billTo> entry?
        billto_fields = [
            'first_name',
            'last_name',
            'company',
            'address',
            'city',
            'state',
            'zip',
            'country',
            'phone',
            'fax',
            ]
        if any(field in options for field in billto_fields):
            billto = ('billTo', self._billto_xml(options))
        else:
            billto = None

        # update <payment> entry?
        if 'number' in options:
            payment = ('payment', self._payment_xml(options))
        else:
            payment = None

        if billto or payment:
            if 'customer_payment_profile_id' in options:
                customer_payment_profile_id = options['customer_payment_profile_id']
            else:
                customer = self.retrieve_customer(customer_id)
                customer_payment_profile_id = customer.customer_payment_profile_id

            merge = None
            if customer_payment_profile_id:
                try:
                    profile = self._get_customer_payment_profile(customer_id, customer_payment_profile_id)
                    merge = self.dict_to_payment_profile(profile)
                    merge.update(options)
                    options = merge
                except CustomerNotFoundError:
                    pass

            stuff = []
            # refresh billto and payment if merge came back with anything
            if merge:
                billto = ('billTo', self._billto_xml(options))

            if billto:
                stuff.append(billto)

            if merge:
                payment = ('payment', self._payment_xml(options))

            if payment:
                stuff.append(payment)

            if customer_payment_profile_id:
                stuff.append(('customerPaymentProfileId', customer_payment_profile_id))

                root = OrderedDict([
                    ('customerProfileId', customer_id),
                    ('paymentProfile', OrderedDict(stuff)),
                    ])
                xml = self.build_xml('updateCustomerPaymentProfileRequest', root)
                resp = xml_to_dict(xml_post(self.url, xml))
            else:
                root = OrderedDict([
                    ('customerProfileId', customer_id),
                    ('paymentProfile', OrderedDict(stuff)),
                    ])
                xml = self.build_xml('createCustomerPaymentProfileRequest', root)
                resp = xml_to_dict(xml_post(self.url, xml))

            try:
                self.check_for_error(resp)
            except GatewayException as e:
                error_code = e.args[0][0][0]
                if error_code == 'E00039':  # Duplicate Record
                    raise DuplicateCustomerError(e)
                raise

    def update_customer(self, customer_id, options):
        try:
            xml = self._update_customer_xml(customer_id, options)
            resp = xml_to_dict(xml_post(self.url, xml))
            self.check_for_error(resp)
        except GatewayException as e:
            error_code = e.args[0][0][0]
            if error_code == 'E00040':  # NotFound
                raise DuplicateCustomerError(e)
            raise
        else:
            self._update_customer_payment(customer_id, options)

        return True

    def retrieve_customer(self, customer_id):
        xml = self.build_xml('getCustomerProfileRequest', OrderedDict([
            ('customerProfileId', customer_id),
            ]))

        resp = xml_to_dict(xml_post(self.url, xml))
        try:
            self.check_for_error(resp)
        except GatewayException as e:
            error_code = e.args[0][0][0]
            if error_code == 'E00040':  # NotFound
                raise CustomerNotFoundError(e)
            raise

        return self.dict_to_customer(resp['profile'])

    def delete_customer(self, customer_id):
        xml = self.build_xml('deleteCustomerProfileRequest', OrderedDict([
            ('customerProfileId', customer_id),
            ]))
        resp = xml_to_dict(xml_post(self.url, xml))
        try:
            self.check_for_error(resp)
        except GatewayException as e:
            error_code = e.args[0][0][0]
            if error_code == 'E00040':  # NotFound
                raise CustomerNotFoundError(e)
            raise

        return True

    def charge_customer(self, customer, price, options):
        customer_id = customer.customer_id
        try:
            customer_payment_profile_id = customer.customer_payment_profile_id
        except AttributeError:
            customer = self.retrieve_customer(customer_id)
            customer_payment_profile_id = customer.customer_payment_profile_id

        xml = self._charge_customer_xml(customer_id, customer_payment_profile_id, price, options)
        resp = xml_to_dict(xml_post(self.url, xml))
        try:
            self.check_for_error(resp)
        except GatewayException as e:
            error_code = e.args[0][0][0]
            if error_code == 'E00040':  # NotFound
                raise CustomerNotFoundError(e)
            raise

        for i, item in enumerate(resp['directResponse'].split(',')):
            print i, ':', item
        return self.transaction_details_direct_response(resp['directResponse'], price)

    def _get_customer_payment_profile(self, customer_id, customer_payment_profile_id):
        xml = self.build_xml('getCustomerPaymentProfileRequest', OrderedDict([
            ('customerProfileId', customer_id),
            ('customerPaymentProfileId', customer_payment_profile_id),
            ]))
        resp = xml_to_dict(xml_post(self.url, xml))
        try:
            self.check_for_error(resp)
        except GatewayException as e:
            error_code = e.args[0][0][0]
            if error_code == 'E00040':  # NotFound
                raise CustomerNotFoundError(e)
            raise

        return resp

    def dict_to_customer(self, resp):
        ret = {
                'customer_id': resp['customerProfileId'],
                'email': resp['email'],
            }

        # more than one paymentProfile?
        if isinstance(resp.get('paymentProfiles'), list):
            resp['paymentProfiles'] = resp['paymentProfiles'][0]

        # more than one creditCard?
        try:
            if isinstance(resp['paymentProfiles']['profile']['creditCard'], list):
                resp['paymentProfiles']['profile']['creditCard'] = resp['paymentProfiles']['profile']['creditCard'][0]
        except KeyError:
            pass

        gets = {
            'first_name': 'paymentProfiles.billTo.firstName',
            'last_name': 'paymentProfiles.billTo.lastName',
            'company': 'paymentProfiles.billTo.company',
            'phone': 'paymentProfiles.billTo.phoneNumber',
            'fax': 'paymentProfiles.billTo.faxNumber',
            'address': 'paymentProfiles.billTo.address',
            'state': 'paymentProfiles.billTo.state',
            'city': 'paymentProfiles.billTo.city',
            'zip': 'paymentProfiles.billTo.zip',
            'country': 'paymentProfiles.billTo.country',
            'last_4': 'paymentProfiles.payment.creditCard.cardNumber',

            # auth.net specific
            'number': 'paymentProfile.payment.creditCard.cardNumber',
            'customer_payment_profile_id': 'paymentProfiles.customerPaymentProfileId',
            }
        for key, kvp in gets.iteritems():
            try:
                search = kvp.split('.')
                val = resp
                while search:
                    val = val[search.pop(0)]
                ret[key] = val
            except KeyError:
                pass

        if 'last_4' in ret:
            # in the form "XXXX1234"
            ret['last_4'] = ret['last_4'][4:]
            # now it's in the form "1234"

        try:
            ret['messages'] = [(message['code'], message['description'])
                               for message in resp['messages']['message']]
        except KeyError:
            pass

        return ret

    def dict_to_payment_profile(self, resp):
        ret = {}

        try:
            if isinstance(resp['paymentProfile']['profile']['creditCard'], list):
                resp['paymentProfile']['profile']['creditCard'] = resp['paymentProfile']['profile']['creditCard'][0]
        except KeyError:
            pass

        gets = {
            'first_name': 'paymentProfile.billTo.firstName',
            'last_name': 'paymentProfile.billTo.lastName',
            'company': 'paymentProfile.billTo.company',
            'phone': 'paymentProfile.billTo.phoneNumber',
            'fax': 'paymentProfile.billTo.faxNumber',
            'address': 'paymentProfile.billTo.address',
            'state': 'paymentProfile.billTo.state',
            'city': 'paymentProfile.billTo.city',
            'zip': 'paymentProfile.billTo.zip',
            'country': 'paymentProfile.billTo.country',
            'last_4': 'paymentProfile.payment.creditCard.cardNumber',

            # these must be sent to auth.net in updateCustomerPaymentProfileRequest
            'number': 'paymentProfile.payment.creditCard.cardNumber',
            'expiration_date': 'paymentProfile.payment.creditCard.expirationDate',

            # auth.net specific
            'customer_payment_profile_id': 'paymentProfile.customerPaymentProfileId',
            }
        for key, kvp in gets.iteritems():
            try:
                search = kvp.split('.')
                val = resp
                while search:
                    val = val[search.pop(0)]
                ret[key] = val
            except KeyError:
                pass

        if 'last_4' in ret:
            # in the form "XXXX1234"
            ret['last_4'] = ret['last_4'][4:]
            # now it's in the form "1234"

        if 'expiration_date' in ret:
            # in the form "XXXX" or "YYYY-MM"
            if '-' in ret['expiration_date']:
                ret['year'], ret['month'] = ret['expiration_date'].split('-', 1)
            else:
                ret['year'], ret['month'] = ('XXXX', 'XX')

        try:
            ret['messages'] = [(message['code'], message['description'])
                               for message in resp['messages']['message']]
        except KeyError:
            pass

        return ret
