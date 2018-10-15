import os
import andyconfig
import requests
import xml.etree.ElementTree as ET
#import folium
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import StringIO
import g

#m=folium.Map(location=(52.48,-1.9),zoom_start=12)

class Point:
	def __init__(self,x,y):
		self.x=x
		self.y=y
def ccw(A,B,C):
	return (C.y-A.y)*(B.x-A.x)>(B.y-A.y)*(C.x-A.x)
def intersect(A,B,C,D):
	return ccw(A,C,D)!=ccw(B,C,D) and ccw(A,B,C)!=ccw(A,B,D)

class Shape():
	def __init__(self,coordlist):
		self.coordlist=coordlist
		if self.coordlist[0]<>self.coordlist[-1]:
			self.coordlist.append(self.coordlist[0])
		self.hlon=float(max(coordlist,key=lambda item:float(item[0]))[0])
		self.llon=float(min(coordlist,key=lambda item:float(item[0]))[0])
		self.hlat=float(max(coordlist,key=lambda item:float(item[1]))[1])
		self.llat=float(min(coordlist,key=lambda item:float(item[1]))[1])

	def reallyuseless(self,x1,y1,x2,y2):
		counter=0
		prevx,prevy=float(self.coordlist[0][0]),float(self.coordlist[0][1])
		for n in self.coordlist[1:]:
			bits=n
			if intersect(Point(prevx,prevy),Point(float(bits[0]),float(bits[1])),Point(y1,x1),Point(y2,x2))==True:
				counter+=1
			prevx,prevy=float(bits[0]),float(bits[1])
		if counter%2<>0:
			return True
		else:
			return False
			
	def iswithin(self,lon,lat):
		if self.llat<float(lat)<self.hlat and self.llon<float(lon)<self.hlon:
			return self.reallyuseless(float(lat),self.llon,float(lat),float(lon))
		else:
			return False



def showgraph(days=56):
	citycentre=[[-1.9195931,52.4921118],[-1.923713,52.4875127],[-1.9278329,52.4833313],[-1.9319527,52.4795677],[-1.9305794,52.4753855],[-1.9243996,52.4716212],[-1.9175332,52.4682749],[-1.9099801,52.4661833],[-1.9017403,52.4640916],[-1.8921273,52.4624182],[-1.8859475,52.4615815],[-1.8804543,52.4632549],[-1.8749612,52.46702],[-1.8708413,52.4712029],[-1.8715279,52.476222],[-1.8735879,52.4816586],[-1.8777077,52.4883489],[-1.8838875,52.4921118],[-1.8900674,52.4942022],[-1.8976205,52.4950383],[-1.9065468,52.4958744],[-1.9140999,52.4958744],[-1.9195931,52.4921118]]

	strdate='%Y-%m-%dT%H:%M:%S'
	keys={'app_key':os.environ['ELGINKEY']}

	a=requests.get('http://data-api.roadworks.org/',params=keys)
	n=a.content
	start=n.find("SOAP-ENV:Body>")+14
	end=n.find("</SOAP-ENV:Body>")
	n=n[start:end]
	#print n[:10000]

	root=ET.fromstring(n)
	ns="{http://datex2.eu/schema/2/2_0}"
	res=[]

	for p in root.findall(ns+'payloadPublication'):
		for sit in p.findall(ns+'situation'):
			thisrecord={}
			tmp=""
			coords=[]
			for record in sit.findall(ns+'situationRecord'):
				thisrecord['severity']=record.find(ns+'severity').text
				for gpc in record.findall(ns+'generalPublicComment'):
					for values in gpc.iter(ns+'value'):
						tmp+=values.text+"<BR>"
						for npc in record.findall(ns+'nonGeneralPublicComment'):
							for values in npc.iter(ns+'value'):
								tmp+=values.text     
				thisrecord['comment']=tmp.replace('<BR>',' ')
				for gol in record.findall(ns+'groupOfLocations'):
					coords=[[float(x.text) for x in gol.iter(ns+'latitude')][0],[float(x.text) for x in gol.iter(ns+'longitude')][0]]
				thisrecord['coordinates']=coords
				for validity in record.findall(ns+'validity'):
					for vts in validity.findall(ns+'validityTimeSpecification'):
						thisrecord['start']=datetime.datetime.strptime(vts.findall(ns+'overallStartTime')[0].text.split('.')[0],strdate)
						thisrecord['end']=datetime.datetime.strptime(vts.findall(ns+'overallEndTime')[0].text.split('.')[0],strdate)
			tmp=tmp.replace("'","")
			res.append(thisrecord)
	#		folium.Marker(coords,popup=tmp).add_to(m)

	from collections import defaultdict
	workdays1=defaultdict(int)
	workdays2=defaultdict(int)
	workdays3=defaultdict(int)
	nw=datetime.datetime.now()
	shp=Shape([g.WGS84toOSGB36(n[1],n[0]) for n in citycentre])
	#print [g.WGS84toOSGB36(n[1],n[0]) for n in citycentre]
	for d in res:
		if shp.iswithin(*g.WGS84toOSGB36(*d['coordinates'])):
			j= int(((d['start']-nw).total_seconds())/86400)
			if j<0:
				j=0
			k= int(((d['end']-nw).total_seconds())/86400)
			for n in range(j,k+1):
				if d['severity']=='low':
					workdays1[n]+=1
				if d['severity']=='medium':
					workdays2[n]+=1
				if d['severity']=='high':
					workdays3[n]+=1
	p1=plt.bar(range(days),[workdays1[n]+workdays2[n]+workdays3[n] for n in range(days)])
	p2=plt.bar(range(days),[workdays2[n]+workdays3[n] for n in range(days)])
	p3=plt.bar(range(days),[workdays3[n] for n in range(days)])
	plt.legend((p1[0],p2[0],p3[0]),('low','medium','high'), title='Severity')
	plt.title('City Centre Planned Streetworks Next '+str(days)+' Days')
	plt.xlabel('Number of days from today')
	plt.ylabel('Streetworks')
	imgdata=StringIO.StringIO()
	plt.savefig(imgdata,format='png')
	imgdata.seek(0)
	plt.close()
	return imgdata.buf

if __name__=='__main__':
	file('foo.png','w').write(showgraph(days=56))
