#!python3
import andyconfig
import os
import requests
import json
import datetime
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import io



#print os.environ['ALKEY']


class RTEM():
	def __init__(self):
		
		n=requests.get("http://bcc.opendata.onl/UTMC RTEM.json?ApiKey="+os.environ['ALKEY'])
		self.data=n.json()
	
	def sites_get(self):
		ret=set()
		for n in self.data['RTEMS']['RTEM']:
			ret.add(n['SCN']['Site'])
		return ret
	
	def findcurrentdata(self,site,removezeroes=False):
		ret=[]
		for n in self.data['RTEMS']['RTEM']:
			if n['SCN']['Site']==site:
				if removezeroes:
					if n['Speed']+n['Cars']+n['Trailers']+n['Rigids']+n['Buses']==0:
						continue
				ret.append([n['SCN']['content'], n['Speed'],n['Cars']+n['Trailers']+n['Rigids']+n['Buses'], int((datetime.datetime.now()-datetime.datetime.strptime(n['Date'],"%Y-%m-%d %H:%M:%S")).total_seconds()/60)])
		return ret
						
	def findhistoricdata(self,site,end=str((datetime.datetime.now()+datetime.timedelta(days=1)).date()),start=str(datetime.datetime.now().date()-datetime.timedelta(days=0)),removezeroes=False):
		url="http://bcc.opendata.onl/UTMC RTEM.json?"+"SCN="+str(site)+"&TS=true&Earliest="+start+"&Latest="+end+"&ApiKey="+os.environ['ALKEY']
		#print url
		
		n=requests.get(url)
		res=n.json()
		#print (res['RTEMs']['Data']['Speed'])
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
		
def graph(loc='R0199D1L0'):
		ret=[]
		x=RTEM()
		data= x.findhistoricdata("R0199D1L0")
		mov=[data[y]['Speed'] for y in data]
		t=[x for x in data]
		mov=[0 if x>127 else x for x in mov]
		plt.plot(t,mov,linestyle='None',marker='o')
		plt.title('Speed '+loc+'\n'+str(t[-1]))
		img=io.BytesIO()
		plt.savefig(img)
		img.seek(0)
		ret.append(img)
		plt.close()
		mov=[data[y]['Cars'] for y in data]
		t=[x for x in data]
		mov=[0 if x>127 else x for x in mov]
		plt.plot(t,mov,linestyle='None',marker='o')
		plt.title('Cars '+loc+'\n'+str(t[-1]))
		img=io.BytesIO()
		plt.savefig(img)
		img.seek(0)
		ret.append(img)
		plt.close()
		return ret

if __name__=='__main__':
	from PIL import Image
	s=Image.open(graph()[0])
	s.show()
	s=Image.open(graph()[1])
	s.show()


	'''
	import matplotlib.pyplot as plt
	import time
	x=RTEM()
	while True:
		print (x.sites_get())
		print (x.findcurrentdata(199, removezeroes=True))
		data= x.findhistoricdata("R0199D1L0")
		#print [x for x in data],[data[y]['Cars'] for y in data]
		
		mov=[data[y]['Speed'] for y in data]
		mov=[-10 if x>127 else x for x in mov]
		
		
		avg=[int(sum(mov[a:a+5])/5) for a in range(len(mov)-4)]
		#print (avg)
		t=[x for x in data]
		tt=[str(x) for x in data]
		print (list(zip(tt,mov)))
		#plt.plot([x for x in t[:-4]],avg,linestyle="None",marker="o")
		plt.plot(t,mov,linestyle='None',marker='o')
		
		plt.show()
		plt.close()
		mov=[data[y]['Cars'] for y in data]
		mov=[-10 if x>127 else x for x in mov]
		
		
		avg=[int(sum(mov[a:a+5])/5) for a in range(len(mov)-4)]
		#print (avg)
		t=[x for x in data]
		tt=[str(x) for x in data]
		#print (list(zip(tt,mov)))
		#plt.plot([x for x in t[:-4]],avg,linestyle="None",marker="o")
		plt.plot(t,mov,linestyle='None',marker='o')
		
		plt.show()
		plt.close()
		time.sleep(60)
		'''
