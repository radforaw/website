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
#import dik

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




def circle(sides, size, centre=(0, 0)):
	midres = [[
		centre[0] + math.cos(((math.pi / 180) * (float(360) / sides)) * n) * size,
		centre[1] + math.sin(((math.pi / 180) * (float(360) / sides)) * n) * size
	] for n in range(sides)]
	midres.append(midres[0])
	return midres



	
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


def FindLineCircleIntersections(p,point1, point2):
	cx,cy,radius= p
	dx = point2[0] - point1[0]
	dy = point2[1] - point1[1]

	A = dx * dx + dy * dy
	B = 2 * (dx * (point1[0] - cx) + dy * (point1[1] - cy))
	C = (point1[0] - cx) * (point1[0] - cx) + (point1[1] - cy) * (
		point1[1] - cy) - radius * radius

	det = B * B - 4 * A * C
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

def setupshortest(plt, ln, plt1, ln1, t, b, a, origang):
	#plt,ln= shortest.getloc(t,b,a,origang)
	n1 = b[ln[0]]  #gets point of start of line
	n2 = b[ln[1]]  #gets point of end of line
	if [True for tmp in a if tmp[0] == ln[1] and tmp[1] == ln[0]]:
		ns = [[-1, ln[0], distance(n2, plt)/4]]
	else:
		ns = [[-1, ln[1], distance(n1, plt)/4]]
	n1 = b[ln1[0]]
	n2 = b[ln1[1]]
	if [True for tmp in a if tmp[0] == ln1[1] and tmp[1] == ln1[0]]:
		ns += [[ln1[1], -2, distance(n2, plt1)/4]]
	else:
		ns += [[ln1[0], -2, distance(n1, plt1)/4]]
	try:
		temp = list(Flatten(Dijkstra(a + ns, -1,-2)))
		dist = temp[0]
		temp = temp[2:-1]
	except:
		return 100000, 0
	temp = [list(plt1)] + [b[nn] for nn in temp] + [list(plt)]
	return dist, temp

