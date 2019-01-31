#!/usr/bin/env python
#
#       interface.py
#       
#       Alice

from pygame import *
from bus import *
import math

class TextInput:
	def insert(string, i, x):
		if math.fabs(i) <= len(string):
			string = string[0:i] + x + string[i:]
		return string
	insert = staticmethod(insert)	
	
	def delete(string, i, n=1):
		if i + n <= len(string):
			string = string[0:i] + string[i+n:]
		return string	
	delete = staticmethod(delete)
	
	def __init__(self, interface, fontfilename):
		self.buffer = ''
		self.bufferLength = 0
		self.strings = []
		self.textColor = (0,0,0)
		self.filename = fontfilename
		self.fontSize = 16
		self.font = font.Font(fontfilename, self.fontSize)
		self.interface = interface
		self.surface = None
		self.renderedText = Surface( (0, 0) )
		self.maxLength=50
		self.memory = ['',]
		self.maxMemory = 10
		self.memPt = 0
		self.bufPt = 0
		
	def set_font(self, fontsize, fontfilename='', color = None):
		file = self.fontfilename
		self.fontsize = fontsize
		if fontfilename != '':
			file = 	fontfilename
		self.font = font.Font(file, fontsize)
		if color != None:
			self.textColor = color
		
	def handle_input(self, commands):	
		for command in commands:
			if command.type == KEYDOWN:
				if (0x20 <= command.key <= 0x7e) and len(self.buffer) < self.maxLength:
					#self.buffer += command.unicode
					self.buffer = self.insert(self.buffer, self.bufPt, command.unicode)
					self.bufPt += 1
					self.memory[self.memPt] = self.buffer
				elif command.key==K_BACKSPACE and len(self.buffer) > 0 and self.bufPt > 0:
					#self.buffer = self.buffer[0:-1]
					self.buffer = self.delete(self.buffer, self.bufPt-1)	
					self.bufPt -= 1
					self.memory[self.memPt] = self.buffer
				elif command.key==K_RETURN:
					self.memory[0] = ''
					#self.interface.textToggle=False
					self.renderedText = Surface( (0, 0) )
					if len(self.buffer) > 0:
						self.strings.append(self.buffer)
						if self.memPt > 0:
							del self.memory[self.memPt]
						if len(self.memory) > 1:	
							self.memory.insert(1, self.buffer)
						else:
							self.memory.append(self.buffer)	
						while len(self.memory) > self.maxMemory:
							del self.memory[-1]
						self.memPt = 0	
						self.bufPt = 0
						self.buffer = ''
						return True
					else:
						self.memPt = 0
						self.memory[0] = ''
						self.buffer = ''
						self.interface.textToggle=False
						return False
				elif command.key == K_ESCAPE:
					self.buffer=''
					self.bufPt=0
					self.bufferLength = 0
					self.memPt = 0
					self.interface.textToggle=False
					self.surface = Surface( (0, 0) )
					self.renderedText = Surface( (0, 0) )
					return False	
				elif command.key == K_UP:
					if self.memPt + 1 < len(self.memory):
						self.memPt += 1
						self.buffer = self.memory[self.memPt]
				elif command.key == K_DOWN:
					if self.memPt - 1 >= 0:
						self.memPt -= 1
						self.buffer = self.memory[self.memPt]
				elif command.key == K_LEFT:
					if self.bufPt > 0:
						self.bufPt -= 1
				elif command.key == K_RIGHT:
					if self.bufPt < len(self.buffer):
						self.bufPt += 1				
			if self.bufPt >= len(self.buffer):
				self.bufPt = len(self.buffer)
			self.renderedText = self.font.render(self.buffer, self.interface.world.video.smoothText, self.textColor)
		return False
		
	def get_string(self):
		if len(self.strings) > 0:
			out = self.strings.pop(0)
			return out
		else:
			return ''
			
	def get_buffer(self):
		return self.buffer	
		
	def get_surface(self):
		#if self.surface != None:
		#	if offset == (-1,-1):
		#		 offset=(0,self.interface.world.video.interface.height-self.font.get_height()) 
		#	self.surface.blit(self.renderedText, offset )
		return self.renderedText	
			
