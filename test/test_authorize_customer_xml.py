import random
import dinero
from dinero.exceptions import *
from lxml import etree

## These tests require that you provide settings for authorize.net and set up
## your account to reject invalid CVV and AVS responses
import authorize_net_configuration


## For information on how to trigger specific errors, see http://community.developer.authorize.net/t5/Integration-and-Testing/Triggering-Specific-Transaction-Responses-Using-Test-Account/td-p/4361


def trimmy(s):
    return ''.join(line.lstrip() for line in s.splitlines())


def test_minimum_create_customer_xml():
    gateway = dinero.get_gateway()
    options = {
        'email': 'someone@fusionbox.com',
    }
    xml = gateway._create_customer_xml(options)
    should_be = trimmy(
             """<createCustomerProfileRequest xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
                              <merchantAuthentication>
                                  <name>{login_id}</name>
                                  <transactionKey>{transaction_key}</transactionKey>
                              </merchantAuthentication>
                              <profile>
                                  <email>someone@fusionbox.com</email>
                              </profile>
                          </createCustomerProfileRequest>""".format(
                        login_id=gateway.login_id,
                        transaction_key=gateway.transaction_key,
                    ))
    assert etree.tostring(xml) == should_be, 'Invalid XML'


def test_payment_create_customer_xml():
    gateway = dinero.get_gateway()
    options = {
        'email': 'someone@fusionbox.com',

        'number': '4' + '1' * 15,
        'month': '12',
        'year': '2012',
    }
    xml = gateway._create_customer_xml(options)
    should_be = trimmy(
             """<createCustomerProfileRequest xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
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
                </createCustomerProfileRequest>""".format(
                        login_id=gateway.login_id,
                        transaction_key=gateway.transaction_key,
                    ))
    assert etree.tostring(xml) == should_be, "Invalid XML (\n\t%s\n\t%s\n)" % (etree.tostring(xml), should_be)


def test_billto_create_customer_xml():
    gateway = dinero.get_gateway()
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
    should_be = trimmy(
             """<createCustomerProfileRequest xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
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
                </createCustomerProfileRequest>""".format(
                        login_id=gateway.login_id,
                        transaction_key=gateway.transaction_key,
                    ))
    assert etree.tostring(xml) == should_be, "Invalid XML (\n\t%s\n\t%s\n)" % (etree.tostring(xml), should_be)


def test_customer_create_xml():
    gateway = dinero.get_gateway()
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
    should_be = trimmy(
             """<createCustomerProfileRequest xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
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
                </createCustomerProfileRequest>""".format(
                        login_id=gateway.login_id,
                        transaction_key=gateway.transaction_key,
                    ))
    assert etree.tostring(xml) == should_be, "Invalid XML (\n\t%s\n\t%s\n)" % (etree.tostring(xml), should_be)


def test_update_customer_xml():
    gateway = dinero.get_gateway()
    options = {
        'customer_payment_profile_id': '987654321',
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
    xml = gateway._update_customer_xml('123456789', options)
    should_be = trimmy(
             """<updateCustomerProfileRequest xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
                    <merchantAuthentication>
                        <name>{login_id}</name>
                        <transactionKey>{transaction_key}</transactionKey>
                    </merchantAuthentication>
                    <profile>
                        <customerProfileId>123456789</customerProfileId>
                        <email>someone@fusionbox.com</email>
                    </profile>
                </updateCustomerProfileRequest>""".format(
                        login_id=gateway.login_id,
                        transaction_key=gateway.transaction_key,
                    ))
    assert etree.tostring(xml) == should_be, "Invalid XML (\n\t%s\n\t%s\n)" % (etree.tostring(xml), should_be)

    xml = gateway._update_customer_payment_xml('123456789', options)
    should_be = trimmy(
             """<updateCustomerPaymentProfileRequest xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
                    <merchantAuthentication>
                        <name>{login_id}</name>
                        <transactionKey>{transaction_key}</transactionKey>
                    </merchantAuthentication>
                    <customerProfileId>123456789</customerProfileId>
                    <paymentProfile>
                        <customerPaymentProfileId>987654321</customerPaymentProfileId>
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
                    </paymentProfile>
                </updateCustomerPaymentProfileRequest>""".format(
                        login_id=gateway.login_id,
                        transaction_key=gateway.transaction_key,
                    ))
    assert etree.tostring(xml) == should_be, "Invalid XML (\n\t%s\n\t%s\n)" % (etree.tostring(xml), should_be)
