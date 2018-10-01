import requests
try:
	from lxml import etree as ET
except ImportError:
	import xml.etree.cElementTree as ET
from io import StringIO
import g
from math import pi,atan2,sqrt
import drawer
	
def latlonsplit(latr):
	return float(latr[:2]+'.'+latr[2:])
	
def angle(a,b):
	x=a[0]-b[0]
	y=a[1]-b[1]
	r=atan2(x,y)*(180/pi)
	r+=180
	return r%360
	
def dist(a,b):
	x=a[0]-b[0]
	y=a[1]-b[1]
	return sqrt(x*x+y*y)

def cardinal(angle):
	reslist=('N','NE','E','SE','S','SW','W','NW')
	return reslist[int(((angle+22.5)%360)/45.0)]
	
def movement(angs):
	defs=('SA','R','U','L')
	calc=int((((angs[1]-angs[0])+45)%360)/90)
	return defs[calc]

def getmap(junc):
	l=0
	url='https://highwaysits-web.northeurope.cloudapp.azure.com/aqatane/demos/crocs/glosaactions?action=MAPCommunicate&param='+str(junc)
	n=requests.get(url,timeout=5)
	root = ET.fromstring(n.content[155:-37])
	print n.content[0:10000]
	a={}
	b={}
	for intersection in root.findall('intersections'):
		for geo in intersection.findall('IntersectionGeometry'):
			for id1 in geo.findall('id'):
				for id2 in id1.findall('id'):
					print id2.text
			for ref in geo.findall('refPoint'):
				a['centroid']=g.WGS84toOSGB36(latlonsplit(ref.find('lat').text),latlonsplit(ref.find('long').text))
			for lan in geo.findall('laneSet'):
				for glan in lan.findall('GenericLane'):
					tmp= glan.find('laneID').text
					tmp2=[]
					for nod in glan.findall('nodeList'):
						for nods in nod.findall('nodes'):
							for node in nods.findall('Node'):
								for delta in node.findall('delta'):
									for ll in delta.findall('node-LatLon'):
										
														tmp2.append(g.WGS84toOSGB36(latlonsplit(ll.find('lat').text),latlonsplit(ll.find('lon').text)))
					
					for ct in glan.findall('connectsTo'):
						for conn in ct.findall('Connection'):
							for cl in conn.findall('connectingLane'):
								for ln in cl.findall('lane'):
									tmp3=[tmp,ln.text]
							for sg in conn.findall('signalGroup'):
								print sg.text
								try:
									b[sg.text].append(tmp3)
								except:
									b[sg.text]=[tmp3]
								
					a[tmp]=tmp2
			ct=a['centroid']
	#sort so they are the right way around
	res={}
	for n in b:
		for d in b[n]:
			new=[]
			for t in a[d[0]]:
				new.append([dist(ct,t),t])
			a[d[0]]=[i[1]for i in sorted(new,reverse=True)]
			new=[]
			for t in a[d[1]]:
				new.append([dist(ct,t),t])
			a[d[1]]=[i[1]for i in sorted(new)]
	return a,b
	
if __name__=='__main__':o
	a,b= getmap(1991)
	print 'a=',a
	print 'b=',b
	#setup visualisation
	l,m=[],[]
	for n in a:
		if n<>'centroid':
			for y in a[n]:
				l.append(y[0])
				m.append(y[1])
	dd=drawer.drawing((min(l),max(l),min(m),max(m)),(640,480))
	#end visualisaion
	
	#calculate line direction
	colors=[(0,0,0),(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255),(128,128,128)]
	cc=0
	res={}
	for n in a:
		c=colors[cc]
		cc+=1
		if cc>=len(colors):
			cc=0
		old=a[n][0]
		if n<>'centroid':
			ang=[]
			for y in a[n][1:]:
				ang.append(angle(old,y))
				dd.line(old,y,c) 
				old=y
			res[n]=ang  
			
	#show results
	fin={}
	alt=[]
	for n in b:
		fin[n]=[]
		tmp=[]
		for d in b[n]:
			rr=(cardinal(res[d[0]][-1]),movement([res[d[0]][-1], res[d[1]][0]]))
			if rr not in fin[n]:
				fin[n].append(rr)
				tmp.append(rr)
			
		alt.append(tmp)
	print fin
	mov=[]
	for n in alt:
		tmp=[]
		s=-10
		for m in n:
			if m[0]=='N'or m[0]=='NE':
				s=6
			if m[0]=='E'or m[0]=='SE':
				s=9
			if m[0]=='S'or m[0]=='SW':
				s=0
			if m[0]=='W'or m[0]=='NW':
				s=3
			if m[1]=='L':
				s+=3
			elif m[1]=='SA':
				s+=2
			else:
				s+=1
			tmp.append(s)
		mov.append(tmp)
	print mov
			
	
	dd.image.show()
'''import sys
sys.exit(0)'''

