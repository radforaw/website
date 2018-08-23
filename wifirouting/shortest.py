import math
import requests
try:
	from lxml import etree as ET
except ImportError:
	import xml.etree.cElementTree as ET
from PIL import Image, ImageDraw
import time
import cPickle as pickle
import heapq
from collections import defaultdict
import geometry
from PIL import Image
from cStringIO import StringIO
import csv
from requests.exceptions import ConnectionError
from math import atan2, pi

ZM = 13


def weightget(mode):
	d = {}
	with open("zweights.csv", "r") as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			d[row['key'], row['value']] = row[mode]
	return d


def OsmRouteImport(imported):
	'''
	str imported : content of osm overpass query
	returns route tree of ways ready for Dijkstra algorithm
	and dictionary of all osm nodes on ways
	'''
	print imported[:1000]
	root = ET.fromstring(imported)
	wt = weightget("car")
	waydict = {}
	nodes = {}
	simpledict={}
	ctr=1
	for m in root.findall('node'):
		x, y = geometry.deg2num(
			float(m.attrib['lat']), float(m.attrib['lon']), zoom=ZM)
		simpledict[int(m.attrib['id'])]=ctr
		nodes[ctr]= [x, y]
		ctr+=1
		#print m.attrib
		if 'k' in m.attrib:
			if m.attrib['k'] == "barrier":
				pass
		#do the translation here
	for n in root.findall('way'):
		oneway = False
		weight = 1
		for ow in n.findall('tag'):
			if ow.attrib['k'] == 'oneway' and ow.attrib['v'] == 'yes':
				oneway = True
			if ow.attrib['k'] == 'junction' and ow.attrib['v'] == 'roundabout':
				oneway = True
			#weights go here
			for wts in wt:
				if ow.attrib['k'] == wts[0] and ow.attrib['v'] == wts[1]:
					weight *= float(wt[wts])
		if weight < 0:
			continue
		prev = None
		for l in n.findall('nd'):

			current = simpledict[int(l.attrib['ref'])]
			if current not in waydict:
				waydict[current] = {}
			if prev:
				waydict[prev][current] = weight * distance(nodes[prev], nodes[current])
				if not oneway:
					waydict[current][prev] = weight * distance(nodes[current], nodes[prev])
			prev = current
	#convert to format for dikstra function	
	n = []
	for a in waydict:
		for b in waydict[a]:
			n.append([int(a), int(b), int(waydict[a][b]*100000)])
	print max(a[0] for a in n)
	print max(a[2] for a in n)
	return n, nodes


def distance(a, b):
	return math.sqrt(((a[0] - b[0])**2) + ((a[1] - b[1])**2))


def pointlinedistance(line, point):
	x1 = line[0][0]
	y1 = line[0][1]
	x2 = line[1][0]
	y2 = line[1][1]
	x3 = point[0]
	y3 = point[1]
	u = (((x3 - x1) * (x2 - x1)) + ((y3 - y1) * (y2 - y1))) / (((x2 - x1)**2) + (
		(y2 - y1)**2))
	if u < 0.0001 or u > 1:
		if ((x3 - x1)**2) + ((y3 - y1)**2) < ((x3 - x1)**2) + ((y3 - y1)**2):
			ix = x1
			iy = y1
		else:
			ix = x2
			iy = y2
	else:
		ix = x1 + u * (x2 - x1)
		iy = y1 + u * (y2 - y1)
	d = ((ix - x3)**2) + ((iy - y3)**2)
	return (ix, iy), d


def angle(a, b):
	x = a[0] - b[0]
	y = a[1] - b[1]
	r = atan2(y, x) * (180 / pi)
	return r % 360


def Dijkstra(edges, f, t):
	#returns shortest path
	g = defaultdict(list)
	for l, r, c in edges:
		g[l].append((c, r))
	q, seen = [(0, f, ())], set()
	while q:
		(cost, v1, path) = heapq.heappop(q)
		if v1 not in seen:
			seen.add(v1)
			path = (v1, path)
			if v1 == t: return (cost, path)
			for c, v2 in g.get(v1, ()):
				if v2 not in seen:
					heapq.heappush(q, (cost + c, v2, path))
	return (-1, -1)


