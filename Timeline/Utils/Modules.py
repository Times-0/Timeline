'''
Timeline - An AS3 CPPS emulator, written by dote, in python. Extensively using Twisted modules and is event driven.
Modules : ModuleHandler handles all modules in the given dir, and takes carre of it's auto-refreshment when it's edited!
		  Will make sure it doesn't reload if it has any error!
'''

from Timeline.Server.Constants import TIMELINE_LOGGER
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from twisted.python.rebuild import rebuild
from twisted.internet import threads
from watchdog.observers import Observer as ModuleObserver
from watchdog.events import FileSystemEventHandler
from collections import deque
import logging
import pkgutil
import importlib
import os, sys

class ModulesEventHandler(FileSystemEventHandler):
	def __init__(self):
		super(ModulesEventHandler, self).__init__()

	def on_created(self, event):
		directory = event.is_directory
		path = event.src_path

		if directory:
			relative_path = path[len(self.module_package):].rstrip("/").rstrip("\\").lstrip("/").lstrip("\\").replace("\\", ".").replace("/", '.')
			module_name = "{0}.{1}".format(self.parent_module_name, relative_path)

			module_parent_path = "/".join(path.replace("\\", "/").split("/")[:-1])
			module_parent_scope = ".".join(module_name.split(".")[:-1])
			self.loadModules(module_parent_scope, [module_parent_path])

			self.logger.info("on_created_directory: {0}".format(module_name))
			return

		if not path.startswith(self.module_package) or not path.endswith(".py"):
			return

		relative_path = path[len(self.module_package):-3].rstrip("/").rstrip("\\").lstrip("/").lstrip("\\").replace("\\", ".").replace("/", '.')
		module_name = "{0}.{1}".format(self.parent_module_name, relative_path)

		module_parent_path = "/".join(path.replace("\\", "/").split("/")[:-1])
		module_parent_scope = (".".join(module_name.split(".")[:-1]))
		self.loadModules(module_parent_scope, [module_parent_path])		

		self.logger.info("on_created: {0}".format(module_name))

	def on_moved(self, event):
		directory = event.is_directory
		path = event.src_path
		path2 = event.dest_path

		relative_path = path[len(self.module_package):-3].rstrip("/").rstrip("\\").lstrip("/").lstrip("\\").replace("\\", ".").replace("/", '.')
		module_name = "{0}.{1}".format(self.parent_module_name, relative_path)

		relative_path2 = path2[len(self.module_package):-3].rstrip("/").rstrip("\\").lstrip("/").lstrip("\\").replace("\\", ".").replace("/", '.')
		module_name2 = "{0}.{1}".format(self.parent_module_name, relative_path2)

		module_parent_path = "/".join(path2.replace("\\", "/").split("/")[:-1])
		module_parent_scope = ".".join(module_name2.split(".")[:-1])

		if directory:
			relative_path = path[len(self.module_package):].rstrip("/").rstrip("\\").lstrip("/").lstrip("\\").replace("\\", ".").replace("/", '.')
			module_name = "{0}.{1}".format(self.parent_module_name, relative_path)

			relative_path2 = path2[len(self.module_package):].rstrip("/").rstrip("\\").lstrip("/").lstrip("\\").replace("\\", ".").replace("/", '.')
			module_name2 = "{0}.{1}".format(self.parent_module_name, relative_path2)

			module_parent_path = "/".join(path2.replace("\\", "/").split("/"))
			module_parent_scope = ".".join(module_name2.split(".")[:-1])

			self.clearModules(module_name, True)
			self.loadModules(module_parent_scope, [module_parent_path])

			self.logger.info("on_moved_directory: from {0} to {1}".format(module_name, module_name2))
			return

		if not path.startswith(self.module_package) or not path.endswith(".py") or not path2.startswith(self.module_package) or not path2.endswith(".py"):
			return

		self.clearModules(module_name)
		
		self.loadModules(module_parent_scope, [module_parent_path])

		self.logger.info("on_moved: from {0} to {1}".format(module_name, module_name2))

	def on_deleted(self, event):
		directory = event.is_directory
		path = event.src_path

		relative_path = path[len(self.module_package):-3].rstrip("/").rstrip("\\").lstrip("/").lstrip("\\").replace("\\", ".").replace("/", '.')
		module_name = "{0}.{1}".format(self.parent_module_name, relative_path)

		pyc_path = "{0}.pyc".format(path[:-3])	

		if not path.endswith(".py"):
			relative_path = path[len(self.module_package):].rstrip("/").rstrip("\\").lstrip("/").lstrip("\\").replace("\\", ".").replace("/", '.')
			module_name = "{0}.{1}".format(self.parent_module_name, relative_path)

			self.clearModules(module_name, True)
			
			self.logger.info("on_deleted_directory: {0}".format(module_name))
			return

		if not path.startswith(self.module_package) or not path.endswith(".py"):
			return

		self.clearModules(module_name)
		if os.path.isfile(pyc_path):
			os.remove(pyc_path)
			self.logger.info("Cleared cached python file for {0}".format(module_name))

		self.logger.info("on_deleted: {0}".format(module_name))

	def on_modified(self, event):
		directory = event.is_directory
		path = event.src_path

		if not path.startswith(self.module_package) or not path.endswith(".py") or directory:
			return

		relative_path = path[len(self.module_package):-3].rstrip("/").rstrip("\\").lstrip("/").lstrip("\\").replace("\\", ".").replace("/", '.')
		module_name = "{0}.{1}".format(self.parent_module_name, relative_path)

		self.clearModules(module_name, only_unset = True)
		self.reloadModules(module_name)

		self.logger.info("on_modified: {0}".format(module_name))

