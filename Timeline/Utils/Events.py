'''
Timeline - An AS3 CPPS emulator, written by dote, in python. Extensively using Twisted modules and is event driven.
Events : Initiates Twisted-defer based Packet-Event handler!!
'''

from twisted.internet.defer import Deferred

class Event(object):

	"""
	Events: A class that is common to both PacketEvent and GeneralEvent
	"""

	EventObject = None

	def __init__(self):
		super(Event, self).__init__()
		Event.EventObject = self
		self.events = dict()

	def addListener(self, event, function):
		if not event in self.events:
			self.events[event] = list()

		self.events[event].append(function)
		return function

	def on(self, event, function = None):
		event = str(event)

		def func(function):
			_func = EventListener(event, function)
			self.addListener(event, _func)

			return _func

		if function != None:
			self.addListener(event, function)
			return function

		return func

	def call(self, e, a, kw):
		defer = Deferred()

		if not e in self.events:
			return defer

		for l in self.events[e]:
			defer.addCallback(l, a = a, kw = kw)

		defer.callback(e)
		return defer

	def unsetEventInModule(self, module):
		events = self.events.copy()
		for event in events:
			ehandlers = events[event]
			for handler in ehandlers:
				if handler.module == module:
					self.events[event].remove(handler)

		return True

	def unsetEventsInModulesAndSubModules(self, module):
		events = self.events.copy()
		for event in events:
			ehandlers = events[event]
			for handler in ehandlers:
				if handler.module.startswith(module):
					self.events[event].remove(handler)

		return True

	def __call__(self, event, *a, **kw):
		return self.call(event, a, kw)

	@staticmethod
	def Event():
		if Event.EventObject == None:
			Event()

		return Event.EventObject

class EventListener(object):

	def __init__(self, name, func):
		self.name = name
		self.function = func
		self.module = self.function.__module__

	def __call__(self, e, a, kw):
		return self.function(*a, **kw)

class PacketEvent(Event):

	"""
	PacketEvent : Handles all XT and XML packet events. Inherits Event!
	"""

	def __init__(self):
		super(PacketEvent, self).__init__()
		self.Event = Event.Event()

	def on(self, _type, category, handler=None):
		_type = str(_type).lower()
		if _type == 'xml':
			return self.onXML(category)

		elif _type == 'xt':
			return self.onXT(category, handler)

		else:
			raise TypeError("Unknown or unhandled packet type {0}".format(_type))

	def onXML(self, action):
		event = "</{0}>".format(str(action))
		return self.Event.on(event)

	def onXT(self, c, h):
		event = "%{0}%{1}%".format(str(c), str(h))
		return self.Event.on(event)

class GeneralEvent(Event):

	def __init__(self):
		super(GeneralEvent, self).__init__()
		self.Event = Event.Event()

PacketEventHandler = PacketEvent()
GeneralEvent = GeneralEvent()
Event = Event.Event()