def Flatten(L):
	while len(L) > 0:
		yield L[0]
		L = L[1]


def findclosest(nodes, x, y):
	#finds closest nodes to location (x,y=lat,lon)
	closest = None
	offset = float(1000000)
	for n in nodes:
		dist = distance((nodes[n][0], nodes[n][1]), (x, y))
		if dist < offset:
			offset = dist
			closest = n
	return offset, closest


def findminmax(nodes):
	print len(nodes)
	a = min([nodes[x][0] for x in nodes])
	b = max([nodes[x][0] for x in nodes])
	c = min([nodes[x][1] for x in nodes])
	d = max([nodes[x][1] for x in nodes])
	e = min([b - a, d - c])
	return a, b, c, d, e


def getloc(pos, nodes, lines, origang):
	nearest = 100000
	nearpoint = (0, 0)
	ln = -1
	ang = 0
	t = (0, 0)
	for n in lines:
		a, b = pointlinedistance((nodes[n[0]], nodes[n[1]]), pos)
		if b < nearest:
			'''ang=angle(nodes[n[0]],nodes[n[1]])
			j=180 - abs(abs(ang - origang) - 180)
			if j<45:'''
			#t=(ang,j)
			nearest = b
			nearpoint = a
			ln = n
	#print origang,tt
	return nearpoint, tuple(ln)


def circle(sides, size, centre=(0, 0)):
	midres = [[
		centre[0] + math.cos(((math.pi / 180) * (float(360) / sides)) * n) * size,
		centre[1] + math.sin(((math.pi / 180) * (float(360) / sides)) * n) * size
	] for n in range(sides)]
	midres.append(midres[0])
	return midres


def getloc2(pos, nodes, lines, origang):
	n = [getloc(x, nodes, lines, origang) for x in circle(2, .0026, centre=pos)]
	return list(set(n))


def getlocs(pos, nodes, lines, origang):
	#{'nearest':100000,'nearpoint':(0,0),'ln':-1}
	c = circle(20, .01, centre=pos)
	#print c
	d = []
	for x in range(len(c)):
		d.append({'nearest': 100000, 'nearpoint': (0, 0), 'ln': -1})
	for n in lines:
		for x in range(len(c)):
			a, b = pointlinedistance((nodes[n[0]], nodes[n[1]]), c[x])
			if b < d[x]['nearest']:
				d[x]['nearest'] = b
				d[x]['nearpoint'] = a
				d[x]['ln'] = n

	j = [(x['nearpoint'], tuple(x['ln'])) for x in d]
	return list(set(j))  #need to remove 'ln' duplicates...
	
def getlocsa(pos, nodes, lines, origang):
	j=[]
	for n in lines:
		p=list(pos)+[0.015]
		lsp=nodes[n[0]]
		esp=nodes[n[1]]
		t=FindLineCircleIntersections(p,lsp,esp)
		if t:
			for a in t:
				j.append([a,n])
	print len(j)
	return j
	
def offset(a,b,off=0.1):
	x1,y1=a
	x2,y2=b
	ang=math.atan2(a,b)-(math.pi/2)
	lx,ly=math.sin(ang)*off,math.cos(ang)*off
	return (x1+lx,y1+ly),(x2+lx,y2+ly)

def LineIntersectCircle(p, lsp, lep):
	# p is the circle parameter, lsp and lep is the two end of the line
	x0, y0, r0 = p
	x1, y1 = lsp
	x2, y2 = lep
	if x1 == x2:
		if abs(r0) >= abs(x1 - x0):
			p1 = x1, y0 - math.sqrt(r0**2 - (x1 - x0)**2)
			p2 = x1, y0 + math.sqrt(r0**2 - (x1 - x0)**2)
			inp = [p1, p2]
			# select the points lie on the line segment
			inp = [p for p in inp if p[1] >= min(y1, y2) and p[1] <= max(y1, y2)]
		else:
			inp = []
	else:
		k = (y1 - y2) / (x1 - x2)
		b0 = y1 - k * x1
		a = k**2 + 1
		b = 2 * k * (b0 - y0) - 2 * x0
		c = (b0 - y0)**2 + x0**2 - r0**2
		delta = b**2 - 4 * a * c
		if delta >= 0:
			p1x = (-b - math.sqrt(delta)) / (2 * a)
			p2x = (-b + math.sqrt(delta)) / (2 * a)
			p1y = k * x1 + b0
			p2y = k * x2 + b0
			inp = [[p1x, p1y], [p2x, p2y]]
			# select the points lie on the line segment
			inp = [p for p in inp if p[0] >= min(x1, x2) and p[0] <= max(x1, x2)]
		else:
			inp = []
	return inp

