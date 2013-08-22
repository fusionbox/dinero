from lxml import etree

import dinero


def prepare(s):
    gateway = dinero.get_gateway('authorize.net')
    template = ''.join(line.strip() for line in s.strip().splitlines())
    return template.format(
        login_id=gateway.login_id,
        transaction_key=gateway.transaction_key,
    )


MINIMAL_CUSTOMER_XML = prepare("""
<createCustomerProfileRequest xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
    <merchantAuthentication>
        <name>{login_id}</name>
        <transactionKey>{transaction_key}</transactionKey>
    </merchantAuthentication>
    <profile>
        <email>someone@fusionbox.com</email>
    </profile>
</createCustomerProfileRequest>
""")


def test_minimum_create_customer_xml():
    gateway = dinero.get_gateway('authorize.net')
    options = {
        'email': 'someone@fusionbox.com',
    }
    xml = gateway._create_customer_xml(options)
    should_be = MINIMAL_CUSTOMER_XML
    assert etree.tostring(xml) == should_be, 'Invalid XML'


PAYMENT_CUSTOMER_XML = prepare("""
<createCustomerProfileRequest xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
    <merchantAuthentication>
        <name>{login_id}</name>
        <transactionKey>{transaction_key}</transactionKey>
    </merchantAuthentication>
    <profile>
        <email>someone@fusionbox.com</email>
        <paymentProfiles>
            <payment>
                <creditCard>
                    <cardNumber>4111111111111111</cardNumber>
                    <expirationDate>2012-12</expirationDate>
                </creditCard>
            </payment>
        </paymentProfiles>
    </profile>
</createCustomerProfileRequest>
""")


def test_payment_create_customer_xml():
    gateway = dinero.get_gateway('authorize.net')
    options = {
        'email': 'someone@fusionbox.com',

        'number': '4' + '1' * 15,
        'month': '12',
        'year': '2012',
    }
    xml = gateway._create_customer_xml(options)
    should_be = PAYMENT_CUSTOMER_XML
    assert etree.tostring(xml) == should_be, "Invalid XML (\n\t%s\n\t%s\n)" % (etree.tostring(xml), should_be)


BILLTO_XML = prepare("""
<createCustomerProfileRequest xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
    <merchantAuthentication>
        <name>{login_id}</name>
        <transactionKey>{transaction_key}</transactionKey>
    </merchantAuthentication>
    <profile>
        <email>someone@fusionbox.com</email>
        <paymentProfiles>
            <billTo>
                <firstName>Joey</firstName>
                <lastName>Shabadoo</lastName>
                <company>Shabadoo, Inc.</company>
                <address>123 somewhere st</address>
                <city>somewhere</city>
                <state>SW</state>
                <zip>12345</zip>
                <country>US</country>
                <phoneNumber>000-000-0000</phoneNumber>
                <faxNumber>000-000-0001</faxNumber>
            </billTo>
        </paymentProfiles>
    </profile>
</createCustomerProfileRequest>
""")


def test_billto_create_customer_xml():
    gateway = dinero.get_gateway('authorize.net')
    options = {
        'email': 'someone@fusionbox.com',

        'first_name': 'Joey',
        'last_name': 'Shabadoo',
        'company': 'Shabadoo, Inc.',
        'phone': '000-000-0000',
        'fax': '000-000-0001',
        'address': '123 somewhere st',
        'state': 'SW',
        'city': 'somewhere',
        'zip': '12345',
        'country': 'US',
    }
    xml = gateway._create_customer_xml(options)
    should_be = BILLTO_XML
    assert etree.tostring(xml) == should_be, "Invalid XML (\n\t%s\n\t%s\n)" % (etree.tostring(xml), should_be)


FULL_DATA_XML = prepare("""
<createCustomerProfileRequest xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
    <merchantAuthentication>
        <name>{login_id}</name>
        <transactionKey>{transaction_key}</transactionKey>
    </merchantAuthentication>
    <profile>
        <email>someone@fusionbox.com</email>
        <paymentProfiles>
            <billTo>
                <firstName>Joey</firstName>
                <lastName>Shabadoo</lastName>
                <company>Shabadoo, Inc.</company>
                <address>123 somewhere st</address>
                <city>somewhere</city>
                <state>SW</state>
                <zip>12345</zip>
                <country>US</country>
                <phoneNumber>000-000-0000</phoneNumber>
                <faxNumber>000-000-0001</faxNumber>
            </billTo>
            <payment>
                <creditCard>
                    <cardNumber>4111111111111111</cardNumber>
                    <expirationDate>2012-12</expirationDate>
                </creditCard>
            </payment>
        </paymentProfiles>
    </profile>
</createCustomerProfileRequest>
""")


def test_customer_create_xml():
    gateway = dinero.get_gateway('authorize.net')
    options = {
        'email': 'someone@fusionbox.com',

        'first_name': 'Joey',
        'last_name': 'Shabadoo',
        'company': 'Shabadoo, Inc.',
        'phone': '000-000-0000',
        'fax': '000-000-0001',
        'address': '123 somewhere st',
        'state': 'SW',
        'city': 'somewhere',
        'zip': '12345',
        'country': 'US',

        'number': '4' + '1' * 15,
        'month': '12',
        'year': '2012',
    }
    xml = gateway._create_customer_xml(options)
    should_be = FULL_DATA_XML
    assert etree.tostring(xml) == should_be, "Invalid XML (\n\t%s\n\t%s\n)" % (etree.tostring(xml), should_be)


UPDATE_XML = prepare("""
<updateCustomerProfileRequest xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
    <merchantAuthentication>
        <name>{login_id}</name>
        <transactionKey>{transaction_key}</transactionKey>
    </merchantAuthentication>
    <profile>
        <email>someone@fusionbox.com</email>
        <customerProfileId>123456789</customerProfileId>
    </profile>
</updateCustomerProfileRequest>
""")


def test_update_customer_xml():
    gateway = dinero.get_gateway('authorize.net')
    options = {
        'email': 'someone@fusionbox.com',
    }
    xml = gateway._update_customer_xml('123456789', options)
    should_be = UPDATE_XML
    assert etree.tostring(xml) == should_be, "Invalid XML (\n\t%s\n\t%s\n)" % (etree.tostring(xml), should_be)


CHARGE_CUSTOMER_XML = prepare("""
<createCustomerProfileTransactionRequest xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
    <merchantAuthentication>
        <name>{login_id}</name>
        <transactionKey>{transaction_key}</transactionKey>
    </merchantAuthentication>
    <transaction>
        <profileTransAuthCapture>
            <amount>123.45</amount>
            <customerProfileId>123456789</customerProfileId>
            <customerPaymentProfileId>987654321</customerPaymentProfileId>
            <cardCode>123</cardCode>
        </profileTransAuthCapture>
    </transaction>
</createCustomerProfileTransactionRequest>
""")


def test_charge_customer_xml():
    gateway = dinero.get_gateway('authorize.net')
    price = 123.45
    customer_id = '123456789'
    card_id = '987654321'
    options = {
        'cvv': '123'
    }
    xml = gateway._charge_customer_xml(customer_id, card_id, price, options)
    should_be = CHARGE_CUSTOMER_XML
    assert etree.tostring(xml) == should_be, "Invalid XML (\n\t%s\n\t%s\n)" % (etree.tostring(xml), should_be)
