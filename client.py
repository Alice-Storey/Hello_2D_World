#!/usr/bin/env python
#
#       world.py
#       
#       Alice
from pygame import*
from interface import*
import random, math, sys, pickle

def get_unit_vector_to(src, loc):
		dy=loc.center[1]-src.center[1]
		dx=loc.center[0]-src.center[0]
		
		if dx==0:
			return [0, dy/math.fabs(dy)]
		elif dy==0:
			return [dx/math.fabs(dx),0]	
		elif dx<dy:
			return [dx/math.fabs(dx), dy/math.fabs(dx)]
		elif dx>dy:
			return [dx/math.fabs(dy), dy/math.fabs(dy)]
		else:	
			return [1,1]	
			
def copy_rect(rect):
	return Rect(rect.left, rect.top, rect.width, rect.height)			

class Gameobject(sprite.Sprite):
	__slots__ = ('_rect', '_name', '_direction', '_image', '_speed', '_velocity', '_remainderPixels', '_filename')
	_images = {}
	def _GetRect(self):
		return self._rect
	def _SetRect(self, n):
		if n.__class__ == Rect:
			self._rect = Rect(n.left, n.top, self.image.get_width(), self.image.get_height() )
		else:
			self._rect = Rect(n[0], n[1], self.image.get_width(), self.image.get_height() )	
	rect = property(fget = _GetRect, fset = _SetRect)
	
	def _GetName(self):
		return self._name
	def _SetName(self, n):
		self._name = n
	name = property(fget = _GetName, fset = _SetName)
	
	def _GetDirection(self):
		return self._direction
	def _SetDirection(self, n):
		while n <0:
			n += 360
		while n >= 360:
			n -= 360
		self._direction = n		
	direction = property(fget = _GetDirection, fset = _SetDirection)
	
	def _GetImage(self):
		return transform.rotate(self._image, self.direction)
	def _SetImage(self, n):
		try:
			Gameobject._images.setdefault(n, image.load(n).convert_alpha())
			self._image = Gameobject._images[n]
			self._filename = n
		except error:
			print 'Unable to load image \'' + n + '\'.'	
	image = property(fget = _GetImage, fset = _SetImage)	
	
	def _GetSpeed(self):
		return self._speed
	def _SetSpeed(self, n):
		self._speed = n
	speed = property(fget = _GetSpeed, fset = _SetSpeed)
	
	def _GetGrid(self):
		return self._grid
	def _SetGrid(self, grid):
		self._grid = grid
	grid = property(fget = _GetGrid, fset = _SetGrid)
	
	def _GetVelocity(self):
		return self._velocity
	velocity = property(fget = _GetVelocity)
	
	def _GetRemainderPixels(self):
		return self._remainderPixels
	remainderPixels = property(fget = _GetRemainderPixels)
	
	def _GetFilename(self):
		return self._filename
	filename = property(fget = _GetFilename)
	
	def __init__(self, name, filename, (x, y) ):
		sprite.Sprite.__init__(self)
		self.name = name
		self.direction=0
		self.image = filename
		self.rect = (x, y)
		self.speed = 300
		self._velocity = [0, 0]
		self._remainderPixels = 0.0

