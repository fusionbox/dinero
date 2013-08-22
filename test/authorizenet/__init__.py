import os
import dinero

# These tests require that you provide settings for authorize.net and set up
# your account to reject invalid CVV and AVS responses
LOGIN_ID = os.environ["AUTHNET_LOGIN_ID"]
TRANSACTION_KEY = os.environ["AUTHNET_TRANSACTION_KEY"]

dinero.configure({
    'authorize.net': {
        'type': 'dinero.gateways.AuthorizeNet',
        'login_id': LOGIN_ID,
        'transaction_key': TRANSACTION_KEY,
        'default': True,
    }
})
