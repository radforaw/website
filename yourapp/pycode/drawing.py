import folium

class mapimg():
	def __init__(self):
		self.m=folium.Map()
		self.m.zoom_start=12
		self.locs=[]
		
	def point(self,loc,data):
		folium.Marker(loc,popup=data).add_to(self.m)
		self.m.location= folium.utilities._validate_location(loc)
		self.locs.append(self.m.location)
	
	def mapdata(self):
		return self.m.get_root().render()
		
x=mapimg()
x.point((52,-1.9),'hello')
import sys
if sys.platform=='ios':
	import ui
	w = ui.WebView()
	w.load_html(x.mapdata())
	w.present()
