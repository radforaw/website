#!python3
import requests
try:
	from lxml import etree as ET
except ImportError:
	import xml.etree.cElementTree as ET
import datetime
import matplotlib as mpl
import matplotlib.style
mpl.use('Agg')
mpl.style.use('classic')
import matplotlib.pyplot as plt
import io

from collections import defaultdict

class carpark:
	def __init__(self):
		self.carpark=self.getcarparknames()

	def getcarparknames(self):
		blacklist=['Bull Ring','NIA Car Parks']
		url='http://bcc.opendata.onl/UTMC Parking.xml?ApiKey=7N0BRC3CT4KIB4BY5342743137151'
		n=requests.get(url).content
		root = ET.fromstring(n)
		res={}
		for x in root.findall('Carpark'):
			no=float(x.find('Northing').text)
			td=(datetime.datetime.now()-datetime.datetime.strptime(x.find('Date').text,"%Y-%m-%d %H:%M:%S")).total_seconds()
			if no>0 and td<84000 and x.find('Description').text not in blacklist:
				ra,rb,rc=x.find('Description').text,int(x.find('Occupancy').text),int(x.find('Capacity').text)
				if rb>rc*1.3:
					rb=0
				res[x.find('SCN').text]=[ra,rb,rc,td,x.find('SCN').text]
		return res

	def livegraph(self):
		i=self.carpark
		tcp=sorted([i[j] for j in i],key= lambda x:x[2],reverse=False)
		plt.barh(range(len(tcp)),[n[2] for n in tcp],color='Grey')
		plt.barh( range(len(tcp)),[n[1] for n in tcp],color='#b666d2')
		plt.gca().set_yticks([a+0.4 for a in range(len(tcp))])
		plt.gca().set_yticklabels(['   '+n[0]+' '+n[4] for n in tcp],ha='left')
		plt.gca().spines['top'].set_visible(False)
		plt.gca().spines['right'].set_visible(False)
		plt.tick_params(top='off', bottom='on', left='off', right='off', labelleft='on', labelbottom='on')
		plt.gca().set_ylim([0,len(tcp)])
		#ax.spines['bottom'].set_visible(False)
		#ax.spines['left'].set_visible(False)
		plt.legend(['Capacity','Occupancy'], loc='lower right')
		#plt.title('Birmingham City Centre Car Parks\nStatus at '+str(datetime.datetime.now()))
		f=io.BytesIO()
		plt.savefig(f,format='png',bbox_inches='tight')
		f.seek(0)
		bars = [rect for rect in plt.gca().get_children() if isinstance(rect, mpl.patches.Rectangle)]
		#print (a.get_xy())
		t=([[a.get_xy()[0],a.get_xy()[1],a.get_height(),a.get_width()] for a in bars])
		print (t)
		res=[list(plt.gca().transData.transform((l[0],l[1])))+list(plt.gca().transData.transform((l[0]+l[3],l[1]+l[2]))) for l in t][:len(tcp)]
		#res.reverse()
		print (res)
		res={tcp[n][4]:[int(res[n][0]),520-int(res[n][1]),int(res[n][2]),520-int(res[n][3])]for n in range(len(res))}
		print(res)
		#ax.transData.transform((5, 0))
		#plt.savefig('test.png')
		plt.close()
		return f,res
		

	def historic(self,n,earl,lat):
		url='http://bcc.opendata.onl/UTMC Parking.xml?SCN='+n+'&TS=true&Earliest='+earl+'&Latest='+lat+'&ApiKey=7N0BRC3CT4KIB4BY5342743137151'
		m= requests.get(url).content
		root = ET.fromstring(m)
		xa,ya,zen,zex=[],[],[],[]
		for x in root.findall('Data'):
			xa.append(datetime.datetime.strptime(x.find('Date').text,"%Y-%m-%d %H:%M:%S"))
			ya.append(x.find('Occupancy').attrib['Percent'])
			zen.append(float(x.find('Statistics').attrib['Entry']))
			zex.append(float(x.find('Statistics').attrib['Exit']))
		cum=defaultdict(float)
		cum2=defaultdict(float)
		#print (xa[0].day)
		barx=[datetime.datetime(xa[0].year,xa[0].month , xa[0].day, h, 0, 0, 0) for h in range(24)]
		barx2=[datetime.datetime(xa[0].year,xa[0].month,xa[0].day, h, 30, 0, 0) for h in range(24)]
		
		for nn in range(len(xa)-1):
			
			diff=(xa[nn+1]-xa[nn]).total_seconds()/60
			hr= (xa[nn+1].hour)
			cum[hr]+=diff*zen[nn+1]
			#print (diff,zen[nn+1],diff*zen[nn+1],cum)
			cum2[hr]+=diff*zex[nn+1]
			#print (diff,zex[nn+1],diff*zex[nn+1],cum2)
		hren=[int(cum[h]) for h in range(24)]
		hrex=[int(cum2[h]) for h in range(24)]
			
		ax=plt.plot(xa,ya)
		bx=plt.plot(xa,[(j/max(zen))*100 for j in zen])
		cx=plt.plot(xa,[(j/max(zex))*100 for j in zex])
		#dx=plt.bar(barx,hren,width=0.01,color='grey')
		#dy=plt.bar(barx2,hrex,width=0.01,color='orange')
		print (60.0/max(zen),60.0/max(zex))
		plt.legend(['% Full','in','out'], loc='upper left')
		plt.title(self.carpark[n][0]+'\n'+str(xa[0].date()))
		plt.show()


'''
a=carpark()
a.historic('BHMBRCBRG03','19/01/2019','20/01/2019')
'''


a,b=carpark().livegraph()
with open ('file.png','wb') as r:
	r.write(a.read())
a.close()

import os
fl='file://'+os.path.abspath('file.png')
fl="file.png"

site='<!DOCTYPE html><html><head><title>very much under test</title></head><body>some text<img src="'+fl+'" alt="graph" usemap="#graphmap"><map name="graphmap">'
for n in b:
	m=n.replace(' ','%20')
	site+='<area shape="rect" coords="'+str(b[n][0])+','+str(b[n][1])+','+str(b[n][2])+','+str(b[n][3])+'" href='+m+'" alt="'+m+'">'

site+='</map></body></html>'

with open('site.html','w') as r:
	r.write(site)
'''
import ui,os
from urllib.parse import urljoin
file_path = 'site.html'
#file_path = urljoin('file://', os.path.abspath(file_path))
w = ui.WebView()
w.load_html(site)
w.present()
'''