class Unit(Gameobject):
	
	def min_vector(cls, (x, y)):
		if (x, y) == (0, 0):
			return (0, 0)
		elif x == 0:
			if y < 0:
				return (0, -1)
			else:
				return (0, 1)
		elif y == 0:
			if x > 0:
				return (1, 0)
			else:
				return (-1, 0)
		elif x > y:
			out =  [x/y, 1]
		else:
			out = [1, y/x]
		v = (x, y)
		for n in range(2):
			if (v[n]<0 and out[n]>0) or (v[n]>0 and out[n]<0):
				out[n] *= -1
		return out
	min_vector = classmethod(min_vector)	
			
	def __init__(self, name, filename, (x, y) ):
		Gameobject.__init__(self, name, filename, (x, y))
		
	def move_to(self,loc):
		pass	
		
	def load_image(self, filename):
		try:
			self.image = self.imageFile= image.load(filename).convert_alpha()
			self.rect.width = self.image.get_width()
			self.rect.height = self.image.get_height()
			if self.rect.width == self.rect.height:
				self.radius = self.image.get_width
			else:
				self.radius = None
		except error:
			pass	
	
	def update(self, commands):
		pass
		
	def turn(self, degree):
		self.direction += degree
		if self.direction%90 == 0:
			self.image = transform.rotate(self.imageFile, self.direction)
		else:	
			image = transform.rotate(self.image, self.degree)
			
	def turn_to_(self, degree):
		while degree <0:
			degree += 360
		while degree >= 360:
			degree -= 360	
		if degree != self.direction:
			self.direction = int(degree)
			self.image = transform.rotate(self.imageFile, self.direction)
			#self.rect = Rect(self.rect.left - (self.image.get_width()-self.rect.width)/2, self.rect.top - (self.image.get_height()-self.rect.height)/2, self.image.get_width(), self.image.get_height() )
			
	def turn_to_coord(self, x, y):
		y *= -1
		if x==0:
			if y > 0:
				deg = 90
			else:
				deg = 270
		else:
			deg = math.atan(1.0*y/x)
			if x <0:
				deg += math.pi
		deg = math.degrees(deg)
		deg -= 90
		while deg <0:
			deg += 360
		while deg >= 360:
			deg -= 360
		self.turnTo(deg)	
	
	def move_(self):
		v = (self.velocity[0], self.velocity[1])
		loc = self.rect.move(v)
		loc = Rect(loc.left, loc.top, 5, 5)
		if self.grid.is_on_grid(loc) and self.velocity != [0, 0]:
			#i = self.grid.getIndex(self,self.grid.units)
			thisloc = self.rect
			#obstacleIndex=loc.collidelistall(self.grid.locs)
			obstacles = sprite.spritecollide(self, self.grid.sprites, False)
			if len(obstacles) > 0:
				backtrack = get_unit_vector_to(loc, thisloc)
				thisloc = copy_rect(loc)	
				while thisloc.colliderect(obstacles[0].rect):
						thisloc = thisloc.move(backtrack)
			else:
				thisloc = copy_rect(loc)
			
			self.rect = thisloc
			
	def move(self):
		#if self.velocity != [0,0]:
		#	if self.velocity[0] != 0:
		#		direction = math.degrees(math.atan(self.velocity[1]/self.velocity[0]))
		#	else:
		#		if self.velocity[1] > 0:
		#			direction = 90
		#		else:
		#			direction = 270
		#	
		#	if self.velocity[0] < 0:
		#		direction += 90
		x = self.velocity[0]
		y = self.velocity[1]
					
		
		ppf = 1.0*self.speed/self.world.video.fps	
		self._remainderPixels += ppf - math.floor(ppf)
		if self.remainderPixels > 1:
			ppf += math.floor(self.remainderPixels)
			self.remainderPixels -= math.floor(self.remainderPixels)
		ppf = int(math.floor(ppf))	
		
		here = self.rect.__copy__()
		self.rect = self.rect.move(ppf*self.velocity[0], ppf*self.velocity[1])
		if (not self.grid.get_rect().contains(self.rect)) or len(sprite.spritecollide(self, self.grid.units, False, sprite.collide_circle))>0 or len(sprite.spritecollide(self, self.grid.statics, False, sprite.collide_circle))>0:
			self.rect = self.rect.move(-1*ppf*self.velocity[0], -1*ppf*self.velocity[1])
			self.rect = here
			movement = Unit.min_vector(self.velocity)
			self._velocity = (0, 0)
			while not ((not self.grid.get_rect().contains(self.rect) ) or len(sprite.spritecollide(self, self.grid.statics, False, sprite.collide_circle))>0 or len(sprite.spritecollide(self, self.grid.units, False, sprite.collide_circle))>0):
				self.rect = self.rect.move(movement)
			back = (movement[0]*-1, movement[1]*-1)
			self.rect = self.rect.move(back)		
			
			
