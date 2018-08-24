import os

import math
import pickle
import time
import folium
from collections import defaultdict

import geometry
import shortest
import sampleget
import journeytimeinfo


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



def main():
	#get data on the links from the portal
	ret=journeytimeinfo.getwifidata()
	# work out how much large the network needs to be
	x, y = minmax([ret[x]['coordinates'][0] for x in ret] + [ret[x]['coordinates'][1] for x in ret])
	# update the sampledata if it is out of data
	old = time.time() - os.path.getmtime('sampledata.pickle')
	if old > 400060: 
		sampleget.osmcreate(x, y)
	
	ctr = 0
	res1=[]
	offdata=offset()
	with open('sampledata.pickle') as file:
		osm = pickle.load(file)
		a, b = shortest.OsmRouteImport(osm)  #a-links,b-nodes
		minx, maxx, miny, maxy, ratio = shortest.findminmax(b)

	for n in ret:
		ctr+=1
		print int((float(ctr) / len(ret))*100),"%"
		t = geometry.deg2num(ret[n]['coordinates'][0][0], ret[n]['coordinates'][0][1], zoom=13)
		t1 = geometry.deg2num(ret[n]['coordinates'][1][0], ret[n]['coordinates'][1][1], zoom=13)
		origang = (shortest.angle(t, t1)) #not currently required
		r2 = []
		tst=time.time()
		zt=shortest.getlocsa(t1, b, a, origang)
		for start in shortest.getlocsa(t, b, a, origang):
			for end in zt:
				r2.append(
					shortest.setupshortest(start[0], start[1], end[0], end[1], t, b, a, origang))
		print time.time()-tst
		#tmp=[(x[0],x[1]) for x in min(r2, key=lambda x: x[0])[1]]
		ret[n]['route']=[geometry.WGS84toOSGB36(*geometry.num2deg(x[0],x[1],13)) for x in min(r2, key=lambda x: x[0])[1]]
		ret[n]['distance']=sum([shortest.distance(ret[n]['route'][i],ret[n]['route'][i+1]) for i in range(len(ret[n]['route'])-1)])
		if ctr == 5:
			break
		
	import json
	with open ('links.json','w') as jsonfile:
		json.dump(ret,jsonfile)

	#this section draws the map

	map_osm = folium.Map(location=(52.483678100000005, -1.8201131000000134), zoom_start=14)
	col = ['red', 'green', 'blue']
	col=['#fff7f3','#fde0dd','#fcc5c0','#fa9fb5','#f768a1','#dd3497','#ae017e','#7a0177','#49006a']
	ctr=0
	vals=[]
	res1=[ret[a]['route'] for a in ret if 'route' in ret[a]]
	for n in res1:
		distance=sum([shortest.distance(n[a],n[a+1]) for a in range(len(n)-1)])
		vals.append([distance,n])
	vals=[n[1] for n in sorted(vals)]
	for tmp in vals:
		mx=max([offdata.add(tmp[x][0],tmp[x][1],20) for x in range(len(tmp)-1)])
		temp=[offdata.off((tmp[x][0],tmp[x][1]),(tmp[x+1][0],tmp[x+1][1]),mx) for x in range(len(tmp)-1)]
		tp=[a[0] for a in temp]
		tp.append(temp[-1][1])
		print tp
		temp = [
			geometry.OSGB36toWGS84(x[0], x[1]) for x in tp
		]
		print 'm', min(r2, key=lambda x: x[0])[0]
		
		folium.PolyLine(
			temp, color='black',weight=8).add_to(map_osm)
		folium.PolyLine(
			temp, popup='try later',weight=7, color=col[ctr % 9]).add_to(map_osm)
		ctr+=1

	
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
