'''
Timeline - An AS3 CPPS emulator, written by dote, in python. Extensively using Twisted modules and is event driven.
Events : Initiates Twisted-defer based Packet-Event handler!!
'''

from Timeline.Server.Constants import TIMELINE_LOGGER
from twisted.internet.defer import Deferred
import logging

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
			_func = EventListener(event, function, self)
			self.addListener(event, _func)

			return function

		if function != None:
			self.addListener(event, function)
			return function

		return func

	def call(self, e, *a, **kw):
		defer = Deferred()

		if not e in self.events:
			return defer

		for l in self.events[e]:
			defer.addCallback(l)

		EventDetails = {'e' : e, 'a' : a, 'kw' : kw}

		defer.callback(EventDetails)
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
		return self.call(event, *a, **kw)

	@staticmethod
	def Event():
		if Event.EventObject == None:
			Event()

		return Event.EventObject

class EventListener(object):

	def __init__(self, name, func, k):
		self.name = name
		self.function = func
		self.module = self.function.__module__
		self.x = k

	def __call__(self, event):
		if event == None:
			return
		ra = event['a']
		kw = event['kw']
		if 'ra' in event and self in PacketEventHandler.function_w_rules:
			ra = event['ra']
			kw = event['rkw']

		a = self.function(*ra, **kw)

		if isinstance(a, Deferred):
			def err(x):
				a = x.getTraceback().split('\n')
				self.x.logger.error("Error executing method - {} : {}".format(self.function.__name__, x.getErrorMessage() + "["+ a[-2].strip() + ' in ' + a[-4].strip() +"]"))
				
			a.addErrback(err)

class PacketEvent(Event):

	"""
	PacketEvent : Handles all XT and XML packet events. Inherits Event!
	"""

	def __init__(self):
		super(PacketEvent, self).__init__()
		self.Event = Event.Event()
		self.packet_rules = dict() # Available packet rules. ie, cat|handler : rule
		self.function_w_rules = list() # Functions
		self.logger = logging.getLogger(TIMELINE_LOGGER)

    #                   xml   action data engin  
	def FetchRule(self, type, c, h_t, s_t):
		type = str(type).lower()
		rule = "{3}->{2}^{0}|{1}".format(c, h_t, type, s_t)

		if rule in self.packet_rules:
			return self.packet_rules[rule]

		return None

	def XTPacketRule(self, c, h, s_t, function = None):
		rule = '{2}->xt^{0}|{1}'.format(c, h, s_t)
		def func(function):
			self.packet_rules[rule] = function
			return function

		if function != None:
			self.packet_rules[rule] = function
			return function

		return func

	def XMLPacketRule(self, a, s_t, t = 'sys', function = None):
		rule = "{2}->xml^{0}|{1}".format(a, t, s_t)
		
		def func(function):
			self.packet_rules[rule] = function
			return function

		if function != None:
			self.packet_rules[rule] = function
			return function

		return func

	def on(self, _type, category, server_type, handler=None):
		_type = str(_type).lower()
		if _type == 'xml':
			return self.onXML(category, server_type)

		elif _type == 'xt':
			return self.onXT(category, handler, server_type)

		else:
			raise TypeError("Unknown or unhandled packet type {0}".format(_type))

	def call(self, e, args = (), kwargs = {}, rules_a = (), rules_kwarg = {}):
		defer = Deferred()

		if not e in self.events:
			return defer

		for l in self.events[e]:
			defer.addCallback(l)

		EventDetails = {'e' : e, 'a' : args, 'kw' : kwargs, 'ra' : rules_a, 'rkw' : rules_kwarg}

		defer.callback(EventDetails)
		return defer

	def on_packet(self, event, isruled):
		event = str(event)
		
		def func(function):
			_func = EventListener(event, function, self)
			self.addListener(event, _func)
			if isruled:
				self.function_w_rules.append(_func)

			return function

		return func

	def onXML(self, action, server_type, type = 'sys', p_r = True):
		event = "{2}-></{1}-{0}>".format(str(action), type, str(server_type))
		return self.on_packet(event, p_r) #super(PacketEvent, self).on(event)

	def onXT(self, c, h, s_t, p_r = True):
		event = "{2}->%{0}%{1}%".format(str(c), str(h), str(s_t))
		return self.on_packet(event, p_r) #super(PacketEvent, self).on(event)

class GeneralEvent(Event):

	def __init__(self):
		super(GeneralEvent, self).__init__()
		self.Event = Event.Event()

PacketEventHandler = PacketEvent()
GeneralEvent = GeneralEvent()
Event = Event.Event()
