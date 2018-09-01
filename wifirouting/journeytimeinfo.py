import requests
import os
import xml.etree.cElementTree as ET
import config
print config.__file__
import pickle
import geometry
import re

class cache:
	def __init__(self):
		try:
			with open('cache.p', 'r') as pfile:
				self.c = pickle.load(pfile)
		except:
			self.c = {}

	def datagrab(self, url):
		par = {'ApiKey': os.environ['ALKEY']}
		try:
			n = requests.get(url, params=par, timeout=1)
		except:
			return self.c[url].content
		self.c[url] = n
		with open('cache.p', 'w') as pfile:
			pickle.dump(self.c, pfile)
		return n.content

def getwifidata():
	f = cache()
	root = ET.fromstring(f.datagrab('http://bcc.opendata.onl/UTMC Flow.xml'))
	locs = {}
	for flow in root.findall('Flow'):
		try:
			a = flow.find('SCN').text
			b = float(flow.find('Northing').text)
			c = float(flow.find('Easting').text)
			for val in flow.findall('Value'):
				d = int(val.find('Level').text)
		except AttributeError:
			continue
		b, c = geometry.OSGB36toWGS84(c, b)
		locs[a] = ((b, c), d)
	root = ET.fromstring(f.datagrab('http://bcc.opendata.onl/UTMC ANPR.xml'))
	ret = {}
	for flow in root.findall('ANPR'):
		try:
			a = flow.find('Description').text
			b = flow.find('SCN').text
			c = flow.find('Plates').attrib['matched']
			d = flow.find('Time').text
			#print b
		except AttributeError:
			continue
		tmp = []
		for t in a.split(' '):
			n = re.findall(r'E\d\d\d\d', t)
			if n:
				tmp.append(n[0][1:])
		if tmp:
			try:
				ret[b] = {
					'coordinates': [locs[tmp[0]][0], locs[tmp[1]][0]],
					'Time': d,
					'Description': a,
					'matched': c
				}
			except KeyError:
				print tmp[0], tmp[1]
	return ret
getwifidata()()
