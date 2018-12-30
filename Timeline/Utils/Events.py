'''
Timeline - An AS3 CPPS emulator, written by dote, in python. Extensively using Twisted modules and is event driven.
Events : Initiates Twisted-defer based Packet-Event handler!!
'''

from Timeline.Server.Constants import TIMELINE_LOGGER, AS3_PROTOCOL, AS2_PROTOCOL
from twisted.internet.defer import Deferred, inlineCallbacks, returnValue, maybeDeferred
from twisted.internet.threads import deferToThread
import logging, traceback

class Event(object):

    """
    Events: A class that is common to both PacketEvent and GeneralEvent
    """

    EventObject = None

    def __init__(self):
        super(Event, self).__init__()
        Event.EventObject = self
        self.events = dict()
        self.logger = logging.getLogger(TIMELINE_LOGGER)

    def removeListener(self, event, function):
        if event in self.events and function in self.events[event]:
            self.events[event].remove(function)

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
            return func(function)

        return func

    @inlineCallbacks
    def callback(self, fn, E):
        for i in fn:
            yield maybeDeferred(i, E)

    def call(self, e, *a, **kw):
        defer = Deferred()
        if not e in self.events:
            return defer

        EventDetails = {'e' : e, 'a' : a, 'kw' : kw}
        return maybeDeferred(self.callback, self.events[e], EventDetails)

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
        event = dict(event)
        ra = event['a']
        kw = event['kw']
        if 'ra' in event and self in PacketEventHandler.function_w_rules:
            ra = event['ra']
            kw = event['rkw']

        a = maybeDeferred(self.function, *ra, **kw)
        def err(x):
            a = x.getTraceback().split('\n')
            self.x.logger.error("Error executing method - {} : {}".format(self.function.__name__, x.getErrorMessage() + "["+ a[-2].strip() + ' in ' + a[-4].strip() +"]"))
            x.printDetailedTraceback()

        a.addErrback(err)
        return a

class PacketEvent(Event):

    """
    PacketEvent : Handles all XT and XML packet events. Inherits Event!
    """

    def __init__(self):
        super(PacketEvent, self).__init__()
        self.Event = Event.Event()
        self.packet_rules = dict() # Available packet rules. ie, cat|handler : rule
        self.function_w_rules = list() # Functions

    def unsetEventInModule(self, module):
        events = self.packet_rules.copy()
        for event in events:
            handler = events[event]
            if handler.__module__ == module:
                del self.packet_rules[event]

        return super(PacketEvent, self).unsetEventInModule(module)

    def unsetEventsInModulesAndSubModules(self, module):
        events = self.packet_rules.copy()
        for event in events:
            handler = events[event]
            if handler.__module__.startswith(module):
                del self.packet_rules[event]

        return super(PacketEvent, self).unsetEventsInModulesAndSubModules(module)

    #                   xml   action data engin  
    def FetchRule(self, type, c, h_t, s_t, server_protocol):
        type = str(type).lower()
        rule = "{3}:{4}->{2}^{0}|{1}".format(c, h_t, type, s_t, server_protocol)

        if rule in self.packet_rules:
            return self.packet_rules[rule]

        return None

    def XTPacketRule(self, c, h, s_t, function = None, server_protocol = AS3_PROTOCOL):
        rule = '{2}:{3}->xt^{0}|{1}'.format(c, h, s_t, server_protocol)
        def func(function):
            self.packet_rules[rule] = function
            return function

        if function != None:
            self.packet_rules[rule] = function
            return function

        return func

    def XMLPacketRule(self, a, s_t, t = 'sys', function = None, server_protocol = AS3_PROTOCOL):
        rule = "{2}:{3}->xml^{0}|{1}".format(a, t, s_t, server_protocol)

        def func(function):
            self.packet_rules[rule] = function
            return function

        if function != None:
            self.packet_rules[rule] = function
            return function

        return func

    def XTPacketRule_AS2(self, c, h, s_t, function = None):
        return self.XTPacketRule(c, h, s_t, function, AS2_PROTOCOL)

    def XMLPacketRule_AS2(self, a, s_t, t = 'sys', function = None):
        return self.XMLPacketRule(a, s_t, t, function, AS2_PROTOCOL)


    def on(self, _type, category, server_type, handler=None, server_protocol = AS3_PROTOCOL):
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

        EventDetails = {'e' : e, 'a' : args, 'kw' : kwargs, 'ra' : rules_a, 'rkw' : rules_kwarg}
        events = self.events[e]

        for k in events:
            maybeDeferred(k, EventDetails)

        defer.callback(1)
        return defer

    def on_packet(self, event, isruled, _f = None):
        event = str(event)

        def func(function):
            _func = EventListener(event, function, self)
            self.addListener(event, _func)
            if isruled:
                self.function_w_rules.append(_func)

            return function

        if _f != None:
            return func(_f)

        return func

    def onXML(self, action, server_type, type = 'sys', p_r = True, function = None, server_protocol = AS3_PROTOCOL):
        event = "{2}:{3}-></{1}-{0}>".format(str(action), type, str(server_type), server_protocol)
        return self.on_packet(event, p_r, function) #super(PacketEvent, self).on(event)

    def onXT(self, c, h, s_t, p_r = True, function = None, server_protocol = AS3_PROTOCOL):
        event = "{2}:{3}->%{0}%{1}%".format(str(c), str(h), str(s_t), server_protocol)
        return self.on_packet(event, p_r, function) #super(PacketEvent, self).on(event)

    def onXML_AS2(self, action, server_type, type = 'sys', p_r = True, function = None):
        return self.onXML(action, server_type, type, p_r, function, AS2_PROTOCOL)

    def onXT_AS2(self, c, h, s_t, p_r = True, function = None):
        return self.onXT(c, h, s_t, p_r, function, AS2_PROTOCOL)

class GeneralEvent(Event):

    def __init__(self):
        super(GeneralEvent, self).__init__()
        self.Event = Event.Event()

PacketEventHandler = PacketEvent()
GeneralEvent = GeneralEvent()
Event = Event.Event()
