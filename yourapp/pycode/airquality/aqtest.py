#!python3
'''
The data is in our hub as private data, so it isnt searchable, if it was public then someone can browse a catalogue and see it is there.
https://datahub.rp.bt.com/reading-feeds/

The unique device ID for the devices in Birmingham are 806-10
<member>852e810d-4acc-44b6-a999-9361cc3fdc16</member>
<member>4053cc29-d543-4327-8d26-bbc53d5ca692</member>
<member>9eba7196-cc8c-44f4-b19f-8670b3d0bf90</member>
<member>06f0b7f5-0df1-423d-bedb-4032c01241e0</member>
<member>8678b712-ae4f-4cac-aaeb-72f7f22c9685</member>

Ive made a token for you
10c70947-5427-4042-b17c-92f296e54643

so you could curl it in by
curl -u 10c70947-5427-4042-b17c-92f296e54643: https://api.rp.bt.com/sensors/feeds/852e810d-4acc-44b6-a999-9361cc3fdc16/datastreams/0/datapoints?limit=6
or copy / paste this into a web browser
https://10c70947-5427-4042-b17c-92f296e54643:@api.rp.bt.com/sensors/feeds/852e810d-4acc-44b6-a999-9361cc3fdc16/datastreams/0/datapoints?limit=6

that will give you the last 6 readings of NO2 in PPB from 806 as XML, but you can get it as CSV, JSON as well
Ill update your dashboard to have a map on it shortly.
nb 806 is on digbeth and Mill lane

datastream 0 is NO2 in PPB,
datastream 1 is NO in PPB
datastream 2 is CO in PPM
the other streams are temperature, humidity, voltage etc. the noise sensor was removed to fit the device into the inlink.

For traffic lights, you may want to look at the NO readings in stream 1

>Can they also do other things? Pedestrian counting via w
'''

import requests
import folium
try:
	from lxml import etree as ET
except ImportError:
	import xml.etree.cElementTree as ET



feeds=('852e810d-4acc-44b6-a999-9361cc3fdc16',
	'4053cc29-d543-4327-8d26-bbc53d5ca692',
	'9eba7196-cc8c-44f4-b19f-8670b3d0bf90',
	'06f0b7f5-0df1-423d-bedb-4032c01241e0',
	'8678b712-ae4f-4cac-aaeb-72f7f22c9685')

u='10c70947-5427-4042-b17c-92f296e54643'
p=''
url='https://api.rp.bt.com/sensors/feeds/'
#'/datastreams/2/datapoints?limit=6'
url='https://api.rp.bt.com/sensors/collections/7b413bc1-ff76-4bda-83b0-a41932794806/snapshot'

n=requests.get(url,auth=(u,p))
print(n.content)


'''
res=[]
for feed in feeds:
	n=requests.get(url+feed,auth=(u,p))
	print ('********')
	print (n.content)
	root = ET.fromstring(n.content)
	for x in root.findall('location'):
		loc=[float(x.find('lat').text),float(x.find('lon').text)]
		print (loc)
		res.append(loc)




m = folium.Map(location=loc,zoom_start=14)
for loc in res:
	folium.Marker(loc).add_to(m)
m.save('site.html')

import ui,os
from urllib.parse import urljoin
file_path = 'site.html'
file_path = os.path.abspath(file_path)
print (file_path)
w = ui.WebView()
w.load_url(file_path)
w.present()
'''