class ModuleHandler(ModulesEventHandler):

	def __init__(self, module):
		super(ModuleHandler, self).__init__()

		self.module_parent = module
		self.parent_module_name = self.module_parent.__name__
		self.module_package = self.module_parent.__path__[-1]
		self.modules = deque()
		self.logger = logging.getLogger(TIMELINE_LOGGER)

	def unsetEventsInModulesAndSubModules(self, name):
		Event.unsetEventsInModulesAndSubModules(name)
		PacketEventHandler.unsetEventsInModulesAndSubModules(name)
		GeneralEvent.unsetEventsInModulesAndSubModules(name)

	def unsetEventInModule(self, name):
		Event.unsetEventInModule(name)
		PacketEventHandler.unsetEventInModule(name)
		GeneralEvent.unsetEventInModule(name)

	def clearModules(self, name = None, submodules = False, only_unset = False):
		main_module = False
		
		for module in list(self.modules):
			if name != None:
				if module.__name__ == name or (submodules and module.__name__.startswith(name) and main_module):
					if submodules:
						self.unsetEventsInModulesAndSubModules(module.__name__)
						main_module = True
					else:
						self.unsetEventInModule(module.__name__)

					if not only_unset:
						self.modules.remove(module)
						del module
			else:
				if submodules:
					self.unsetEventsInModulesAndSubModules(module.__name__)
				else:
					self.unsetEventInModule(module.__name__)

				if not only_unset:
					self.modules.remove(module)
					del module

		if name == None and submodules == False:
			self.modules.clear()

	def reloadModules(self, name = None):
		for i in range(len(self.modules)):
			try:
				if name == None:
					self.modules[i] = rebuild(self.modules[i])
				elif self.modules[i].__name__ == name:
					self.modules[i] = rebuild(self.modules[i])
			except Exception, e:
				self.logger.error("Error rebuilding - {0}".format(self.modules[i].__name__))
				self.logger.error("[TE030] {0}".format(e))

		return self.modules

	def loadModules(self, scope = None, _path = None):
		ms_path = self.module_parent.__path__ if _path == None else _path
		ms_name = self.module_parent.__name__ if scope == None else scope.strip('.')
		for im, name, ispkg in pkgutil.iter_modules(ms_path):
			mscope = "{0}.{1}".format(ms_name, name)

			hm = importlib.import_module(mscope, package=ms_path)
			if ispkg:
				self.loadModules(hm.__name__, hm.__path__)
				continue

			self.modules.append(hm)

	def modulesLoaded(self, a):
		for module in self.modules:
			if hasattr(module, 'init'):
				getattr(module, 'init')()

		self.logger.info("Loaded a fresh set of {1} module(s) in {0}".format(self.module_parent.__name__, len(self.modules)))

	def autoReloadModules(self, a):
		Observer = ModuleObserver()
		ModuleEventHandler = self

		Observer.schedule(ModuleEventHandler, path=self.module_parent.__path__[0], recursive=False)
		Observer.start()

	def loadingException(self, err):
		self.logger.error("[Error loading module] : {}".format(err.getErrorMessage()))
		sys.exit(0)

	def startLoadingModules(self):
		self.modules.clear()

		defer = threads.deferToThread(self.loadModules)
		defer.addCallback(self.modulesLoaded)
		defer.addCallback(self.autoReloadModules) #Prefer doing more research on this to get a better implementation
		defer.addErrback(self.loadingException)

		self.logger.info("Loading modules in: {0}".format(self.module_parent.__name__))
		return defer
