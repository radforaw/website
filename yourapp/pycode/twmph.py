import requests
import json
import math
import folium
from bs4 import BeautifulSoup
import base64


def encoder(obj):
        x=json.dumps(obj)
        return base64.urlsafe_b64encode(x)

def decoder(text):
        x=base64.urlsafe_b64decode(text)
        return json.loads(x)


class twentymphquery():
        def __init__(self,road):
                self.road=road
                if self.road=='':
                        self.error('no road name')
                self.rawnominatumdata=self.nomin()
                if not self.rawnominatumdata:
                        self.error('no roads found matching that name')
                self.candidates=self.process()
                if self.candidates==[]:
                        self.error('no candidates')
                for n in self.candidates:
                        print encoder(n)
                        print decoder(encoder(n))
                #process first candidate
                self.current=0
                self.overpassquery=self.overpass(self.current)
                if not self.overpassquery:
                        self.error('something went wrong with overpass')
                self.result=self.overprocess(),self.candidates[self.current]['points'],self.candidates[self.current]['name']
                
        def error(self,text):
                pass
                
                
        def nomin(self):
                url='https://nominatim.openstreetmap.org/search'
                payload={'q':str(self.road+', birmingham').replace(' ',' '),'format':'json','polygon':'1','addresssdetails':'1'}
                try:
                        n=requests.get(url,params=payload).json()
                except:
                        return False
                return n
        
        def process(self):
                ret=[]
                for result in self.rawnominatumdata:
                        if u'osm_type' in result:
                                if result[u'osm_type']==u'way' and result[u'class']==u'highway':
                                        pg=[]
                                        for pts in result[u'polygonpoints']:
                                                pg.append([float(pts[1]),float(pts[0])])
                                        ret.append({'points':pg,'name':result[u'display_name'],'way':int(result[u'osm_id'])})
                return ret
                
        def overpass(self,n):
                url='http://overpass-api.de/api/interpreter'
                payload={'data':'[out:json][timeout:5];way('+str(n)+');out;'}
                try:
                        n=requests.get(url,params=payload,timeout=5).content
                        return json.loads(n)
                except:
                        return False
        
        def overprocess(self):
                res=False
                try:
                        if 'maxspeed' in self.overpassquery['elements'][self.current]['tags']:
                                if self.overpassquery['elements'][self.current]['tags']['maxspeed']=='20 mph':
                                        res=True
                except:
                        return False
                return res



def ismyroad(road):
        if road=='':
                return False # no road name
        x=nomin(road)
        if x:
                y=process(x)
        else:
                return False # nothing from nominatum
        if y==[]:
                return False
        else:
                z=overpass(y[0]['way'])
                for j in y:
                        print j
        if z:
                return overprocess(z),y[0]['points'],y[0]['name']
        else:
                return False








def createmap(n):
        isittwenty=n[0]
        points=n[1]
        text=n[2].split(", ")
        centre=[(points[0][0]+points[-1][0])/2,(points[0][1]+points[-1][1])/2]
        dist=haversine(points[0][0],points[-1][0],points[0][1],points[-1][1])
        print centre,dist
        
        map=folium.Map(width=500,height=500,location=centre,zoom_start=16)
        col="red"
        if isittwenty:
                col="green"
        folium.PolyLine(points,color=col).add_to(map)
        html=map.get_root().render()
        soup=BeautifulSoup(html,'html.parser')
        newtag=soup.new_tag("b")
        soup.body.insert(0,newtag)
        newtag.string="Is My Road 20 MPH?"
        
        br=[]
        j=0
        for n in text[:3]:
                soup.body.append(n)
                br.append(soup.new_tag('br'))
                soup.body.append(br[j])
                j+=1
        with open("del.html","w") as f:
                f.write(str(soup))
        
        
def haversine(lat1,lat2,lon1,lon2):
        R=6371000
        a1=math.radians(lat1)
        a2=math.radians(lat2)
        ca=math.radians(lat2-lat1)
        ct=math.radians(lat2-lat1)
        a=math.sin(ca/2)*math.sin(ca/2)+math.cos(a1)*math.cos(a2)*math.sin(ct/2)*math.sin(ct/2)
        c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))
        return R*c
        
if __name__=="__main__":
        a=twentymphquery('alcester road').result
        print a
        createmap(a)
