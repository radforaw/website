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
from cStringIO import StringIO
import csv
from requests.exceptions import ConnectionError


ZM=13

class this():
	def __init__(self,imported,mode):
		self.imported=imported
		self.mode=mode
		self.graph,self.nodes=self.OsmRouteImport()
		self.minx,self.maxx,self.miny,self.maxy,self.ratio=self.findminmax()

	def weightget(self):
		d={}
		with open("zweights.csv","r") as csvfile:
			reader=csv.DictReader(csvfile)
			for row in reader:
				d[row['key'],row['value']]=row[self.mode]
		return d

	def OsmRouteImport(self):
		'''
		str imported : content of osm overpass query
		returns route tree of ways ready for Dijkstra algorithm
		and dictionary of all osm nodes on ways
		'''
		root = ET.fromstring(self.imported)
		wt=self.weightget()
		waydict={}
		nodes={}
		for m in root.findall('node'):
			x,y=geometry.deg2num(float(m.attrib['lat']),float(m.attrib['lon']),zoom=ZM)
			nodes[m.attrib['id']]=[x,y]
			#print m.attrib
			if 'k' in m.attrib:
				if m.attrib['k']=="barrier":
					pass
			#do the translation here
		for n in root.findall('way'):
			oneway=False
			weight=1
			for ow in n.findall('tag'):
				if ow.attrib['k']=='oneway' and ow.attrib['v']=='yes':
					oneway=True
				if ow.attrib['k']=='junction' and ow.attrib['v']=='roundabout':
					oneway=True
				#weights go here
				for wts in wt:
					if ow.attrib['k']==wts[0] and ow.attrib['v']==wts[1]:
						weight*=float(wt[wts])
			if weight<0:
				continue
			prev=None
			for l in n.findall('nd'):
	
				current=l.attrib['ref']
				if current not in waydict:
					waydict[current]={}
				if prev:
					waydict[prev][current]=weight*self.distance(nodes[prev],nodes[current])
					if not oneway:
						waydict[current][prev]=weight*self.distance(nodes[current],nodes[prev])
				prev=current
		#convert to format for dikstra function	
		n=[]
		for a in waydict:
			for b in waydict[a]:
				#print [nodes[a],nodes[b]]
				n.append([a,b,waydict[a][b]])
		return n,nodes
	
		
	def distance(self,a,b):
		return math.sqrt(((a[0]-b[0])**2)+((a[1]-b[1])**2))
	
	def pointlinedistance(self,line,point):
		#should this go in a geometry library?
		x1=line[0][0]
		y1=line[0][1]
		x2=line[1][0]
		y2=line[1][1]
		x3=point[0]
		y3=point[1]
		u=(((x3-x1)*(x2-x1))+((y3-y1)*(y2-y1)))/(((x2-x1)**2)+((y2-y1)**2))
		if u<0.0001 or u>1:
			if ((x3-x1)**2)+((y3-y1)**2)<((x3-x1)**2)+((y3-y1)**2):
				ix=x1
				iy=y1
			else:
				ix=x2
				iy=y2
		else:
			ix = x1 + u * (x2 - x1)
			iy = y1 + u * (y2 - y1)
		d=((ix-x3)**2)+((iy-y3)**2)
		return (ix,iy),d

	
	def Dijkstra(self,f,t):
		#returns shortest path
		g=defaultdict(list)
		for l,r,c in self.graph:
			g[l].append((c,r))	
		q,seen = [(0,f,())],set()
		while q:
			(cost,v1,path)=heapq.heappop(q)
			if v1 not in seen:
				seen.add(v1)
				path = (v1,path)
				if v1==t:return self.Flatten(cost,path)
				for c, v2 in g.get(v1,()):
					if v2 not in seen:
						heapq.heappush(q,(cost+c, v2, path))
		return (-1,-1)

	def Flatten(self,L):
		while len(L)>0:
			yield L[0]
			L=L[1]

	def findclosest(self,x,y):
		#finds closest nodes to location (x,y=lat,lon)
		closest=None
		offset=float(1000000)
		for n in self.nodes:
			dist=distance((self.nodes[n][0],self.nodes[n][1]),(x,y))
			if dist<offset:
				offset=dist
				closest=n
		return offset,closest

	def findminmax(self):
		a= min([self.nodes[x][0] for x in self.nodes])
		b= max([self.nodes[x][0] for x in self.nodes])
		c= min([self.nodes[x][1] for x in self.nodes])
		d= max([self.nodes[x][1] for x in self.nodes])
		e=min([b-a,d-c])
		return a,b,c,d,e

	def getloc(self,pos):
		nearest=100000
		nearpoint=(0,0)
		ln=-1
		for n in self.graph:
			a,b=self.pointlinedistance((self.nodes[n[0]],self.nodes[n[1]]),pos)
			if b<nearest:
				nearest=b
				nearpoint=a
				ln=n
		return nearpoint,ln

class osmmap():
	def __init__(self,zoom=13,baseurl="https://tile.openstreetmap.org/"):

		self.zoom=zoom
		self.baseurl=baseurl
		try:
			with open("tilecache.pickle","r") as picfile:
				self.cache=pickle.load(picfile)
		except:
			self.cache={}
		

	def getmetiles(self,a, b):
		try:
			return self.cache[a,b]
		except:
			url = self.baseurl + str(self.zoom) + "/" + str(a) + "/" + str(b) + ".png"
			response = requests.get(url)
			tmp=Image.open(StringIO(response.content)).convert('RGB')
			self.cache[a,b]= tmp.load()
			return self.cache[a,b]

	def deg2num(self,lat_deg, lon_deg):
		lat_rad = math.radians(lat_deg)
		n = 2.0 ** self.zoom
		xtile = ((lon_deg + 180.0) / 360.0 * n)
		ytile = ((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
		xrem = int((xtile % 1) * 256)
		yrem = int((ytile % 1) * 256)
		xtile = int(xtile)
		ytile = int(ytile)
		return (xtile, ytile),(xrem,yrem)

	def locationcolour(self,(xtile,ytile),(xrem,yrem)):
		img=self.getmetiles(xtile,ytile)
		return img[xrem,yrem]
	
	def tilesave(self):
		with open("tilecache.pickle","w") as picfile:
			pickle.dump(self.cache,picfile)
			

with open('sampledata.pickle') as file:
	osm=pickle.load(file)
x=this(osm,'car')
