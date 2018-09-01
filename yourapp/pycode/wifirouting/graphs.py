import datetime
import os
import andyconfig as config
import requests
import xml.etree.cElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import StringIO

class drawagraph():
	def __init__(self,scn):
		self.scn=scn
		self.ct={}
		self.graph()
		self.quality=int((len(self.ct)/float(28*12*24))*100)
		self.img = StringIO.StringIO()
		self.nextbit()
		self.img.seek(0)
		plt.clf()
		
	def graph(self):
		url='http://bcc.opendata.onl/UTMC ANPR.xml'
		par={'start':str(datetime.datetime.now().date()),
		'end': str((datetime.datetime.now()-datetime.timedelta(days=28)).date()), 'TS':True,'ApiKey': os.environ['ALKEY'],'SCN':self.scn}
		n = requests.get(url, params=par)
		root = ET.fromstring(n.content)
		for a in root.findall('Data'):
			tmp=[]
			#2018-08-07 01:25:00
			j= a.find('Plates').attrib
			j= {k:int(j[k]) for k in j}
			d={'speed':float(a.find('Speed').text),'time':int(a.find('Time').text)}
			z=j.copy()
			z.update(d)
			self.ct[datetime.datetime.strptime(a.find('Date').text,'%Y-%m-%d %H:%M:%S')]=z

	def nextbit(self):
		tm=datetime.datetime.now()-datetime.timedelta(days=28)
		tm = tm - datetime.timedelta(minutes=tm.minute % 5,seconds=tm.second,microseconds=tm.microsecond)
		b=datetime.timedelta(minutes=5)
		c=[tm+(b*n) for n in range(28*12*24)]
		jt=0
		thing=[]
		for d in c:
			if d in self.ct:
				if 500>self.ct[d]['time']>0:
					jt=self.ct[d]['time']
				thing.append(jt)
		mult=len(thing)/4
		g,h=[],[]
		for n in range(mult):
			g.append(sorted([thing[n],thing[n+mult],thing[n+mult+mult]])[1])
			h.append(thing[n+mult+mult+mult])
		c=[a.strftime("%H:%M") for a in c]
		plt.plot(range(24),g[-24:],color="grey",label="last 4 weeks")
		plt.plot(range(24),h[-24:], label="today")
		plt.legend()
		plt.xticks(range(24),c[-24:],rotation='vertical')
		plt.title(self.scn+"\nQuality " +str(self.quality)+"%")
		plt.savefig(self.img)
		
if __name__=="__main__":
	from PIL import Image
	s=Image.open(drawagraph("WiFiL1").img)
	s.show()
