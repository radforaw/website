import andyconfig
import os
import requests
import json
import datetime
import matplotlib.pyplot as plt
print os.environ['ALKEY']


class RTEM():
	def __init__(self):
		
		n=requests.get("http://bcc.opendata.onl/UTMC RTEM.json?ApiKey="+os.environ['ALKEY'])
		self.data=n.json()
		
	def findcurrentdata(self,site,removezeroes=False):
		ret=[]
		for n in self.data['RTEMS']['RTEM']:
			if n['SCN']['Site']==site:
				if removezeroes:
					if n['Speed']+n['Cars']+n['Trailers']+n['Rigids']+n['Buses']==0:
						continue
				ret.append([n['Speed'],n['Cars']+n['Trailers']+n['Rigids']+n['Buses'], int((datetime.datetime.now()-datetime.datetime.strptime(n['Date'],"%Y-%m-%d %H:%M:%S")).total_seconds()/60)])
		return ret
						
	def findhistoricdata(self,site,start=str((datetime.datetime.now()-datetime.timedelta(days=1)).date()),end=str(datetime.datetime.now().date()),removezeroes=False):
		url="http://bcc.opendata.onl/UTMC RTEM.json?"+"SCN="+str(site)+"&TS=true&Earliest="+start+"&Latest="+end+"&ApiKey="+os.environ['ALKEY']
		print url
		
		n=requests.get(url)
		res=n.json()
		#print res['RTEMs']['Data']['Speed']
		data=[]
		names=[]
		for n in res['RTEMs']['Data']:
			names.append(n)
			data.append(res['RTEMs']['Data'][n])
		d = [[data[j][i] for j in range(len(data))] for i in range(len(data[0]))]
		tmp=[]
		for n in d:
			tmp.append({names[a]:n[a] for a in range(len(data))})
		d={datetime.datetime.strptime(a['Date'],"%Y-%m-%d %H:%M:%S"):a for a in tmp}	
		return d
		
		#with open('deletethis.txt','w') as hello:
		#	hello.write(n.content)

x=RTEM()

print json.dumps(x.data,indent=2)

print x.findcurrentdata(199, removezeroes=True)
'''
data= x.findhistoricdata("R0199D1L1")
print [x for x in data],[data[y]['Cars'] for y in data]

plt.plot([x for x in data],[data[y]['Cars'] for y in data],linestyle="None",marker="o")

plt.show()
'''
