#!python3
import andyconfig
import os
import requests
import json
import datetime
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io



#print os.environ['ALKEY']


class RTEM():
	def __init__(self):
		
		n=requests.get("http://bcc.opendata.onl/UTMC RTEM.json?ApiKey="+os.environ['ALKEY'])
		self.data=n.json()
	
	def sites_get(self):
		ret=set()
		for n in self.data['RTEMS']['kids']:
			ret.add(self.data['RTEMS']['kids'][n]['kids']['SCN']['attrs']['Site'])
		return ret
	
	def findcurrentdata(self,site,removezeroes=False):
		ret=[]
		for n in self.data['RTEMS']['kids']:
			b=self.data['RTEMS']['kids'][n]['kids']
			if int(b['SCN']['attrs']['Site'])==site:
				if removezeroes:
					if float(b['Speed'])+float(b['Cars'])+float(b['Trailers'])+float(b['Rigids'])+float(b['Buses'])==0:
						continue
				ret.append([b['SCN']['value'], float(b['Speed']),float(b['Cars']),float(b['Trailers'])+float(b['Rigids'])+float(b['Buses']), int((datetime.datetime.now()-datetime.datetime.strptime(b['Date'],"%Y-%m-%d %H:%M:%S")).total_seconds()/60),b['Date']])
		return ret
						
	def findhistoricdata(self,site,end=str((datetime.datetime.now()+datetime.timedelta(days=1)).date()),start=str(datetime.datetime.now().date()-datetime.timedelta(days=0)),removezeroes=False):
		url="http://bcc.opendata.onl/UTMC RTEM.json?"+"SCN="+str(site)+"&TS=true&Earliest="+start+"&Latest="+end+"&ApiKey="+os.environ['ALKEY']
		#print url
		
		n=requests.get(url)
		res=n.json()
		#print (n.content[:1000])
		#print (res['RTEMs']['Data']['Speed'])
		data=[]
		names=[]
		for n in res['RTEMs']['kids']:
			b=res['RTEMs']['kids'][n]['kids']
			names.append(b['SCN']['value'])
			data.append(b)
		#print ([i for i in data[0]])
		#d = [[data[j][i] for i in data[0]] for j in range(len(data))] #range(len(data[0]))]
		#print (d)
		d=data
		#tmp=[]
		#for n in d:
		#	tmp.append({names[a]:n[a] for a in range(len(data))})
		d={datetime.datetime.strptime(d[a]['Date'],"%Y-%m-%d %H:%M:%S"):d[a] for a in range(len(d))}	
		return d
		
		#with open('deletethis.txt','w') as hello:
		#	hello.write(n.content)
		
def graph(loc='R0199D1L0'):
	print (datetime.datetime.now())
	ret=[]
	x=RTEM()
	data= x.findhistoricdata(loc,end=str((datetime.datetime.now()+datetime.timedelta(days=1)).date()),start=str(datetime.datetime.now().date()-datetime.timedelta(days=0)))
	mov=[float(data[y]['Speed']) for y in data]
	#print (mov)
	t=[x for x in data]
	mov=[0 if x>127 else x for x in mov]
	plt.figure(figsize=(10,7))
	plt.plot(t,mov,linestyle='None',marker='o')
	#plt.xticks(range(len(t)),[str(tt.time()) for tt in sorted(t)],rotation='vertical')
	myFmt=mdates.DateFormatter('%H:%M')
	plt.gca().xaxis.set_major_formatter(myFmt)
	hours=mdates.HourLocator(interval=1)
	plt.gca().xaxis.set_major_locator(hours)
	plt.gca().set_axisbelow(True)
	plt.gca().yaxis.grid(color='gray',linestyle='dashed')
	plt.gca().xaxis.grid(color='gray',linestyle='dashed')
	plt.xticks(rotation=90)
	plt.title('Speed '+loc+'\n'+str(max(t).time()))
	img=io.BytesIO()
	plt.savefig(img,dpi=150)
	img.seek(0)
	ret.append(img)
	plt.close()
	mov=[float(data[y]['Vehicles']) for y in data]
	#t=[x for x in data]
	mov=[0 if x>127 else x for x in mov]
	plt.plot(t,mov,linestyle='None',marker='o')
	myFmt=mdates.DateFormatter('%H:%M')
	plt.gca().xaxis.set_major_formatter(myFmt)
	#plt.xticks(range(len(t)),[str(tt.time()) for tt in sorted(t)],rotation='vertical')
	plt.title('Cars '+loc+'\n'+str(max(t).time()))
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
