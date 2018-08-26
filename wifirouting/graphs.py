import datetime
import os
import config
import requests
import xml.etree.cElementTree as ET


def graph(scn='WiFiL3'):
	url='http://bcc.opendata.onl/UTMC ANPR.xml'
	par={'start':str(datetime.datetime.now().date()),
	'end': str((datetime.datetime.now()-datetime.timedelta(days=28)).date()), 'TS':True,'ApiKey': os.environ['ALKEY'],'SCN':scn}
	n = requests.get(url, params=par)
	#print n.content[-1000:-1]
	root = ET.fromstring(n.content)
	ct={}
	for a in root.findall('Data'):
		tmp=[]
		#2018-08-07 01:25:00
		j= a.find('Plates').attrib
		j= {k:int(j[k]) for k in j}
		d={'speed':float(a.find('Speed').text),'time':int(a.find('Time').text)}
		z=j.copy()
		z.update(d)
		ct[datetime.datetime.strptime(a.find('Date').text,'%Y-%m-%d %H:%M:%S')]=z
	return ct
	

	
def nextbit(ct):
	tm=datetime.datetime.now()-datetime.timedelta(days=28)
	tm = tm - datetime.timedelta(minutes=tm.minute % 5,seconds=tm.second,microseconds=tm.microsecond)
	b=datetime.timedelta(minutes=5)
	c=[tm+(b*n) for n in range(28*12*24)]
	jt=0
	thing=[]
	for d in c:
		if d in ct:
			if 500>ct[d]['time']>0:
				jt=ct[d]['time']
			thing.append(jt)
	mult=len(thing)/4
	for n in range(mult):
		print sorted([thing[n],thing[n+mult],thing[n+mult+mult]])[1],thing[n+mult+mult+mult]
	
	
ct=graph()
print int((len(ct)/float(28*12*24))*100)
nextbit(ct)
