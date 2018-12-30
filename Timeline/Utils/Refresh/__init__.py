class PenguinObject(dict):

    def __init__(self, value=None):
        dict.__init__(self)
        self.POvalue = value

    def __repr__(self):
        values = list()

        for i, j in dict.iteritems(self):
            values.append("{0}={1}".format(i, j))

        values = ", ".join(values)
        return "<{0}: {1}>".format(self.__class__.__name__, values)

    def __getitem__(self, key):
        try:
            value = (dict.__getitem__(self, key))
        except:
            value = None
            dict.__setitem__(self, key, value)
        finally:
            return value

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)

    def __setattr__(self, attr, value):

        dict.__setitem__(self, attr, value)
        object.__setattr__(self, attr, value)

    def __getattr__(self, attr):
        try:
            value = (dict.__getitem__(self, attr))
        except:
            value = None
            dict.__setitem__(self, attr, value)
        finally:
            return value
