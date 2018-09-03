import json
import folium
import branca
import math
import geometry
import journeytimeinfo
from collections import OrderedDict,defaultdict
from operator import itemgetter
import os
print os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class offset():
	def __init__(self):
		self.c=defaultdict(int)
		
	def add(self,a,b,off=0.0024):
		self.c[(a,b)]+=1
		#print [str(a)[-3:-1],self.c[(a,b)]],
		off*=self.c[(a,b)]
		return off
		
	def off(self,a,b,off):
		x1,y1=a
		x2,y2=b
		ang=math.atan2(x2-x1,y2-y1)+(3.1415926/2.0)
		lx,ly=math.sin(ang)*off,math.cos(ang)*off
		return [(x1+lx,y1+ly),(x2+lx,y2+ly)]
	
	def check(self,a,b,off=0.0024):
		null=self.add(a,b,off)
		return self.off(a,b,off)

def main():
	with open('links.json','r')as jfile:
		data=json.load(jfile)
	'''for n in data:
		print data[n]
		break'''
	update=journeytimeinfo.getwifidata()
	for x in data:
		data[x]['Time']=update[x]['Time']
		data[x]['matched']=update[x]['matched']
	a=sorted([[data[n][u'distance'],n,data[n]] for n in data if u'distance' in data[n]])
	offdata=offset()
	map_osm = folium.Map(location=(52.483678100000005, -1.8201131000000134), zoom_start=14)
	col = ['red', 'green', 'blue']
	col=['#fff7f3','#fde0dd','#fcc5c0','#fa9fb5','#f768a1','#dd3497','#ae017e','#7a0177','#49006a']
	ctr=0



	for tmp in a:
		#print tmp
		print tmp[2][u'Description'],
		mx=[offdata.add(tmp[2][u'route'][x][0],tmp[2][u'route'][x][1],40) for x in range(len(tmp[2][u'route']))]
		mx=max(mx)
		for x in tmp[2][u'route']:
			offdata.c[(x[0],x[1])]=mx/40
		temp=[offdata.off((tmp[2][u'route'][x][0],tmp[2][u'route'][x][1]),(tmp[2][u'route'][x+1][0],tmp[2][u'route'][x+1][1]),mx) for x in range(len(tmp[2][u'route'])-1)]
		tp=[a[0] for a in temp]
		tp.append(temp[-1][1])
		temp = [
			geometry.OSGB36toWGS84(x[0], x[1]) for x in tp
		]
		#print 'm', min(r2, key=lambda x: x[0])[0]
		try:
			print tmp[2][u'distance'],
			print float(tmp[2][u'Time']),
			print matched
		except:
			print 0,
		try:
			zcol=int((tmp[2][u'distance']/float(tmp[2][u'Time'])/13)*8)
		except:
			zcol=0
		if zcol>8:
			zcol=8
		print zcol
		jx="<HTML><BODY><IMG SRC=\"http://54.164.31.65/graph.png?scn="+str(tmp[1])+"\"></BODY></HTML>"
		iframe=branca.element.IFrame(html=jx,width=660,height=500)
		po=folium.Popup(iframe,max_width=660)
		folium.PolyLine(
			temp, color='black',weight=8).add_to(map_osm)
		folium.PolyLine(
			temp, popup=po,weight=7, color=col[zcol]).add_to(map_osm)
		ctr+=1
	
	
	return map_osm.get_root().render()

if __name__=="__main__":
	import sys,os, StringIO
	if sys.platform=='ios':
		import ui
		#file_path=StringIO.StringIO(main())
		#file_path = 'map.html'
		#file_path = os.path.abspath(file_path)
		w = ui.WebView()
		#w.load_url(file_path)
		w.load_html(main())
		w.present()
