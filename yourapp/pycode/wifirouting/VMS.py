import requests
try:
	from lxml import etree as ET
except ImportError:
	import xml.etree.cElementTree as ET
import datetime
import time
import os
import andyconfig
import geometry as g
import folium
import branca

def get_vms():
	url='http://bcc.opendata.onl/UTMC VMS.xml'
	n=requests.get(url,params={'ApiKey':os.environ['ALKEY']})
	root=ET.fromstring(n.content)
	ret=[]
	#print root('VMS_State')
	for VMS in root.iterfind('VMS'):
		tmp=datetime.datetime.strptime(VMS.find("Date").text,'%Y-%m-%d %H:%M:%S')
		now=datetime.datetime.now()-datetime.timedelta(days=28)
		if tmp>now and len(VMS.find('SCN').text)<20 and VMS.find('Message').text:
			ret.append([VMS.find('Description').text,VMS.find('Message').text,(float(VMS.find('Northing').text),(float(VMS.find('Easting').text))),VMS.find('SCN').text])
	return ret

def main():
	m=folium.Map(location=(52.49087856718512, -1.8801756029242436))
	
	for b in get_vms():
		if b[3][:2]=='BI' or b[3][:2]=='M0':
			print b[0]
			print g.OSGB36toWGS84(b[2][1],b[2][0])
			print b[1].replace('|','\n')
			print b[3]
			print
			pop="<HTML><BODY><B>"+b[3]+"<IMG SRC=\'http://54.164.31.65/board.png?text="+b[1]+"\'></BODY></HTML>"
			print pop
			iframe=branca.element.IFrame(html=pop,width=700,height=400)
			po=folium.Popup(iframe,max_width=700)
			folium.Marker(g.OSGB36toWGS84(b[2][1],b[2][0]),popup=po).add_to(m)
	return m.get_root().render()
	

if __name__=="__main__":
	import sys,os, StringIO
	if sys.platform=='ios':
		import ui
		#file_path=StringIO.StringIO(main())
		#file_path = 'map.html'
		#file_path = os.path.abspath(file_path)
		w = ui.WebView()
		#w.load_url(file_path)
		w.load_html(main())
		w.present()
	else:	
		print main()
	

