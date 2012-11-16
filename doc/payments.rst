Payments 101
------------

.. note::
    This document aims to introduce a developer to what is involved in taking
    online payments.  If you already have experience with online payments, then
    you can probably skip ahead to the :doc:`quickstart`.

There are a lot of pieces involved in accepting payments.  The first thing you
need in order to accept payments is a merchant account.  Then you need a
payment gateway.  Then you need code which talks to the payment gateway.
Associated with the merchant account is a payment processor.  The payment
processor talks to credit card companies.  All of these pieces add up together
in order for an end user to enter their credit card and you to receive money
from them.

There seem to be two paradigms in online payments.  One is the PayPal paradigm,
where customers are redirected off site to the PayPal site where they log into
their PayPal account and confirm the payment on that site and then are
redirected back to your website afterwards.  Examples of PayPal-style payment
providers include, of course, PayPal, Amazon Payments, and Google Wallet.

The other paradigm is sometimes called the server-to-server paradigm.  With
server-to-server, users are not redirected off of your site, your server code
will communicate the necessary data to the gateway behind the scenes.
Server-to-server payments give you (the developer) complete control of the
customer experience.  Server-to-server payments also give you more control of
information management and recurring payments.  Examples of server-to-server
providers include Authorize.Net, Braintree payments, and Stripe.


Merchant Account
================

A merchant account is a special type of bank account that can receive credit
card transactions.  To protect against fraud, opening a merchant account is
something of an involved process.

.. todo::
    Explain how to get a merchant account???


Payment Gateway
===============

Payment gateways are what communicate between the credit card processors and
your merchant account.  There are several credit card processors these days,
but the major ones include Authorize.Net, Braintree Payments, and Stripe.

Braintree and Stripe both offer accounts that don't require merchant accounts.
If you are familiar with Square, this is quite similar.  These accounts are
more convenient in that you don't have to go through the hassle of getting a
merchant account and you don't have to pay the merchant account fees.  However,
the pricing for this type of account is generally higher per transaction
(almost always 2.9% + 30¢ per transaction).

Stripe and merchant account-less Braintree accounts are good for companies that
are just starting out who don't expect to have large transactions.  Often it is
cheaper to have one of these accounts because the high transaction fees are
still smaller than the monthly fees associated with merchant accounts.

Authorize.Net or merchant account-backed Braintree accounts are more suitable
for website that expect high volume or high priced transactions, or for
companies that also want to do offline payments as well.

Features
________

Payment gateways usually offer a variation on the same list of features.

Transactions
~~~~~~~~~~~~
The usual process for transaction is as follows:

1.  Send a payment to the gateway.  The gateway will validate the payment and
    then send it to the processor who will validate that the credit card is
    real and "authorize" the payment.  Validating means checking that the
    credit card number is real, that the CVV code matches or that the address
    is correct.  Authorization is a fancy word for making sure that the credit
    card actually has money for the payment.

2.  Then you submit the payment for settlement.  This means that you wish the
    payment to actually go through.  Payments are usually settled once a day.
    Settlement is the actually process of transferring the money.

Prior to a payment being settled, it can be voided.  If a payment is neither
settled nor voided within 30 days, it goes away.  A processor may charge you a
fee if you leave a payment suspended like that.

After a payment has been settled, you may refund all or part of a payment.
This process takes the money from your merchant account and gives it back to
the customer.

.. note::
    It is possible to charge a credit card with only the number and the
    expiration date.  Name on card, CVV code, and billing address are all
    optional fields.  However, if you ask for CVV code and/or billing address
    you can verify your transaction more soundly.
    
    With certain payment gateways, more verified qualify for better rates.
    There is a lot of risk involved for the payment companies and they will
    charge more when they are worried about fraud.

Vaulting
~~~~~~~~
If you store a customer's credit card information on your server, you are
exposing yourself to some big liabilities.  There is this thing called PCI
compliance which is sort of a list of regulations that you need to conform to
when processing credit cards.  It is much preferable to store that information
with the gateway, who can afford those risks.  The vaulting process is
something similar to the following:

1.  Collect the customer's credit card information on your website.  It is
    especially important to avoid storing (or logging!) the credit card number
    or the CVV code.

2.  Send the information to the gateway.  The gateway will give you a token or
    and ID that you can use to reference the credit card.  You don't have
    access to the credit card number anymore, but that is probably for the
    best.

.. note::
    Some payment gateways offer solutions for storing credit card information
    that never need to touch your server.  These are very convenient because
    they may help avoid the need for you to have a PCI compliant website.

    Older implementations of this included redirects to the gateway website to
    display the form.  This may not be acceptable for some websites because it
    makes it difficult to control the customer experience and also to track the
    customer.

    Newer solutions include JavaScript libraries that allow you to capture the
    credit card information in the browser and communicate to the gateway over
    AJAX.  This allows you to have complete control over the interface, but may
    not be the perfect solution for everyone.

Alternatives
____________
There are some alternative online payment providers that have been cropping up
recently.  Because of the hassles involved with credit card risk and dealing
with credit card processors, there are some companies like Dwolla or
GoCardless, that are skipping credit cards and connect directly to your bank
account for payments.  These providers seems to have drastically lower fees,
but at the downside of requiring a user to enter their bank account
information.

Additionally, if you need to make bi-directional payments, it is kind of
difficult with the traditional gateway.  Balanced Payments and Stripe Connect
are geared more towards marketplaces where the website collects money for its
users.
