from Timeline.Utils.Plugins.AbstractManager import AbstractManager
from abc import abstractproperty

class ExtensibleObject(object):
    '''
    In a safer side, inherit all class you want to make 'Extensible' from this ExtensibleObject.
    '''

    extend = True

    pass

class Abstract(AbstractManager):
    """
    Base definition for all Timeline Plugins.
    All plugins must inherit Abstract to be promoted as a Plugin.

    Direct usage of Abstract into a plugin base class is not recommended. It is recommended to build a interface upon which a plugin is built on.
    """

    __plugin_req = list()

    @abstractproperty
    def requirements(self):
        return self.__plugin_req

    @requirements.setter
    def requirements(self, req):
        self._plugin_req = list(req)

    """
    element : tuple
        syntax: (Plugin code name, plugin version [0 for any version], )

        Rejects the following plugin if requirements not satisfied with an error.
    """

    __plugin_name = 'AbstractPlugin - {0}'
    __plugin_code = None
    __plugin_author = 'anonymous'
    __plugin_version = 0

    def __str__(self):
        return self.name
    
    def __int__(self):
        return self.__plugin_version

    @abstractproperty
    def name(self):
        return self.__plugin_name
    
    @name.setter
    def name(self, name):
        self.__plugin_name = str(name)
    
    @abstractproperty
    def code(self):
        return id(self)    
    
    @abstractproperty
    def developer(self):
        return self.__plugin_author
    
    @developer.setter
    def developer(self, name):
        self.__plugin_author = str(name)

    @abstractproperty
    def version(self):
        return self.__plugin_version
    
    @version.setter
    def version(self, v):
        self.__plugin_version = int(v)