class Mover(Unit):
	def update(self, commands):
		self.move()
		
	def center_view(self):
		newView = Rect(self.rect.left - (self.world.video.view.width - self.rect.width)/2, self.rect.top - (self.world.video.view.height - self.rect.height)/2, self.world.video.view.width, self.world.video.view.height)
		if newView.left >= 0 and newView.right <= self.grid.get_rect().right:
			self.world.video.view = self.world.video.view.move(newView.left-self.world.video.view.left, 0)
		if newView.top >= 0 and newView.bottom <= self.grid.get_rect().bottom:
			self.world.video.view = self.world.video.view.move(0, newView.top-self.world.video.view.top)
	
	def handle_input(self, commands):
		#if command.type == KEYDOWN:
		vel = [0, 0]
		if key.get_pressed()[K_DOWN]:
			self.destination = None
			vel[1] += 1
		if key.get_pressed()[K_UP]:
			self.destination = None
			vel[1] -= 1
		if key.get_pressed()[K_LEFT]:
			self.destination = None
			vel[0] -= 1
		if key.get_pressed()[K_RIGHT]:
			self.destination = None
			vel[0] += 1
		if key.get_pressed()[K_SPACE]:
			pass
		
		self._velocity = vel
		
		if vel != [0,0]:
				x = vel[0]
				y = vel[1]
				deg = 0
				if x == 0:
					if y < 0:
						deg = 0
					else:
						deg = 180
				elif y == 0:
					if x > 0:
						deg = 270
					else:
						deg = 90
				elif x > 0:
					if y < 0:
						deg = 315
					else:
						deg = 225
				else:
					if y < 0:
						deg = 45
					else:
						deg = 135
				
				self.direction = deg		
			
class Static(Gameobject):
	def __init__(self, type, filename, (x, y), direction = 180 ): 
		sprite.Sprite.__init__(self)
		self.direction = direction
		self.image = None
		self.imageFile = None
		self.filename = filename
		self.type = type
		self.rect = Rect(x, y, 1, 1)
		try:
			self.load_image(filename)
			self.Rect = Rect(x, y, self.image.get_width(), self.image.get_height())
		except error:
			print 'Could not load image for Static of type', self.type
		
	def turn_to(self, degree):
		while degree <0:
			degree += 360
		while degree >= 360:
			degree -= 360	
		self.direction = int(degree)
		self.image = transform.rotate(self.imageFile, self.direction)
		
	def load_image(self, filename):
		try:
			self.image = self.imageFile= image.load(filename).convert_alpha()
			self.rect.width = self.image.get_width()
			self.rect.height = self.image.get_height()
			if self.rect.width == self.rect.height():
				self.radius = self.image.get_width
			else:
				self.radius = None	
		except error:
			pass					

