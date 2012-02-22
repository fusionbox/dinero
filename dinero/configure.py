

def fancy_import(name):
    """
    This takes a fully qualified object name, like
    'dinero.gateways.AuthorizeNet', and turns it into the
    dinero.gateways.AuthorizeNet object.
    """

    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


_configured_gateways = {}


def configure(options):
    """
    Takes a dictionary of name -> gateway configuration pairs.
    configure({
        'auth.net': { # the name for this gateway
            'default': True, # register as the default gateway
            'type': 'dinero.gateways.AuthorizeNet' # the gateway path
            # ... gateway-specific configuration
        }})

    `settings.py` is a great place to put this call in a Django project.
    """
    for name, conf in options.iteritems():
        _configured_gateways[name] = fancy_import(conf['type'])(conf)
        _configured_gateways[name].name = name


def get_gateway(gateway_name=None):
    """
    Returns a configured gateway.  If no gateway name is provided, it returns
    the config marked as 'default'.
    """
    if gateway_name is None:
        return get_default_gateway()
    return _configured_gateways[gateway_name]


def get_default_gateway():
    """
    Returns the default gateway name.  If no gateway is found, a KeyError is thrown.

    Why KeyError?  That is the same error that would be thrown if _configured_gateways
    was accessed with a gateway name that doesn't exist.
    """
    for name, conf in _configured_gateways.iteritems():
        if 'default' in conf and conf['default']:
            return conf
    raise KeyError("Could not find a gateway configuration that is assigned as 'default'")
