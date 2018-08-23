import config
import os
import requests
import xml.etree.cElementTree as ET
import re
import math
import geometry
import shortest
import pickle
import sampleget
import time
import folium
import os
from collections import defaultdict

def dist(x):
	a1 = x[0][0]
	a2 = x[1][0]
	b1 = x[0][1]
	b2 = x[1][1]
	return math.sqrt(((a1 - a2)**2) + ((b1 - b2)**2))


def minmax(a):
	minx = min([x[0] for x in a])
	maxx = max([x[0] for x in a])
	miny = min([x[1] for x in a])
	maxy = max([x[1] for x in a])
	minx-=(maxx-minx)*.2
	miny-=(maxx-minx)*.2
	maxx+=(maxx-minx)*.2
	maxy+=(maxx-minx)*.2
	return (minx, miny), (maxx, maxy)


class cache:
	def __init__(self):
		try:
			with open('cache.p', 'r') as pfile:
				self.c = pickle.load(pfile)
		except:
			self.c = {}

	def datagrab(self, url):
		par = {'ApiKey': os.environ['ALKEY']}
		try:
			n = requests.get(url, params=par, timeout=1)
		except:
			return self.c[url].content
		self.c[url] = n
		with open('cache.p', 'w') as pfile:
			pickle.dump(self.c, pfile)
		return n.content

class offset():
	def __init__(self):
		self.c=defaultdict(int)
		
	def add(self,a,b,off=0.0024):
		self.c[(a,b)]+=1
		off*=self.c[(a,b)]
		return off
		
	def off(self,a,b,off):
		x1,y1=a
		x2,y2=b
		ang=math.atan2(x2-x1,y2-y1)-(3.1415926/2.0)
		lx,ly=math.sin(ang)*off,math.cos(ang)*off
		return [(x1+lx,y1+ly),(x2+lx,y2+ly)]
	
	def check(self,a,b,off=0.0024):
		null=self.add(a,b,off)
		return self.off(a,b,off)


def setupshortest(plt, ln, plt1, ln1, t, b, a, origang):
	#plt,ln= shortest.getloc(t,b,a,origang)
	n1 = b[ln[0]]  #gets point of start of line
	n2 = b[ln[1]]  #gets point of end of line
	if [True for tmp in a if tmp[0] == ln[1] and tmp[1] == ln[0]]:
		ns = [[-1, ln[0], shortest.distance(n2, plt)/4]]
	else:
		ns = [[-1, ln[1], shortest.distance(n1, plt)/4]]
	n1 = b[ln1[0]]
	n2 = b[ln1[1]]
	if [True for tmp in a if tmp[0] == ln1[1] and tmp[1] == ln1[0]]:
		ns += [[ln1[1], -2, shortest.distance(n2, plt1)/4]]
	else:
		ns += [[ln1[0], -2, shortest.distance(n1, plt1)/4]]
	try:
		temp = list(shortest.Flatten(shortest.Dijkstra(a + ns, -1,-2)))
		dist = temp[0]
		temp = temp[2:-1]
	except:
		return 100000, 0
	temp = [list(plt1)] + [b[nn] for nn in temp] + [list(plt)]
	return dist, temp