class Grid:
	def __init__(self, w, h, filename=''):
		self.w = w
		self.h = h
		self.units = sprite.Group()
		self.statics = sprite.Group()
		self.sprites = sprite.Group()
		self.image = Surface( (w, h) )
		self.bg = Surface( (w, h) )
		self.filename = filename
		if filename== '':
			self.set_bgcolor( (0xff, 0xff, 0xff) )
			self.filename = '_fill_0,0,0'
		else:
			self.set_bg(filename)
		self.type= ''
		self.world = None
		self.player = sprite.GroupSingle()
	
	def set_bg(self, filename):
		string = filename.split('_')
		if string[1]=='fill':
			color = string[2].split(',')
			color = (int(color[0]), int(color[1]), int(color[2]))
			self.set_bgcolor( color )
		elif string[1]=='image':
			self.set_bgimage(string[2])
		elif string[1]=='tile':
			self.set_bgtile(string[2])		
		
		
	def get(self, loc):
		for e in self.sprites:
			if e.rect.collidepoint(loc):
				return e
		return None
	
					
	def add(self, e):
		loc = (e.rect.width, e.rect.height) 
		if self.get(loc)==None and self.is_on_grid(loc):
			e.grid = self
			e.world = self.world
			if e.__class__ == Unit:
				print 'added Unit'
				self.units.add(e)
				self.sprites.add(e)
			elif e.__class__ == Static:	
				print 'added Static'
				self.statics.add(e)
				self.sprites.add(e)
			elif e.__class__ == Mover:
				print 'added Mover'
				self.player.add(e)
				self.sprites.add(e)
			
	def remove(self, e):
		self.sprites.remove(e)
		self.statics.remove(e)
		self.units.remove(e)
		
	def remove_loc(self, loc):
		try:
			self.remove(self.get(loc))
		except error:
			print 'Error in Grid.remove_loc()'			
			
	def is_on_grid(self, rectORpoint):
		if rectORpoint.__class__ == Rect:
			return self.get_rect().contains(rectORpoint)
		else:	
			return self.get_rect().collidepoint(rectORpoint)		
		
	def show(self):
		self.image.blit(self.bg, (0, 0) )
		self.sprites.draw(self.image)
		self.world.video.screen.blit(self.image, (0,0), self.world.video.view )	
			
	def update(self, commands, flag=True):
		self.player.update(commands)
		self.units.update(commands)
		if flag and len(self.player.sprites() ) > 0:
			self.player.sprite.handle_input(commands)
			self.player.sprite.center_view()
			
	def setColor(self, (r, g, b)):
		self.color = (r,g,b)
		
	def getRandomLoc(self):
		return Loc(random.randint(0, self.w-1), random.randint(0,self.h-1))
		
	def getAllLocs(self):
		out = []
		for x in range(self.w):
			for y in range(self.h):
				out.append(Loc(x,y))
		return out		
		
	def get_rect(self):
		return Rect(0,0,self.w,self.h)	
		
	def set_bgcolor(self, (r, g, b) ):
		self.bg.fill((r, g, b))
		self.filename = '_fill_'+str(r)+','+str(g)+','+str(b)
		
	def set_bgimage(self, filename, scale=False):
		try:
			self.bg = image.load(filename).convert_alpha()
			if scale:
				print 'scaling grid bg'
				self.bg = transform.scale(self.bg, (self.w, self.h) )
			self.filename = '_image_' + filename	
		except error:
			pass		
			
	def set_bgtile(self, filename):
		try:
			tile = image.load(filename).convert_alpha()
			self.filename = '_tile_' + filename
		except error:
			return
		for x in range(int(math.ceil(self.w*1.0/tile.get_width()))):
			for y in range(int(math.ceil(self.h*1.0/tile.get_height()))):
				self.bg.blit(tile, (x*tile.get_width(), y*tile.get_height()))								

class Video():
	def __init__(self, (resx, resy), fps):
		self.resolution = None
		self.view = None
		self.set_resolution( (resx, resy) )
		self.fps = fps
		self.screen = display.set_mode( (resx, resy) )
		self.smoothText = False
		self.interface = None
	
	def set_resolution ( self, (x, y) ):
		self.resolution = (x, y)
		self.view = Rect(0,0,x,y-(x/6))
		self.interface = Rect(0, y-(x/6), x, x/6)
		self.screen = display.set_mode( (x, y) )
		
	def set_fps (self, fps):
		if int(fps) > 0:
			self.fps = int(fps)	
		
