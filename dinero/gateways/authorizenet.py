import re
import requests
from lxml import etree

from dinero.ordereddict import OrderedDict
from dinero.exceptions import *
from dinero.gateways.base import Gateway


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
    return re.sub('\D', '', number)


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
            exceptions.extend(i(message) for i in RESPONSE_CODE_EXCEPTION_MAP[code])
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
                raise PaymentException(payment_exception_factory([(i['errorCode'], i['errorText'])
                    for i in resp['transactionResponse']['errors']['error']]))
            else:
                raise GatewayException([(i['code'], i['text'])
                    for i in resp['messages']['message']])

        # Sometimes Authorize.net is confused and returns errors even though it
        # says that the request was Successful!
        try:
            raise PaymentException(payment_exception_factory([(i['errorCode'], i['errorText'])
                for i in resp['transactionResponse']['errors']['error']]))
        except KeyError:
            pass

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
            ret['messages'] = [(i['code'], i['description'])
                    for i in resp['messages']['message']]
        except KeyError:
            pass

        return ret

    def charge(self, price, options):
        expiry = str(options['month']) + '/' + str(options['year'])

        xml = self.build_xml('createTransactionRequest', OrderedDict([
            ('transactionRequest', OrderedDict([
                ('transactionType', 'authCaptureTransaction'),
                ('amount', price),
                ('payment', OrderedDict([
                    ('creditCard', OrderedDict([
                        ('cardNumber', prepare_number(options['number'])),
                        ('expirationDate', expiry),
                        ('cardCode', options.get('cvv')),
                        ])),
                    ])),
                ('billTo', OrderedDict([
                    ('firstName', options.get('first_name')),
                    ('lastName', options.get('last_name')),
                    ('address', options.get('address')),
                    ('city', options.get('city')),
                    ('state', options.get('state')),
                    ('zip', options.get('zip')),
                    ]),),
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
                ('payment', OrderedDict([
                    ('creditCard', OrderedDict([
                        ('cardNumber', transaction.data['account_number']),
                        # The XML Schema Definition requires that there be an
                        # expirationDate element, however, the API does not
                        # require it for refunds.
                        ('expirationDate', 'XXXX'),
                        ])),
                    ])),
                ('refTransId', transaction.transaction_id),
                ])),
            ]))

        resp = xml_to_dict(xml_post(self.url, xml))
        self.check_for_error(resp)

        return True

    def create_customer(self, options):
        xml = self.build_xml('createCustomerProfileRequest', OrderedDict([
            ('profile', OrderedDict([
                ('email', options['email']),  # email is required
                ('profile', OrderedDict([
                    ('paymentProfiles', OrderedDict([
                        ('billTo', OrderedDict([
                            ('firstName', options.get('firstName')),
                            ('lastName', options.get('lastName')),
                            ('company', options.get('company')),
                            ('phoneNumber', options.get('phoneNumber')),
                            ('faxNumber', options.get('faxNumber')),
                            ('address', options.get('address')),
                            ('state', options.get('state')),
                            ('city', options.get('city')),
                            ('zip', options.get('zip')),
                            ('country', options.get('country')),
                            ])),
                        ('payment', OrderedDict([
                            ('creditCard', OrderedDict([
                                ('cardNumber', options.get('number')),
                                ('expirationDate', options.get('year') + '/' + options.get('month')),
                                ])),
                            ])),
                        ])),
                    ])),
                ])),
            ]))
        resp = xml_to_dict(xml_post(self.url, xml))
        self.check_for_error(resp)

        return self.customer_details(resp['profile'])

    def retrieve_customer(self, customer_id):
        xml = self.build_xml('getCustomerProfileRequest', OrderedDict([
            ('customerProfileId', customer_id),
            ]))
        resp = xml_to_dict(xml_post(self.url, xml))
        self.check_for_error(resp)

        return self.customer_details(resp['profile'])

    def customer_details(self, resp):
        ret = {
                'customer_id': resp['customerProfileId'],
                'email': resp['email'],
            }

        # more than one paymentProfile?
        if isinstance(resp.get('paymentProfiles'), list):
            resp['paymentProfiles'] = resp['paymentProfiles'][0]

        # more than one paymentProfile?
        try:
            if isinstance(resp['paymentProfiles']['profile']['creditCard'], list):
                resp['paymentProfiles']['profile']['creditCard'] = resp['paymentProfiles']['profile']['creditCard'][0]
        except KeyError:
            pass

        gets = {
            'first_name': 'paymentProfiles.billTo.firstName',
            'last_name': 'paymentProfiles.billTo.lastName',
            'company': 'paymentProfiles.billTo.company',
            'phone': 'paymentProfiles.billTo.phone',
            'fax': 'paymentProfiles.billTo.fax',
            'address': 'paymentProfiles.billTo.address',
            'state': 'paymentProfiles.billTo.state',
            'city': 'paymentProfiles.billTo.city',
            'zip': 'paymentProfiles.billTo.zip',
            'country': 'paymentProfiles.billTo.country',
            'last_4': 'paymentProfiles.profile.creditCard.cardNumber',
            }
        for key, kvp in gets.iteritems():
            try:
                search = kvp.split('.')
                val = None
                while search:
                    val = resp[search.pop(0)]
            except KeyError:
                val = None
            ret[key] = val

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
