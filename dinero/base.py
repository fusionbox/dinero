class DineroObject(object):
    def __getattr__(self, attr):
        if attr == '__setstate__':
            raise AttributeError
        try:
            return self.data[attr]
        except KeyError as e:
            raise AttributeError(e)

    def to_dict(self):
        return vars(self)
