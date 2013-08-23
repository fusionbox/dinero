

def fancy_import(import_name):
    """
    This takes a fully qualified object name, like
    'dinero.gateways.authorizenet.Gateway', and turns it into the
    dinero.gateways.authorizenet.Gateway object.
    """
    import_path, import_me = import_name.rsplit('.', 1)
    imported = __import__(import_path, globals(), locals(), [import_me], -1)
    return getattr(imported, import_me)


_configured_gateways = {}


def configure(options):
    """
    Takes a dictionary of name -> gateway configuration pairs.
    configure({
        'auth.net': { # the name for this gateway
            'default': True, # register as the default gateway
            'type': 'dinero.gateways.authorizenet.Gateway' # the gateway path
            # ... gateway-specific configuration
        }})

    `settings.py` is a great place to put this call in a Django project.
    """
    for name, conf in options.iteritems():
        backend = conf['type']
        # BBB: <= 0.0.3 import paths
        if backend == 'dinero.gateways.AuthorizeNet':
            backend = 'dinero.gateways.authorizenet.Gateway'
        _configured_gateways[name] = fancy_import(backend)(conf)
        _configured_gateways[name].name = name
        is_default = conf.get('default', False)
        if is_default:
            set_default_gateway(name)
        else:
            _configured_gateways[name].default = is_default


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
    for gateway in _configured_gateways.itervalues():
        if gateway.default:
            return gateway
    raise KeyError("Could not find a gateway configuration that is assigned as 'default'")


def set_default_gateway(name):
    """
    Set a default gateway that has already been configured.
    """
    for gateway in _configured_gateways.itervalues():
        gateway.default = False
    _configured_gateways[name].default = True