class World():
	
	def getPlayer(self):
		return self.grids[self.currentGrid].player.sprite
	player = property(fget = getPlayer)	
	
	def exit(self):
		self.quit = True
		
	def take_admin_command(cls, string):
		pass
	take_admin_command = classmethod(take_admin_command)	
	
	def __init__(self, datafilename, prefsfilename, caption='The World'):
		init()
		display.set_caption(caption)
		self.grids = []
		self.loaded=False
		self.currentGrid = 0
		self.video = Video( (640, 480), 60)
		self.preferences_load(prefsfilename)
		if datafilename != '':
			self.data_load(datafilename)
		self.ticker = time.Clock()
		self.interface = Interface(self)
		self.quit = False
		
	def preferences_load(self, filename='preferences'):
		try:
			f = open(filename, 'rb')
			set = pickle.load(f)
			self.video.set_resolution ( set[0] )
			self.video.fps = int( set[1] )
			f.close()		
		except (IOError, EOFError, ValueError):
			print 'Could not load \'' + filename + '\'. Saving default preferences to same filename.'
			self.preferences_save(filename)	
	
	def preferences_save(self, filename='preferences'):
		f = open(filename, 'wb')
		pickle.dump( (self.video.resolution, self.video.fps), f)
		f.close()
		
	def data_load(self, filename):
		pass
		#try:
		#	f = open(filename, 'rb')
		#	exit = False
		#	g = -1
		#	while not exit:
		#		try:
		#			set = pickle.load(f)
		#			if len(set) == 2:
		#				self.put(Grid(set[0][0], set[0][1], set[1]))
		#				g += 1
		#			elif len(set) == 4:
		#				if set[0]=='Mover':
		#					self.grids[g].put( Mover(set[0],set[1]), Loc(set[2], set[3]) )	
		#				elif set[0]=='Ball':
		#					self.grids[g].put( Unit(set[0],set[1]), Loc(set[2], set[3]) )
		#		except EOFError:
		#			exit = True		
		#	f.close()
		#	loaded = True
		#except IOError:
		#	print 'Missing or corrupt data file.'
		
	def data_save(self, filename):
		pass
	#	f = open(filename, 'w')
	#	for grid in self.grids:
	#		pickle.dump( ((grid.w, grid.h), grid.filename), f )
	#		for e in grid.units:
	#			loc = e.getLoc()
	#			pickle.dump( (e.type, e.filename, loc.x, loc.y), f )
	#	f.close()	
	
	def get_now_grid(self):
		return self.grids[self.currentGrid]	
		
	def show(self):
		tick = self.ticker.tick()
		self.grids[self.currentGrid].show()	
		self.interface.show()
		display.update()	
		time.wait(1000/self.video.fps - tick)
		self.ticker.tick()	
		
	def add(self, grid):
		self.grids.append(grid)
		grid.world = self	
		
	def update(self, commands, flag=True):
		self.grids[self.currentGrid].update(commands, flag)	
	
	def handle_input(self, commands):
		return self.interface.handle_input(commands)			
		#return quit						
		
		
	def run(self):
		while not self.quit:
			event.pump()
			commands = event.get()
			self.interface.handle_objects()
			flag = self.handle_input(commands)
			self.update(commands, flag)		
			self.show()

def main():
	
	w = World('','data/prefsdat')
	w.add (Grid(1000,1000))
	w.get_now_grid().set_bgimage('data/bg.png', True)
	w.get_now_grid().add(Mover('Mover', 'data/arrow.png', (100, 100)) )
	w.get_now_grid().add(Unit('Ball', 'data/ball.png', (300, 300)) )
	
	#w.get_now_grid().put(Unit('Ball','data/ball.png'), Loc(400,400))
	try:
		w.video.set_resolution( ( int(sys.argv[1]), int(sys.argv[2]) ) )
	except (IndexError, ValueError):
		pass
	
	try:
		w.video.set_fps( int(sys.argv[3]) )
	except (IndexError, ValueError):
		pass
	#print w.video.resolution
	w.interface.set_bg('data/interfacebg.png')
	
	w.run()
	
	#w.data_save('data/objectdata')
		
	return 0

if __name__ == '__main__': main()
