from abc import ABCMeta

class Abstraction:
    loaded_plugins = list()

    @classmethod
    def PluginExists(cls, _id,  ps = None):
        plugins = Abstraction.loaded_plugins if ps is None else ps
        for plugin in plugins:
            if plugin[0] == _id:
                return True
        
        return False
    
    @classmethod
    def getPlugin(cls, _id,  ps = None):
        plugins = Abstraction.loaded_plugins if ps is None else ps
        for plugin in plugins:
            if plugin[0] == _id:
                return plugin[1]
        
        return None
    
    @classmethod
    def getAllPlugins(cls):
        return list(p[1] for p in Abstraction.loaded_plugins)

    @classmethod
    def getAllPluginsByDeveloper(cls, dev,  ps = None):
        plugins = list()
        _plugins = Abstraction.loaded_plugins if ps is None else ps
        for plugin in _plugins:
            if plugin[1].developer == dev:
                plugins.append(plugin[1])

        return plugins

class AbstractManager(object):
    """
    AbstractManager: base type for any plugin
    """

    def __new__ (cls, *args, **kwargs):
        instance = super(AbstractManager, cls).__new__(cls, *args, **kwargs)
        _id = instance.code

        Abstraction.loaded_plugins.append((_id, instance))
        return instance

    pass