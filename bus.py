#!/usr/bin/env python
#
#       bus.py
#       
#       Alice

from Queue import *
import socket

def parse_string(string):
	if string=='':
		return [['','']]
	out = []
	args = string.split('\t')
	for arg in args:
		try:
			property = arg.split('=')[0]
			value = arg[arg.find('=')+1:]
			out.append([property, value])
		except ValueError:
			pass
	return out			

class Bus(object):
	def _GetHost(self):
		return self._host
	def _SetHost(self, ip):
		try:
			self._socket.sendto('', (ip, self.toPort))
			self._socket = Bus.new_socket()
			self._socket.setblocking(0)
			self._host = ip
		except socket.gaierror:
			print 'Bus: unable to assign host to \''+ ip + '\''
	host = property(fget = _GetHost, fset = _SetHost)
	
	def _GetPort(self):
		return self._port
	def _SetPort(self, port):
		if port.__class__() == 0:
			pass	
		elif port.__class__() == '':
			try:
				port = int(port)
			except ValueError:
				return
		self._socket = Bus.new_socket()		
		self._port = port		
		self._socket.bind(('', port))	
	port = property(fget = _GetPort, fset = _SetPort)
	
	def _GetToPort(self):
		return self._toPort
	def _SetToPort(self, port):
		if port.__class__() == 0:
			pass	
		elif port.__class__() == '':
			try:
				port = int(port)
			except ValueError:
				return
		self._toPort = port	
	toPort = property(fget = _GetToPort, fset = _SetToPort)
	
	def _GetBuffer(self):
		return self._buffer
	buffer = property(fget = _GetBuffer)
	
	def _GetAddress(self):
		return (self.host, self.port)
	address = property(fget = _GetAddress)
	
	def _GetData(self):
		out = []
		addresses = []
		exit = False
		while not exit:
			try:
				data, fromAddress = self._socket.recvfrom(self._buffer)
				out.append(data)
				addresses.append(fromAddress)
			except socket.error:
				exit = True
		self._fromAddress = addresses
		return out	
	data = property(fget = _GetData)
	
	def _GetFromAddress(self):
		return self._fromAddress
	fromAddress = property(fget = _GetFromAddress)		
	
	def new_socket():
		return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	new_socket = staticmethod(new_socket)	
	
	def __init__(self, host, toPort, port):
		self._socket = Bus.new_socket()
		self.toPort = toPort
		self.host = host
		self.port = port
		self._buffer = 1024
		self._socket.setblocking(0)
		self._fromAddress = []
		
	def __str__(self):
		return 'Bus: Rcv ' + socket.gethostbyname(socket.gethostname()) + ':' + str(self.port) + '  Host ' + self.host + ':' + str(self.toPort)	
		
	def send(self, data, ip=None):
		if not ip:
			ip = self.host
		try:
			self._socket.sendto(data, (ip, self.toPort))	
		except socket.gaierror:
			print 'Bus: could not find server. Sending of', data, 'to', host, 'failed.'	
		
	#def listen(self):
	#	data, self._fromAddress = self._socket.recvfrom(self._buffer)
	#	if data:
	#		self._data.put_nowait(data)
				