def FindLineCircleIntersections(p,point1, point2):
	cx,cy,radius= p
	dx = point2[0] - point1[0]
	dy = point2[1] - point1[1]
	'''if distance(point1,(cx,cy))<radius and distance(point2,(cx,cy))<radius:
		return []'''
	A = dx * dx + dy * dy
	B = 2 * (dx * (point1[0] - cx) + dy * (point1[1] - cy))
	C = (point1[0] - cx) * (point1[0] - cx) + (point1[1] - cy) * (
		point1[1] - cy) - radius * radius

	det = B * B - 4 * A * C
	'''if (A <= 0.0000001) or (det < 0):
		return []
	elif det == 0:
		t = -B / (2 * A)
		intersection1 = (point1[0] + t * dx, point1[1] + t * dy)
		if min([point1[0],point2[0]])<intersection1[0]<max([point1[0],point2[0]]) and min([point1[1],point2[1]])<intersection1[1]<max([point1[1],point2[1]]):
			return []
		return [intersection1]
	else:'''
	try:
		n=[]
		t = (-B + math.sqrt(det)) / (2 * A)
		intersection1 = (point1[0] + t * dx, point1[1] + t * dy)
		t = (-B - math.sqrt(det)) / (2 * A)
		intersection2 = (point1[0] + t * dx, point1[1] + t * dy)
		if min([point1[0],point2[0]])<intersection1[0]<max([point1[0],point2[0]]) and min([point1[1],point2[1]])<intersection1[1]<max([point1[1],point2[1]]):
			n.append(intersection1)
		if min([point1[0],point2[0]])<intersection2[0]<max([point1[0],point2[0]]) and min([point1[1],point2[1]])<intersection2[1]<max([point1[1],point2[1]]):
			n.append(intersection2)
	except:
		pass
	return n

class osmmap():
	def __init__(self, zoom=13, baseurl="https://tile.openstreetmap.org/"):

		self.zoom = zoom
		self.baseurl = baseurl
		try:
			with open("tilecache.pickle", "r") as picfile:
				self.cache = pickle.load(picfile)
		except:
			self.cache = {}

	def getmetiles(self, a, b):
		try:
			return self.cache[a, b]
		except:
			url = self.baseurl + str(self.zoom) + "/" + str(a) + "/" + str(b) + ".png"
			response = requests.get(url)
			tmp = Image.open(StringIO(response.content)).convert('RGB')
			self.cache[a, b] = tmp.load()
			return self.cache[a, b]

	def deg2num(self, lat_deg, lon_deg):
		lat_rad = math.radians(lat_deg)
		n = 2.0**self.zoom
		xtile = ((lon_deg + 180.0) / 360.0 * n)
		ytile = (
			(1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) /
			2.0 * n)
		xrem = int((xtile % 1) * 256)
		yrem = int((ytile % 1) * 256)
		xtile = int(xtile)
		ytile = int(ytile)
		return (xtile, ytile), (xrem, yrem)

	def locationcolour(self, (xtile, ytile), (xrem, yrem)):
		img = self.getmetiles(xtile, ytile)
		return img[xrem, yrem]

	def tilesave(self):
		with open("tilecache.pickle", "w") as picfile:
			pickle.dump(self.cache, picfile)


