from Timeline.Utils.Plugins.Abstract import Abstract
from Timeline.Utils.Plugins.AbstractManager import Abstraction

class Requirement:
    name = None
    code = 0
    developer = None
    version = 0

    def __init__(self, **kw):
        req_args = ['name', 'code', 'developer', 'version']
        for arg in req_args:
            if arg in kw:
                setattr(self, arg, kw[arg])

class RequirementsManager(object):

    @classmethod
    def getRequirement(cls, req, ps = None):
        if req.name == None and req.code == 0 and req.developer == None and req.version == 0:
                return None
            
        if req.name is not None and (req.code is None and req.developer is None):
            return None

        if req.name and req.developer:
            plugins =  Abstraction.getAllPluginsByDeveloper(req.developer, ps)

            for p in plugins:
                if p.name is not req.name: continue

                if p.version is not 0 and req.version != 0 and p.version < req.version:
                    return None
                
                return p

        elif req.code is not 0:
            if not Abstraction.PluginExists(req.code, ps):
                return None

            plugin = Abstraction.getPlugin(_id, ps)
            if plugin.version != 0 and req.version != 0 and plugin.version < req.version:
                return None

            return Plugin

        return None

    @classmethod
    def getAllRequirements(cls, requirements):
        req = list()

        for r in requirements:
            if not isinstance(r, Requirement):
                continue
            
            reqm = RequirementsManager.getRequirement(r)
            if reqm is not None:
                req.append(reqm)

        return req
    
    @classmethod
    def checkForRequirements(cls, requirements):
        for req in requirements:
            if req.name == None and req.code == 0 and req.developer == None and req.version == 0:
                continue
            
            if req.name is not None and (req.code is None and req.developer is None):
                raise ReferenceError("Unable to satisfy requirements. Only Plugin name passed, required code name or developer name.")

            if req.name and req.developer:
                plugins =  Abstraction.getAllPluginsByDeveloper(req.developer)
                found = sum(p.name == req.name for p in plugins) > 0
                if not found:
                    raise NotImplementedError("Requirement not satsfied for {}".format(req.name))

                for p in plugins:
                    if p.name is not req.name: continue

                    if p.version is not 0 and req.version != 0 and p.version < req.version:
                        raise ImportError("Plugin version not satisfied for {}".format(req.name))
                    break

            elif req.code is not 0:
                if not Abstraction.PluginExists(req.code):
                    raise NotImplementedError("Requirement not satisfied for key:{}".format(req.code))

                plugin = Abstraction.getPlugin(_id)
                if plugin.version != 0 and req.version != 0 and plugin.version < req.version:
                    raise ImportError("Plugin version not satisfied for {}".format(plugin))

class IPluginAbstractMeta (type):

    def __init__(cls, name, bases, attrs):
        cls.onBuild()

class IPlugin(Abstract):
    """
    Defined the base class of Plugin Objects. All plugin classes are recommended to inherit from this base class.
    """

    requirements = list()

    name = "plugin_name"
    '''
    str : Name of the plugin
    '''
    developer = "developer_name"
    '''
    str : Plugin developer's name
    '''
    version = 0
    '''
    int : Version of the current plugin. Default 0, 0 specifies the plugin is version(less or) independent
    '''

    def __new__ (cls):
        #check for requirements first!
        requirements = list(cls.requirements)

        for i in range(len(requirements)):
            req = requirements[i]
            if isinstance(req, dict):
                req = requirements[i] = Requirement(**req)

            elif not isinstance(req, Requirement):
                raise TypeError("Expected type `Requirements` found `{}` instead".format(type(req).__name__))
        
        RequirementsManager.checkForRequirements(requirements)

        return super(IPlugin, cls).__new__(cls)

    def __init__(self):
        self.dependencies = list()
        """
        List of plugin instances current plugin depends upon
        """

        self.dependent = list()
        '''
        List if plugins which depend on current plugin
        '''

        self.loadDependencies()

        super(IPlugin, self).__init__(self)

    def loadDependencies(self):
        self.dependencies = RequirementsManager.getAllRequirements(self.requirements)
        for dependency in self.dependencies:
            dependencies.on_dependency(self)

    def on_dependency(self, plugin):
        self.dependent.append(plugin)