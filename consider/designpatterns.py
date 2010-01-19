
class Singleton(object):
    def __new__(cls):
        if not '_theInstance' in cls.__dict__:
            cls._theInstance = object.__new(cls)
        return cls._theInstance

class Borg(object):
    _sharedState = {}
    def __new__(cls, *params, **kwargs):
        self = object.__new__(cls, *params, **kwargs)
        self.__dict__ = cls._sharedState
        return self
