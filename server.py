#!/usr/bin/env python
#
#       server.py
#       
#       Alice

from bus import *
import pygame, time

def main():
	clients = {}
	bus = Bus('localhost', 21567, 21568)
	print str(bus)
	quit = False
	
	while not quit:
		for i, string in enumerate(bus.data):
			if string == '':
				continue
			print ''
			print str(bus.fromAddress[i]) + ' (' + time.strftime('%X') + '): ' + string
			data = ''
			for n in parse_string(string):
				property = n[0]
				value = n[1]
				if property == ('login'):
					clients[bus.fromAddress[i]] = value
					print str(bus.fromAddress[i]) + ' mapped to username \'' + value + '\''
				elif property == ('logoff'):
					if bus.fromAddress[i] in clients:
						del clients[bus.fromAddress[i]]
					print str(bus.fromAddress[i]) + ' removed from user map'	
				elif property == ('clientchatmessage'):
					try:
						data = 'chatmessage=' + value
						data += '\tusername=' + clients[bus.fromAddress[i]]
						for client in clients:
							print 'sending to '+ str(client) + ': ' + data
							bus.send(data, client[0])
					except KeyError:
						print 'Anonymous data from ' + str(bus.fromAddress[i])				
				#elif property == ('username'):
				#	username = 
		pygame.time.wait(100)		
	return 0

if __name__ == '__main__': main()
