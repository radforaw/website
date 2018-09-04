#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  bristol.py
#  
#  Copyright 2018  <pi@raspberrypi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import requests
import datetime
import pprint
try:
	from lxml import etree as ET
except ImportError:
	import xml.etree.cElementTree as ET
key={"apikey":"QAPLPKaFokiEkmpv7oFDSw"}
surl="https://highways-bristol.api.urbanthings.io/api/1.0/dynamic/vms/status"
durl="https://highways-bristol.api.urbanthings.io/api/1.0/dynamic/vms/definition"
surl="https://highways-bristol.api.urbanthings.io/api/1.0/dynamic/traveltime/status"
durl="https://highways-bristol.api.urbanthings.io/api/1.0/dynamic/traveltime/definition"
ns="{http://datex2.eu/schema/2/2_0}"

#'WiFiL8': {'matched': '4', 'Description': 'Tyburn Rd WB E4421 to E4439', 'coordinates': [(52.513136240808485, -1.8279231846372113), (52.51100479248898, -1.8336337387460437)], 'Time': '50'}}


def anpr():
	ret={}
	n=requests.get(durl,params=key)
	#pprint.pprint(n.content)
	root=ET.fromstring(n.content)
	for a in root.iter(ns+'measurementSiteRecord'):
		tmp= a.attrib['id']
		for b in a.iter(ns+'measurementSiteName'):
			ret[tmp]={'Description':b.find(ns+'values').find(ns+'value').text}
		j=[float(c.text) for c in a.iter(ns+'latitude')]
		k=[float(c.text) for c in a.iter(ns+'longitude')]
		ret[tmp]['coordinates']=[(j[0],k[0]),(j[-1],k[-1])]
	n=requests.get(surl,params=key)
	#pprint.pprint(n.content)
	root=ET.fromstring(n.content)
	for a in root.iter(ns+'siteMeasurements'):
		tmp=a.find(ns+'measurementSiteReference').attrib['id']
		ret[tmp]['timestamp']=datetime.datetime.strptime(a.find(ns+'measurementTimeDefault').text[:-5],'%Y-%m-%dT%H:%M:%S')
		for b in a.iter(ns+'travelTime'):
			ret[tmp]['Time']=b.find(ns+'duration').text
		for b in a.iter(ns+'normallyExpectedTravelTime'):
			ret[tmp]['expected']= b.find(ns+'duration').text
		ret[tmp]['matched']='0'
	return ret


def main():
	defs={}
	n=requests.get(durl,params=key)
	root=ET.fromstring(n.content)
	for a in root.iter(ns+"vmsUnitRecord"):
		t=a.attrib['id']
		for b in a.iter(ns+"latitude"):
			tlat=float(b.text)
		for b in a.iter(ns+"longitude"):
			tlon=float(b.text)
		defs[t]=[[tlat,tlon]]
	n=requests.get(surl,params=key)
	root=ET.fromstring(n.content)
	for a in root.iter(ns+"vmsUnit"):
		p=a.find(ns+'vmsUnitReference')
		tmp=""
		for b in a.iter(ns+'vmsText'):
			for c in b.findall(ns+'vmsTextLine'):
				for d in c.findall(ns+'vmsTextLine'):
					for e in d.findall(ns+'vmsTextLine'):
						if e.text:
							tmp+=e.text+"|"
		defs[p.attrib['id']].append(tmp)
	for n in defs:
		if len(defs[n])<>2:
			defs[n].append("")
	print defs
	return [['Null',defs[h][1],defs[h][0],h] for h in defs]

if __name__ == '__main__':
	#print main()
	anpr()