def main():
	#print n.content
	f = cache()
	root = ET.fromstring(f.datagrab('http://bcc.opendata.onl/UTMC Flow.xml'))
	locs = {}
	for flow in root.findall('Flow'):
		try:
			a = flow.find('SCN').text
			b = float(flow.find('Northing').text)
			c = float(flow.find('Easting').text)
			for val in flow.findall('Value'):
				d = int(val.find('Level').text)
		except AttributeError:
			continue
		b, c = geometry.OSGB36toWGS84(c, b)
		#b,c=geometry.deg2num(c,b,zoom=13)
		#print a,((b,c),d)
		locs[a] = ((b, c), d)
	
	#print n.content
	root = ET.fromstring(f.datagrab('http://bcc.opendata.onl/UTMC ANPR.xml'))
	ret = {}
	for flow in root.findall('ANPR'):
		try:
			a = flow.find('Description').text
			b = flow.find('SCN').text
			c = flow.find('Plates').attrib['matched']
			d = flow.find('Time').text
		except AttributeError:
			continue
		#print a,b,c,d
		tmp = []
		for t in a.split(' '):
			n = re.findall(r'E\d\d\d\d', t)
			if n:
				tmp.append(n[0][1:])
		if tmp:
			try:
				ret[b] = {
					'coordinates': [locs[tmp[0]][0], locs[tmp[1]][0]],
					'Time': d,
					'Description': a,
					'matched': c
				}
			except KeyError:
				print tmp[0], tmp[1]
	
	old = time.time() - os.path.getmtime('sampledata.pickle')
	x, y = minmax([ret[x]['coordinates'][0]
																for x in ret] + [ret[x]['coordinates'][1] for x in ret])
	
	if old > 400060: 
		sampleget.osmcreate(x, y)
	
	map_osm = folium.Map(location=(52.483678100000005, -1.8201131000000134), zoom_start=14)
	ctr = 0
	res1=[]
	offdata=offset()
	with open('sampledata.pickle') as file:
		osm = pickle.load(file)
		a, b = shortest.OsmRouteImport(osm)  #a-links,b-nodes
		minx, maxx, miny, maxy, ratio = shortest.findminmax(b)
		col = ['red', 'green', 'blue']
		col=['#fff7f3','#fde0dd','#fcc5c0','#fa9fb5','#f768a1','#dd3497','#ae017e','#7a0177','#49006a']
	for n in ret:
		ctr+=1
		print int((float(ctr) / len(ret))*100),"%"
		#print ret[n]['coordinates'][0][0]
		t = geometry.deg2num(ret[n]['coordinates'][0][0], ret[n]['coordinates'][0][1], zoom=13)
		t1 = geometry.deg2num(ret[n]['coordinates'][1][0], ret[n]['coordinates'][1][1], zoom=13)
		origang = (shortest.angle(t, t1))
		r2 = []
		zt=shortest.getlocsa(t1, b, a, origang)
		for start in shortest.getlocsa(t, b, a, origang):
			for end in zt:
				r2.append(
					setupshortest(start[0], start[1], end[0], end[1], t, b, a, origang))
				'''if r2[-1][0] > 0 and r2[-1][0]<100000:
					print r2[-1][0],len(r2[-1][1])'''
		'''
		for nn in r2:
			print nn[0]
			try:
				folium.Marker(
				geometry.num2deg(nn[1][0][0], nn[1][0][1], 13),
				icon=folium.Icon(color='green'),popup='start').add_to(map_osm)
	
				folium.Marker(
				geometry.num2deg(nn[1][-1][0], nn[1][-1][1], 13),
				icon=folium.Icon(color='green'), popup='end').add_to(map_osm)
			except:
				continue
		'''
	
		#print len(r2)
		
			#temp=[x for x in r2 if x[0]>0]
			#for nn in r2:
			#print nn[0],len(nn[1])

		tmp=[(x[0],x[1]) for x in min(r2, key=lambda x: x[0])[1]]
		res1.append(tmp)
		if ctr == 2:
			break
		
	import json
	with open ('links.json','w') as jsonfile:
		json.dump(res1,jsonfile)
		
	ctr=0
	vals=[]
	for n in res1:
		distance=sum([shortest.distance(n[a],n[a+1]) for a in range(len(n)-1)])
		vals.append([distance,n])
	vals=[n[1] for n in sorted(vals)]
	for tmp in vals:
		mx=max([offdata.add(tmp[x][0],tmp[x][1],.013) for x in range(len(tmp)-1)])
		temp=[offdata.off((tmp[x][0],tmp[x][1]),(tmp[x+1][0],tmp[x+1][1]),mx) for x in range(len(tmp)-1)]
		tp=[a[0] for a in temp]
		tp.append(temp[-1][1])
		print tp
		temp = [
			geometry.num2deg(x[0], x[1], 13) for x in tp
		]
		print 'm', min(r2, key=lambda x: x[0])[0]
		'''except:
			continue'''
		
		folium.PolyLine(
			temp, color='black',weight=8).add_to(map_osm)
		folium.PolyLine(
			temp, popup='try later',weight=7, color=col[ctr % 9]).add_to(map_osm)
		#folium.Marker(ret[n]['coordinates'][0]).add_to(map_osm)
		#folium.Marker(ret[n]['coordinates'][1]).add_to(map_osm)
		ctr+=1

	
	'''
	to draw
	sort lines by length
	draw longest first
	if line exists in database - increase its offset by 10
	'''
	
	
	map_osm.save('map.html')
	import sys
	if sys.platform=='ios':
		import ui
		file_path = 'map.html'
		file_path = os.path.abspath(file_path)
		w = ui.WebView()
		w.load_url(file_path)
		w.present()
	

if __name__=='__main__':
	main()
