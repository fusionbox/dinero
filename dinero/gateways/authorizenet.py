import requests
from lxml import etree

from dinero.ordereddict import OrderedDict
from dinero.exceptions import PaymentException, GatewayException
from dinero.gateways.base import Gateway

def xml_post(url, obj):
    resp = requests.post(
            url,
            data=etree.tostring(obj),
            headers={'content-type': 'application/xml'},
            verify=True,
            )

    content = resp.content
    if content[0] == u'\ufeff':
        # authorize.net puts a BOM in utf-8. Shame.
        content = content[1:]
    content = str(content)
    return etree.XML(content)


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
            if error_code == 'E00007': # PermissionDenied
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
                raise PaymentException([(i['errorCode'], i['errorText'])
                    for i in resp['transactionResponse']['errors']['error']])
            else:
                raise GatewayException([(i['code'], i['text'])
                    for i in resp['messages']['message']])

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
                        ('cardNumber', options['number']),
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
