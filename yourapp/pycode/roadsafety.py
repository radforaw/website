from PIL import Image, ImageDraw
import math
import io


def compcalc(n):
	#return coordinates for 
	ang = (((n - 1) * 45) + 270) % 360
	return [
		int(round(math.cos(math.radians(ang)))),
		int(round(math.sin(math.radians(ang))))
	]

def angcor(n,rev=False):
	return (((1-n) * 45)+(not(rev)*180)) % 360

def linecalc(vector, angle):
	x = vector[0] * sin(angle)
	y = vector[1] * cos(angle)
	return x, y


def calcalt(a, size=50):
	'''
	return a list of 2 time lists representing the coordinates of the shape with an arrowhead
	int a: the stats19 compass point
	int size: represents the size of the shape
	'''
	print a
	first = int(a / 10) #get first number
	fl=turtlecoords(direction=angcor(first,rev=False))
	n=fl.line(0,size)
	second = a % 10 #get second number
	sl=turtlecoords(direction=(angcor(second,rev=True)))
	n=[sl.line(*a) for a in arrow(size,5)]
	return fl.ret[1:]+sl.ret


def minmax(x, off=[0, 0]):
	minx = min([a[0] for a in x])
	miny = min([a[1] for a in x])
	maxx = max([a[0] for a in x])
	maxy = max([a[1] for a in x])
	ox = 0 - minx
	oy = 0 - miny
	return {
		'line': tuple([(a[0] + ox + off[0], a[1] + oy + off[1]) for a in x]),
		'limits': [maxx + ox + 1 + off[0], maxy + oy + 1 + off[1]],
		'centre': [ox + off[0], oy + off[1]]
	}


def minmaxobj(objs):
	x = []
	for n in objs:
		for y in n:
			x.append(y)
	print x
	minx = min([a[0] for a in x])
	miny = min([a[1] for a in x])
	maxx = max([a[0] for a in x])
	maxy = max([a[1] for a in x])
	ox = 0 - minx
	oy = 0 - miny
	ret = []
	for b in objs:
		ret.append(tuple([(a[0] + ox, a[1] + oy) for a in b]))
	return {'lines': ret, 'limits': [maxx + ox + 1, maxy + oy + 1]}


def wheredoesitgo(a, limitsa, limitsb):
	loc = ((a % 10) + 4)
	d = compcalc(loc)
	return [((d[0] < 0) * -limitsa[0]) + ((d[0] > 0) * limitsb[0]),
									((d[1] < 0) * -limitsa[1]) + ((d[1] > 0) * limitsb[1])]


def quickimage(z, p):
	a = calcalt(z)
	print 'this',z,a
	b = minmax(a)
	y = minmax(calcalt(p))
	pos2 = wheredoesitgo(p, y['limits'], b['limits'])
	y = minmax(y['line'], pos2)
	res = minmaxobj([b['line'], y['line']])
	return drawimage(res)
	
def drawimage(res):
	col = ['blue', 'red', 'green']
	c = 0
	x = Image.new('RGB', res['limits'], 'White')
	draw = ImageDraw.Draw(x)
	for b in res['lines']:
		draw.line(b, fill=col[c % 3])
		c += 1
	ret = io.BytesIO()
	x.save(ret, format='PNG')
	return ret

class turtlecoords():
	def __init__(self,x=0,y=0,direction=0):
		self.x,self.y=x,y
		self.direction=direction
		self.ret=[[int(self.x),int(self.y)]]
		
	def line(self,direction,distance):
		self.direction+=direction
		self.x-=math.sin(math.radians(self.direction))*distance
		self.y-=math.cos(math.radians(self.direction))*distance
		self.ret.append([int(self.x),int(self.y)])
		return (self.x,self.y)

def arrow(l,x):
	return [[0,l],[135,x],[135,(math.sqrt((x**2)*2))],[135,x]]


if __name__ == '__main__':
	'''
	test=arrow(50,5)
	x=turtlecoords(direction=angcor(5))
	d=[x.line(*a) for a in test]
	print x.ret
	print arrow(50,25)
	j= minmaxobj([x.ret])
	x=drawimage(j)
	Image.open(x).show()
	'''
	n = (12, 23, 34, 42, 57, 65, 78, 84, 84)
	m = (41, 42, 57, 65, 78, 84, 23, 12, 84)
	for d in range(len(n)):
		x = quickimage(n[d], m[d])
		Image.open(x).show()


'''
we want to send (direction,distance)
return a bunch of coordinates
todo -catch 00
'''
