from dinero import get_gateway


class DineroObject(object):
    required_attributes = []

    def __getattr__(self, attr):
        if attr == '__setstate__':
            raise AttributeError
        try:
            return self.data[attr]
        except KeyError as e:
            raise AttributeError(e)

    def __setattr__(self, attr, val):
        if attr in self.required_attributes + ['data', 'gateway_name']:
            self.__dict__[attr] = val
        else:
            self.data[attr] = val

    @classmethod
    def from_dict(cls, dict):
        gateway_name = dict.pop('gateway_name')
        kwargs = dict['data']
        kwargs.update(dict((key, dict[key])
                           for key in cls.required_attributes))
        return cls(gateway_name, **kwargs)

    def __init__(self, gateway_name, **kwargs):
        self.gateway_name = gateway_name
        for key in self.required_attributes:
            setattr(self, key, kwargs.pop(key))
        self.data = kwargs

    def to_dict(self):
        return vars(self)

    @property
    def gateway(self):
        return get_gateway(self.gateway_name)