'''
if __name__=='__main__':
	import pygame,sys
	with open('sampledata.pickle') as file:
		osm=pickle.load(file)
		a,b=OsmRouteImport(osm) #a-links,b-nodes
		minx,maxx,miny,maxy,ratio=findminmax(b)
		print a[0]
		for n in b:
			print n,b[n]
			break
	pygame.init()
	size = width, height = 1024,768
	screen = pygame.display.set_mode(size)
	screen.fill((255,255,255))
	clock=pygame.time.Clock()
	for n in a: #draws the screen
		start=(int(((b[n[0]][0]-minx)/(ratio))*width),int(((b[n[0]][1]-miny)/(ratio))*height))
		end=(int(((b[n[1]][0]-minx)/(ratio))*width),int(((b[n[1]][1]-miny)/(ratio))*height))
		pygame.draw.line(screen, (0,0,0), start, end, 1)
	try: #draws the image on top
		c=osmmap(zoom=ZM,baseurl="http://192.168.1.113/hot/")
		pxarray=pygame.PixelArray(screen)
		for x in range(width):
			for y in range(height):
				tx=(((x/float(width))*(ratio))+minx)
				ty=(((y/float(height))*(ratio))+miny)
				pxarray[x,y]=c.locationcolour((int(tx),int(ty)),(int((tx%1)*256),int((ty%1)*256)))
			pygame.display.flip()
		del pxarray
	except ConnectionError as e:
		pass
	#c.tilesave()
	end=False
	while 1:
		for event in pygame.event.get():
			if event.type == pygame.QUIT: sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				if pygame.mouse.get_pressed()[0]==True:
					pos=pygame.mouse.get_pos()
					print pos
					plt,ln=getloc(((((pos[0]/float(width))*(ratio))+minx),(((pos[1]/float(height))*(ratio))+miny)),b,a)
					pltloc=(int(((plt[0]-minx)/(ratio))*width),int(((plt[1]-miny)/(ratio))*height))
					pygame.draw.circle(screen,(255,0,0),pltloc,4)
					if not end:
						n1=b[ln[0]]
						n2=b[ln[1]]
						d1=distance(n1,plt)
						d2=distance(n2,plt)
						ns=[['start',ln[1],d2]]
						o=plt
						t=False
						for tmp in a:
							if tmp[0]==ln[1] and tmp[1] ==ln[0]:
								t=True
						if t:
							ns+=[['start',ln[0],d1]]
						end=True
					else:
						n1=b[ln[0]]
						n2=b[ln[1]]
						d1=distance(n1,plt)
						d2=distance(n2,plt)
						ns+=[[ln[1],'end',d2]]
						# 'start',n2
						t=False
						for tmp in a:
							if tmp[0]==ln[1] and tmp[1] ==ln[0]:
								t=True
						if t:
							ns+=[[ln[0],'end',d1]]
						temp=list(Flatten(Dijkstra(a+ns,'start','end')))[2:-1]
						temp=[list(plt)]+[b[n] for n in temp]+[list(o)]
						pygame.draw.lines(screen,(255,0,0),False,[[int(((plt[0]-minx)/(ratio))*width),int(((plt[1]-miny)/(ratio))*height)] for plt in temp],4)
						end=False
				elif pygame.mouse.get_pressed()[2]==True:
					pos=pygame.mouse.get_pos()
					print pos
					plt,ln=getloc(((((pos[0]/float(width))*(ratio))+minx),(((pos[1]/float(height))*(ratio))+miny)),b,a)
					pltloc=(int(((plt[0]-minx)/(ratio))*width),int(((plt[1]-miny)/(ratio))*height))
					print pltloc
					pygame.draw.line(screen,(0,0,192),[pltloc[0]-8,pltloc[1]-8],[pltloc[0]+8,pltloc[1]+8],4)
					pygame.draw.line(screen,(0,0,192),[pltloc[0]+8,pltloc[1]-8],[pltloc[0]-8,pltloc[1]+8],4)
					a.remove(ln)
					for n in range(len(a)):
						if a[n][1]==ln[0] and a[n][0]==ln[1]:
							a.remove(a[n])
							break
		clock.tick(30)
		pygame.display.flip()


# lines [from,to,distance]
# node[no]=[x,y] 
'''

