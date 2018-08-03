import requests
import json
import math

def ismyroad(road):
        if road=='':
                return False
        x=nomin(road)
        if x:
                y=process(x)
        else:
                return False
        if y==[]:
                return False
        else:
                z=overpass(y[0]['way'])
        if z:
                print y[0]['name']
                return overprocess(z),y[0]['points']
        else:
                return False

def nomin(a='townsend way'):
        url='https://nominatim.openstreetmap.org/search'
        payload={'q':str(a+', birmingham').replace(' ',' '),'format':'json','polygon':'1','addresssdetails':'1'}
        try:
                n=requests.get(url,params=payload).json()
        except:
                return False
        return n

def process(n):
        ret=[]
        for result in n:
                if u'osm_type' in result:
                        if result[u'osm_type']==u'way' and result[u'class']==u'highway':
                                pg=[]
                                for pts in result[u'polygonpoints']:
                                        pg.append([float(pts[0]),float(pts[1])])
                                ret.append({'points':pg,'name':result[u'display_name'],'way':int(result[u'osm_id'])})
        return ret

def overpass(n):
        url='http://overpass-api.de/api/interpreter'
        payload={'data':'[out:json][timeout:5];way('+str(n)+');out;'}
        #print payload
        try:
                n=requests.get(url,params=payload,timeout=5).content
                #print n
                #with open('t20of.p','w') as jsonfile:
                #json.dump(json.loads(n),jsonfile)
                return json.loads(n)
        except:
                return False
                
def overprocess(n):
        res=False
        try:
                if 'maxspeed' in n['elements'][0]['tags']:
                        if n['elements'][0]['tags']['maxspeed']=='20 mph':
                                res=True
        except:
                return False
        return res

if __name__=="__main__":
        print ismyroad('alcester road')

