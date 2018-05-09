'''
Timeline - An AS3 CPPS emulator, written by dote, in python. Extensively using Twisted modules and is event driven.
Packets : PacketHandler - Handles the packets given and executed a defered request.
'''

from Timeline.Server.Constants import TIMELINE_LOGGER, PACKET_TYPE, PACKET_DELIMITER, AVAILABLE_XML_PACKET_TYPES
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent

from twisted.python.rebuild import rebuild
from twisted.internet import threads

from lxml.etree import fromstring as parseXML
from lxml import etree as XML

from collections import deque
import logging
import os
import json

class PacketHandler(object):

	def __init__(self, penguin):
		self.penguin = penguin

	def tryParseXML(self, xml_data):
		try:
			if not self.penguin.ReceivePacketEnabled:
				return True

			XMLdata = parseXML(str(xml_data))
			
			t = XMLdata.get('t')
			if t not in AVAILABLE_XML_PACKET_TYPES:
				return None

			body = XMLdata.xpath('//body')
			for i in range(len(body)):
				b = body[i]
				action = b.get("action") # Just to make sure `action` exists!

			return [t, body]

		except:
			return None

	def tryParseXT(self, xt_data):
		try:
			xt_data = str(xt_data)
			if not xt_data.startswith(PACKET_DELIMITER) or not self.penguin.ReceivePacketEnabled:
				return None

			data = xt_data.split(PACKET_DELIMITER)
			# '', 'xt', 'cat', 'hand', 'room', ''
			if len(data) < 6:
				return None

			t = data[1]
			if t != PACKET_TYPE:
				return None

			category = data[2]
			handler = data[3]
			# TODO : Strict check room internal id.
			internal_id = data[4]

			client_data = data[5:-1]

			if not self.penguin.canRecvPacket:
				# Check for exceptions
				ignores = [(i[0], i[1]) for i in self.penguin.ignorableXTPackets]
				packet = (category, handler)

				if packet in ignores:
					pid = ignores.index(packet)
					p_d = self.penguin.ignorableXTPackets[pid]
					if p_d[2] == 0:
						return True

				else:
					return None

			return [category, handler, client_data]

		except Exception, e:
			print e
			return None

	def parsePacket(self, data):
		_data = self.tryParseXML(data)
		if not _data and data.startswith("<"):
			self.penguin.disconnect()
			raise Exception("[TE001] Malformed XML String")

		if _data:
			return self.executePacket(_data, 1)

		_data = self.tryParseXT(data)
		if not _data and data.startswith(PACKET_DELIMITER):
			self.penguin.disconnect()
			raise Exception("[TE002] Malformed XT String")

		if _data:
			return self.executePacket(_data, 2)
		
		raise Exception("[TE003] Unhandled Packet Type")

		# JSON NOT HANDLED ATM

	'''
	@param[type] : 1 -> XML, 2 -> XT, 3 -> JSON
	'''
	def executePacket(self, data, type):
		if type == 1:
			if data == True:
				return False

			for i in range(len(data[1])):
				body = data[1][i]
				action = body.get("action")

				event = "{2}:{3}-></{0}-{1}>".format(data[0], action, self.penguin.engine.type, self.penguin.Protocol)
				RuleHandler = PacketEventHandler.FetchRule('xml', action, data[0], self.penguin.engine.type, self.penguin.Protocol)
				
				if RuleHandler != None:
					args, kwargs = RuleHandler(body)
				else:
					args, kwargs = [[], {}]

				args = [self.penguin] + args

				PacketEventHandler.call(event, args = (self.penguin, body), rules_a = args, rules_kwarg = kwargs)

		elif type == 2:
			if data == True:
				return False

			event = "{2}:{3}->%{0}%{1}%".format(data[0], data[1], self.penguin.engine.type, self.penguin.Protocol)
			RuleHandler = PacketEventHandler.FetchRule('xt', data[0], data[1], self.penguin.engine.type, self.penguin.Protocol)
			if RuleHandler != None:
				args, kwargs = RuleHandler(data)
			else:
				args = []
				kwargs = {}

			args = [self.penguin] + args

			PacketEventHandler.call(event, args = [self.penguin, data], rules_a = args, rules_kwarg = kwargs)

		elif type == 3:
			return False

		return True

	def handlePacketReceived(self, line):
		if line == "<policy-file-request/>":
			deferedHandler = threads.deferToThread(self.penguin.handleCrossDomainPolicy)
		else:
			deferedHandler = threads.deferToThread(self.parsePacket, line)
		
		return deferedHandler

	def buildXML(self, node):
		root = XML.Element(node.keys()[0])
		self.buildXMLNodes(root, node[node.keys()[0]])
		return XML.tostring(root)

	def buildXMLNodes(self, element, node):
		if type(node) is str or type(node) is int or type(node) is bool:
			node = str(node)
			element.text = XML.CDATA(node)
		else:
			for k, v in node.iteritems():
				if type(v) is dict:
					# serialize the child dictionary
					child = XML.Element(k)
					self.buildXMLNodes(child, v)
					element.append(child)
				elif type(v) is list:
					if k[-1] == 's':
						name = k[:-1]
					else:
						name = k

					for item in v:
						child = XML.Element(name)
						self.buildXMLNodes(child, item)
						element.append(child)
				else:
					# add attributes to the current element
					element.set(k, unicode(v))