class Interface:
	def _GetConsoleHeight(self):
		return (len(self.consoleBuffer)+1)*self.textInput.font.get_height()
	consoleHeight = property(fget = _GetConsoleHeight)	
	
	def __init__(self,world):
		self.world = world
		self.surface = Surface((self.world.video.interface.width, self.world.video.interface.height))
		self.textInput = TextInput(self, 'data/Arial.ttf')	
		self.surface.set_colorkey( (0xff, 0xff, 0xff) )
		self.textToggle = False
		self.consoleRows=5
		self.consoleBuffer = []
		self.consoleSurface = None
		self.bg = None
		self.textXOffset = 5
		self.bus = Bus('localhost', 21568, 21567)
		self.username = 'Anonymous'
		self.bus.send('login=' + self.username)
		self.ticker = time.Clock()
	
	def set_bg(self, filename):
		try:
			self.bg = image.load(filename).convert_alpha()
		except error:
			print 'Could not load bg image for interface.'	 
	
	def set_dimensions(self):
		self.surface = Surface((self.world.video.interface.width, self.world.video.interface.height))
	
	def get_console_surface(self):
		self.consoleSurface = Surface( (self.surface.get_width()/2, self.surface.get_height() ) )
		self.consoleSurface.fill( (0xff, 0xff, 0xff) )
		self.consoleSurface.set_colorkey( (0xff, 0xff, 0xff) )
		if self.textToggle:
			self.consoleSurface.blit(self.textInput.get_surface(), (self.textXOffset, self.consoleSurface.get_height() - self.textInput.get_surface().get_height() ) )
			if len(self.textInput.buffer) == 0:
				x = 0
			else:
				x = self.textInput.get_surface().get_width() * self.textInput.bufPt / len(self.textInput.buffer)
			draw.line(self.consoleSurface, self.textInput.textColor, (x+self.textXOffset, self.consoleSurface.get_height()-self.textInput.font.get_height()), (x+self.textXOffset, self.consoleSurface.get_height()), 2 )
		#print len(self.consoleBuffer)
		for i, line in enumerate(self.consoleBuffer):
			#print line, 'rendering at', (0, self.surface.get_height() - (i+2)*(self.textInput.font.get_height()) )
			self.consoleSurface.blit(self.textInput.font.render(line, self.world.video.smoothText, self.textInput.textColor), (self.textXOffset, self.consoleSurface.get_height() - (len(self.consoleBuffer)-i+1)*(self.textInput.font.get_height()) ))
		return self.consoleSurface
	
	def show(self):
		self.set_dimensions()
		if self.bg == None:
			self.surface.fill( (0xff, 0xff, 0xff) )
		else:
			self.surface.blit(transform.scale(self.bg, (self.surface.get_width(), self.surface.get_height() ) ), (0, 0) )	
		self.surface.blit( self.get_console_surface(), (0, 0) )
		self.world.video.screen.blit(self.surface, (self.world.video.interface.left, self.world.video.interface.top) )	
		
	def console(self, string):
		#self.consoleBuffer.append(string)
		if self.consoleHeight > self.surface.get_height():
				del self.consoleBuffer[0]
		args = string.split(' ')
		if args[0]=='/quit':
			self.quit()
		elif args[0]=='/say':
			self.bus.send("clientchatmessage=" +string[5:])	
		elif args[0]=='/setusername':
			self.username = args[1]
		elif args[0]=='/setserver':
			self.bus.host = args[1]
			self.bus.toPort = args[2]
		elif args[0]=='/login':
			print args[1]
			self.bus.send('login=' + args[1])
		elif args[0][0]=='/':
			pass	
		else:
			#self.consoleBuffer.append(string)
			self.bus.send("clientchatmessage=" +string)				
			
	def console_print(self, string):
		self.consoleBuffer.append(string)
		if len(self.consoleBuffer)>self.consoleRows:
				del self.consoleBuffer[0]			
	
	def handle_objects(self):
		tick = self.ticker.tick()
		#print tick
		if tick > 100:
			self.bus.send('unit=player\t' + 'location=' + str(self.world.currentGrid) + ',' + str(self.world.player.rect.left) + ',' +  str(self.world.player.rect.top) + '\t' + 'velocity=' + str(self.world.player.velocity[0]) + ',' + str(self.world.player.velocity[1]) ) 
	
	def handle_input(self, commands):		
		data = self.bus.data
		for string in data:
			print string
			message = ''
			username = '<SYSTEM>'
			for n in parse_string(string):
				property = n[0]
				value = n[1]
				print type(property), property, type(value)
				
				if property == ('chatmessage'):
					message = value
				elif property == ('username'):
					username = value
			if message:
				self.console_print(username + ': ' + message)
		for command in commands:
			if command.type==QUIT:
				self.quit()		
		if self.textToggle:
			if self.textInput.handle_input(commands):
				self.console(self.textInput.get_string())
			return False
		else:
			for command in commands:
				if command.type==KEYDOWN:
					if command.key==K_RETURN:
						self.textToggle=True
					elif command.key==K_f:
						display.toggle_fullscreen()
					elif command.key==K_ESCAPE:
						self.quit()
			return True			
						
	def quit(self):
		self.bus.send('logoff=1')
		self.world.exit()					

def main():
	
	return 0

if __name__ == '__main__': main()
